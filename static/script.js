let dcaChart = null;

// ------------------------------------------------------------
// ELEMENTS DU DOM
// ------------------------------------------------------------
const inputSymbol = document.getElementById("symbol-input");
const autoBox = document.getElementById("autocomplete-box");
const startDate = document.getElementById("start-date");
const amountRange = document.getElementById("amount-range");
const amountNumber = document.getElementById("amount-number");
const runBtn = document.getElementById("run-btn");
const errorDiv = document.getElementById("error");

// METRICS UI
const summaryTitle = document.getElementById("summary-title");
const summarySub = document.getElementById("summary-sub");

const metricInvested = document.getElementById("metric-invested");
const metricValue = document.getElementById("metric-value");
const metricGain = document.getElementById("metric-gain");
const metricGainPct = document.getElementById("metric-gain-pct");
const metricPeriods = document.getElementById("metric-periods");
const metricParams = document.getElementById("metric-params");
const metricDates = document.getElementById("metric-dates");
const metricLastPrice = document.getElementById("metric-last-price");

const chartTitle = document.getElementById("chart-title");

// ------------------------------------------------------------
// INIT
// ------------------------------------------------------------
if (!startDate.value) {
  startDate.value = "2000-01-01";
}

// sync montant slider <-> number
amountRange.addEventListener("input", () => {
  amountNumber.value = amountRange.value;
  metricParams.textContent = `Montant mensuel : ${amountRange.value} €`;
});

amountNumber.addEventListener("input", () => {
  const v = Number(amountNumber.value || 0);
  amountRange.value = Math.min(Math.max(v, 10), 10000);
  metricParams.textContent = `Montant mensuel : ${amountNumber.value} €`;
});

// ------------------------------------------------------------
// AUTOCOMPLETE
// ------------------------------------------------------------
let autoTimeout = null;

inputSymbol.addEventListener("input", () => {
  const q = inputSymbol.value.trim();

  if (q.length < 2) {
    autoBox.style.display = "none";
    autoBox.innerHTML = "";
    return;
  }

  clearTimeout(autoTimeout);
  autoTimeout = setTimeout(() => {
    fetch(`/search?query=${encodeURIComponent(q)}`)
      .then((res) => res.json())
      .then((data) => {
        const symbols = data.symbols || [];

        if (symbols.length === 0) {
          autoBox.style.display = "none";
          autoBox.innerHTML = "";
          return;
        }

        autoBox.innerHTML = symbols
          .map(
            (item) => `
          <div class="auto-item"
               data-symbol="${item.symbol}"
               style="
                 padding: 8px 12px;
                 cursor: pointer;
                 border-bottom: 1px solid rgba(255,255,255,0.06);
               ">
            <strong>${item.symbol}</strong> – ${item.name} 
            <span style="color:#9ca3af">(${item.exchange})</span>
          </div>
        `
          )
          .join("");

        autoBox.style.display = "block";

        document.querySelectorAll(".auto-item").forEach((el) => {
          el.addEventListener("click", () => {
            const sym = el.dataset.symbol;
            inputSymbol.value = sym;
            autoBox.style.display = "none";
            autoBox.innerHTML = "";
          });
        });
      })
      .catch(() => {
        autoBox.style.display = "none";
        autoBox.innerHTML = "";
      });
  }, 200);
});

// Fermer la liste si clic hors zone
document.addEventListener("click", (e) => {
  if (!autoBox.contains(e.target) && e.target !== inputSymbol) {
    autoBox.style.display = "none";
  }
});

// ------------------------------------------------------------
// SIMULATION DCA
// ------------------------------------------------------------
async function runSimulation() {
  clearError();

  const symbol = inputSymbol.value.trim().toUpperCase();
  const amount = Number(amountNumber.value || amountRange.value || 100);
  const start = startDate.value;

  if (!symbol) {
    showError("Merci de renseigner un symbole boursier.");
    return;
  }

  // /dca?symbol=...
  const params = new URLSearchParams({
    symbol: symbol,
    amount: String(amount),
  });

  if (start) params.append("start", start);

  let response;
  try {
    response = await fetch(`/dca?${params.toString()}`);
  } catch (e) {
    showError("Impossible d'atteindre l'API.");
    return;
  }

  let data;
  try {
    data = await response.json();
  } catch {
    showError("Format API invalide.");
    return;
  }

  if (!response.ok) {
    showError(data?.detail || "Erreur API.");
    return;
  }

  updateSummary(data, amount, symbol);
  updateChart(data);
}

