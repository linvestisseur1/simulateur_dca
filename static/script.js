let chart;

async function simulate() {
    const ticker = document.getElementById("ticker").value;
    const montant = document.getElementById("montant").value;
    const start = document.getElementById("start").value;

    const url = `/dca?ticker=${ticker}&montant=${montant}&start=${start}`;
    const r = await fetch(url);
    const data = await r.json();

    const hist = data.historique;

    const dates = hist.map(x => x.date);
    const invest = hist.map(x => x.investi_total);
    const valeur = hist.map(x => x.valeur_total);

    const gainBox = document.getElementById("gainBox");

    if (data.gain >= 0) {
        gainBox.className = "gainBox green";
    } else {
        gainBox.className = "gainBox red";
    }

    gainBox.textContent = 
        `Gain : ${data.gain.toFixed(2)} € (Investi : ${data.investi_total} € – Valeur finale : ${data.valeur_finale.toFixed(2)} €)`;

    if (chart) chart.destroy();

    const ctx = document.getElementById("dcaChart");

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: dates,
            datasets: [
                {
                    label: "Valeur du portefeuille (€)",
                    data: valeur,
                    borderWidth: 3
                },
                {
                    label: "Somme investie (€)",
                    data: invest,
                    borderWidth: 3
                }
            ]
        },
        options: {
            scales: {
                y: { beginAtZero: false }
            }
        }
    });

}
