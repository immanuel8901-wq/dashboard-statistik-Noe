"""Dashboard Statistik Deskriptif - Flask (lokal).
Jalankan:  python app.py   lalu buka http://127.0.0.1:5000
"""
from collections import Counter
from flask import Flask, jsonify, render_template
import numpy as np
import pandas as pd

app = Flask(__name__)
FILE = "data.xlsx"


def load_data():
    # baris 1 = judul, baris 2 kosong, baris 3 = header -> header=2
    df = pd.read_excel(FILE, sheet_name="Data Nilai", header=2)
    df = df.dropna(subset=["Kelompok"]).set_index("Kelompok")
    return df.astype(float)


def mode_info(values):
    """Modus. Kalau semua nilai muncul sekali -> tidak ada modus."""
    c = Counter(values)
    top = max(c.values())
    if top == 1:
        return [], "tidak ada"
    modes = sorted(k for k, v in c.items() if v == top)
    return modes, ", ".join(f"{m:g}" for m in modes)


def kategori_sd(sd):
    if sd < 1:
        return "kecil"
    if sd < 2:
        return "sedang"
    return "besar"


def compute():
    df = load_data()
    rows = []
    for name, r in df.iterrows():
        v = r.values
        mean, sd = float(v.mean()), float(v.std(ddof=1))
        _, mode_txt = mode_info(v.tolist())
        rows.append({
            "kelompok": name,
            "values": v.tolist(),
            "n": int(len(v)),
            "mean": mean,
            "median": float(np.median(v)),
            "modus": mode_txt,
            "min": float(v.min()),
            "max": float(v.max()),
            "range": float(v.max() - v.min()),
            "q1": float(np.percentile(v, 25)),
            "q3": float(np.percentile(v, 75)),
            "sd": sd,
            "varians": float(v.var(ddof=1)),
            "cv": sd / mean * 100,
            "kategori_sd": kategori_sd(sd),
        })
    return rows


def insights(rows):
    allv = np.concatenate([r["values"] for r in rows])
    by_sd = sorted(rows, key=lambda r: r["sd"])
    same_mean = [r["kelompok"] for r in rows if abs(r["mean"] - 5.5) < 1e-9]
    best = max(rows, key=lambda r: r["mean"])
    worst = min(rows, key=lambda r: r["mean"])
    skew = [r for r in rows if r["kelompok"] == "Kelompok 10"][0]
    return {
        "kpi": {
            "jumlah_kelompok": len(rows),
            "mean_total": float(allv.mean()),
            "sd_total": float(allv.std(ddof=1)),
            "sd_terbesar": {"kelompok": by_sd[-1]["kelompok"], "nilai": by_sd[-1]["sd"]},
            "sd_terkecil": {"kelompok": by_sd[0]["kelompok"], "nilai": by_sd[0]["sd"]},
        },
        "temuan": [
            f"{len(same_mean)} kelompok ({same_mean[0]} s.d. {same_mean[-1]}) punya rata-rata sama, 5,5, "
            f"tetapi SD-nya berkisar {min(r['sd'] for r in rows if r['kelompok'] in same_mean):.2f} "
            f"sampai {max(r['sd'] for r in rows if r['kelompok'] in same_mean):.2f}. "
            "Rata-rata saja tidak cukup untuk membedakan kelompok.",
            f"{best['kelompok']} punya rata-rata tertinggi ({best['mean']:.1f}) dengan SD kecil "
            f"({best['sd']:.2f}): tinggi dan merata.",
            f"{worst['kelompok']} punya rata-rata terendah ({worst['mean']:.1f}) dan nilainya "
            "juga cukup seragam: rendah dan merata.",
            f"{by_sd[-1]['kelompok']} paling menyebar (SD {by_sd[-1]['sd']:.2f}): nilainya dari "
            f"{by_sd[-1]['min']:.0f} sampai {by_sd[-1]['max']:.0f} dan tidak ada nilai yang berulang, jadi tidak ada modus.",
            f"{skew['kelompok']}: mean ({skew['mean']:.1f}) lebih rendah dari median ({skew['median']:.1f}) "
            "karena satu nilai ekstrem (1) menarik rata-rata ke bawah. Di sini median lebih mewakili.",
        ],
        "keputusan": [
            "Jangan menilai kelompok hanya dari rata-rata; selalu lihat SD (atau CV) bersama mean.",
            "Kelompok SD besar (4, 5, 6): ada anggota sangat tinggi dan sangat rendah. Pertimbangkan "
            "pendampingan yang berbeda per anggota (tutor sebaya: pasangkan yang tinggi dengan yang rendah).",
            "Kelompok SD kecil dan rata-rata rendah (Kelompok 8): masalahnya menyeluruh, "
            "jadi butuh intervensi untuk seluruh kelompok, bukan individual.",
            "Kelompok SD kecil dan rata-rata tinggi (Kelompok 7): pertahankan, bisa jadi contoh praktik baik.",
            "Kelompok 10: periksa dulu apakah nilai 1 itu outlier karena kesalahan input atau memang kondisi nyata sebelum mengambil keputusan.",
        ],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    rows = compute()
    return jsonify({"rows": rows, **insights(rows)})


if __name__ == "__main__":
    app.run(debug=True)