runBtn.addEventListener("click", runSimulation);

// ------------------------------------------------------------
// UPDATE UI SUMMARY
// ------------------------------------------------------------
function formatEuro(v) {
  if (v === null || v === undefined || isNaN(v)) return "–";
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  }).format(v);
}

function formatPct(v) {
  if (v === null || v === undefined || isNaN(v)) return "–";
  return `${v.toFixed(2)} %`;
}

function showError(msg) {
  errorDiv.style.display = "block";
  errorDiv.textContent = msg;
}

function clearError() {
  errorDiv.style.display = "none";
  errorDiv.textContent = "";
}

function updateSummary(data, amount, symbol) {
  const last = data.data[data.data.length - 1];
  const isGain = data.total_gain >= 0 ? "gain-pos" : "gain-neg";

  summaryTitle.textContent = `DCA sur ${symbol}`;
  summarySub.textContent = `Investissement de ${formatEuro(amount)} par mois.`;

  metricInvested.textContent = formatEuro(data.total_invested);
  metricValue.textContent = formatEuro(data.current_value);

  metricGain.textContent = formatEuro(data.total_gain);
  metricGain.className = `metric-value ${isGain}`;

  const pct = data.total_gain_pct;
  metricGainPct.textContent = pct >= 0 ? `+${formatPct(pct)}` : formatPct(pct);
  metricGainPct.className = `metric-sub ${isGain}`;

  metricPeriods.textContent = `${data.n_periods} versements`;
  metricParams.textContent = `Montant mensuel : ${formatEuro(amount)}`;
  metricDates.textContent = `Période : ${data.start_date} → ${data.end_date}`;
  metricLastPrice.textContent = `Dernier cours : ${formatEuro(last.price)}`;

  chartTitle.textContent = `Courbe DCA – ${symbol}`;
}

// ------------------------------------------------------------
// CHART
// ------------------------------------------------------------
function updateChart(data) {
  const labels = data.data.map((p) => p.date);
  const prices = data.data.map((p) => p.price);
  const values = data.data.map((p) => p.value);

  const isGain = data.total_gain >= 0;

  const ctx = document.getElementById("dca-chart").getContext("2d");

  if (dcaChart) dcaChart.destroy();

  dcaChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Prix de clôture",
          data: prices,
          yAxisID: "y",
          borderColor: "#9ca3af",
          backgroundColor: "rgba(156, 163, 175, 0.18)",
          borderWidth: 2,
          tension: 0.25,
          pointRadius: 0,
        },
        {
          label: "Valeur du portefeuille",
          data: values,
          yAxisID: "y1",
          borderColor: isGain ? "#16a34a" : "#dc2626",
          backgroundColor: isGain
            ? "rgba(22,163,74,0.18)"
            : "rgba(220,38,38,0.18)",
          borderWidth: 3,
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { font: { size: 11 } } },
        tooltip: {
          mode: "index",
          callbacks: {
            label: (ctx) =>
              ctx.datasetIndex === 0
                ? ` Prix : ${formatEuro(ctx.parsed.y)}`
                : ` Valeur : ${formatEuro(ctx.parsed.y)}`,
          },
        },
      },
      scales: {
        x: {
          ticks: { maxTicksLimit: 10, font: { size: 10 } },
          grid: { display: false },
        },
        y: {
          position: "left",
          grid: { color: "rgba(31,41,55,0.6)" },
          ticks: { font: { size: 10 } },
        },
        y1: {
          position: "right",
          grid: { drawOnChartArea: false },
          ticks: { font: { size: 10 } },
        },
      },
    },
  });
}

// ------------------------------------------------------------
// AUTO LAUNCH DEFAULT SIMULATION
// ------------------------------------------------------------
window.addEventListener("load", () => {
  runSimulation();
});
