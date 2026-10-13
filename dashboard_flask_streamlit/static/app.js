const WARNA = {kecil: "#2f9e44", sedang: "#f59f00", besar: "#e03131"};
const f = (x, d = 2) => Number(x).toFixed(d).replace(".", ",");
let distChart;

fetch("/api/data").then(r => r.json()).then(render);

function render({rows, kpi, temuan, keputusan}) {
  renderKpi(kpi);
  renderTabel(rows);
  renderCharts(rows);
  renderDist(rows);
  fill("temuan", temuan);
  fill("keputusan", keputusan);
}

function fill(id, items) {
  document.getElementById(id).innerHTML = items.map(t => `<li>${t}</li>`).join("");
}

function renderKpi(k) {
  const items = [
    ["Jumlah Kelompok", k.jumlah_kelompok, ""],
    ["Rata-rata Keseluruhan", f(k.mean_total), `SD keseluruhan ${f(k.sd_total)}`],
    ["SD Terbesar", f(k.sd_terbesar.nilai), k.sd_terbesar.kelompok],
    ["SD Terkecil", f(k.sd_terkecil.nilai), k.sd_terkecil.kelompok],
  ];
  document.getElementById("kpis").innerHTML = items.map(([l, v, s]) =>
    `<div class="kpi"><div class="label">${l}</div><div class="value">${v}</div><div class="sub">${s}</div></div>`
  ).join("");
}

function renderTabel(rows) {
  const head = ["Kelompok","N","Mean","Median","Modus","Min","Maks","Range","Q1","Q3","SD","Varians","CV (%)","Penyebaran"];
  const body = rows.map(r => `<tr>
    <td>${r.kelompok}</td><td>${r.n}</td><td>${f(r.mean,1)}</td><td>${f(r.median,1)}</td>
    <td>${r.modus}</td><td>${r.min}</td><td>${r.max}</td><td>${r.range}</td>
    <td>${f(r.q1)}</td><td>${f(r.q3)}</td><td>${f(r.sd)}</td><td>${f(r.varians)}</td>
    <td>${f(r.cv,1)}</td><td><span class="badge ${r.kategori_sd}">${r.kategori_sd}</span></td></tr>`).join("");
  document.getElementById("tabel").innerHTML =
    `<thead><tr>${head.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${body}</tbody>`;
}

function renderCharts(rows) {
  const labels = rows.map(r => r.kelompok.replace("Kelompok ", "K"));
  new Chart("chartMean", {
    type: "bar",
    data: {labels, datasets: [{label: "Mean", data: rows.map(r => r.mean), backgroundColor: "#3b5bdb"}]},
    options: {plugins: {legend: {display: false}}, scales: {y: {beginAtZero: true, max: 10}}},
  });
  new Chart("chartSd", {
    type: "bar",
    data: {labels, datasets: [{label: "SD", data: rows.map(r => r.sd),
      backgroundColor: rows.map(r => WARNA[r.kategori_sd])}]},
    options: {plugins: {legend: {display: false}}, scales: {y: {beginAtZero: true}}},
  });
}

function renderDist(rows) {
  const sel = document.getElementById("pilih");
  sel.innerHTML = rows.map((r, i) => `<option value="${i}">${r.kelompok}</option>`).join("");
  sel.onchange = () => draw(rows[sel.value]);
  draw(rows[0]);
}

function draw(r) {
  const counts = Array.from({length: 10}, (_, i) => r.values.filter(v => v === i + 1).length);
  document.getElementById("miniStat").innerHTML =
    [`Mean ${f(r.mean,1)}`, `Median ${f(r.median,1)}`, `Modus ${r.modus}`, `SD ${f(r.sd)}`, `Range ${r.range}`]
      .map(t => `<span>${t}</span>`).join("");
  if (distChart) distChart.destroy();
  distChart = new Chart("chartDist", {
    type: "bar",
    data: {labels: [1,2,3,4,5,6,7,8,9,10], datasets: [{label: "Jumlah orang", data: counts, backgroundColor: WARNA[r.kategori_sd]}]},
    options: {plugins: {legend: {display: false}},
      scales: {x: {title: {display: true, text: "Nilai"}}, y: {beginAtZero: true, ticks: {stepSize: 1}, title: {display: true, text: "Jumlah orang"}}}},
  });
}
