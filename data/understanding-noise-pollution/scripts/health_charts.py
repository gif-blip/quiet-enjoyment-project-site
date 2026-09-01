# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# House-style rebuilds of the two health charts for the intro report.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ASSETS = "./figures"
INK = "#1C2B39"; BROWN = "#8a5a2b"; TAN = "#D9BE9C"; MUTE = "#6B6353"; BLUE = "#8FA3B3"

# ---- thresholds ladder ----
fig, ax = plt.subplots(figsize=(9.4, 3.9), dpi=200)
ax.set_xlim(34, 96); ax.set_ylim(-2.6, 2.6); ax.axis("off")
ax.axhline(0, color="#BBBBBB", lw=3, zorder=1)
marks = [
    (40, "WHO night guideline\nsleep protection", 1),
    (45, "EPA indoor sleep level (1974) ·\nColorado night limit,\namplified bass (from 7 p.m.)", -1),
    (50, "Colorado residential\nnight limit", 1),
    (55, "Colorado residential\nday limit", -1),
]
for x, label, side in marks:
    ax.plot(x, 0, "v" if side > 0 else "^", ms=13, color=INK, zorder=3)
    ax.text(x, 0.52*side, f"{x} dB", ha="center",
            va="bottom" if side > 0 else "top", fontsize=12, fontweight="bold", color=INK)
    ax.text(x, 1.05*side, label, ha="center",
            va="bottom" if side > 0 else "top", fontsize=8.2, color=MUTE)
ax.axvspan(70, 90, ymin=0.42, ymax=0.58, color=BROWN, alpha=0.85, zorder=2)
ax.text(80, 0.85, "a loud house party at the property line: typically 70–90 dB",
        ha="center", fontsize=10, color=BROWN, fontweight="bold", style="italic")
ax.text(80, -0.8, "(illustrative — Boulder deploys no noise monitoring,\nso no measured record exists)",
        ha="center", va="top", fontsize=8, color=MUTE, style="italic")
ax.set_title("Every threshold in the law descends from health science — parties clear them all",
             fontsize=13, color=INK, fontweight="bold", loc="left", pad=14)
plt.tight_layout(); plt.savefig(f"{ASSETS}/chart_thresholds.png", facecolor="white"); plt.close()

# ---- school nights ----
import json as _json
_res = _json.load(open("./data/health_exposure_results.json")) if __import__("os").path.exists("./data/health_exposure_results.json") else _json.load(open("/Users/stephanvandermersch/Library/CloudStorage/Dropbox/Claude Code/University Hill Noise/Health Cost of Party Noise/health_exposure_results.json"))
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
vals = [_res["dow_night"].get(d, 0) for d in days]
cols = [BROWN, BROWN, BROWN, BROWN, BLUE, BLUE, BROWN]
fig, ax = plt.subplots(figsize=(8.6, 3.9), dpi=200)
bars = ax.bar(days, vals, color=cols)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+8, str(v), ha="center", fontsize=10, color=INK)
ax.set_ylabel("Nighttime calls (10 p.m.–3 a.m.)", fontsize=9.5)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Thursday is a school night — and runs near weekend volume",
             fontsize=13, color=INK, fontweight="bold", loc="left", pad=12)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=BROWN, label="Sun–Thu nights"),
                   Patch(color=BLUE, label="Weekend")], frameon=False, fontsize=9)
plt.tight_layout(); plt.savefig(f"{ASSETS}/chart_schoolnights.png", facecolor="white"); plt.close()
print("health charts rebuilt")
