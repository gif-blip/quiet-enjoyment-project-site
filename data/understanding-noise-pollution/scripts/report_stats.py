# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# Final stats + two charts for the intro report.
# 1) overall inside-walkshed share (excl. outlier) and per-permanent-resident ratio
# 2) chart: calls/night by academic period, inside vs outside
# 3) chart: monthly complaints inside the walkshed, with break shading
import json, datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = "."  # package root
ASSETS = "./figures"
import os; os.makedirs(ASSETS, exist_ok=True)

INK = "#1C2B39"; BRASS = "#A98643"; LIGHT = "#8FA3B3"
fp = json.load(open("./data/term_break_fingerprint_2026-08-31.json"))
pop = json.load(open("./data/walkshed_age_split_2026-08-31.json"))

# ---- overall inside share + ratios ----
tot_in = sum(v["inside"] for v in fp["monthly"].values())
tot_out = sum(v["outside"] for v in fp["monthly"].values())
share = tot_in / (tot_in + tot_out)
print(f"overall (Jan 2023-Aug 2026, excl outlier): inside {tot_in:,} outside {tot_out:,} -> {100*share:.1f}% inside")

months = 43.5  # Jan 2023 - mid Aug 2026
perm_in = pop["permanent_proxy"]  # 28,010 - walkshed permanent-resident proxy (age_split.py)
# Citywide figure from the SAME proxy (under-18 + 25-and-over, DHC block level,
# clipped to citylimits.json in EPSG:2876) - i.e. age_split.py's method applied
# to every city block; 28,010 of the 77,730 fall inside the walkshed.
CITY_PERM_PROXY = 77730
perm_out = CITY_PERM_PROXY - perm_in         # ~49,720 permanent-proxy residents outside
rate_in  = tot_in  / (months/12) / perm_in  * 1000
rate_out = tot_out / (months/12) / perm_out * 1000
print(f"complaints per 1,000 permanent residents/yr (matched proxy both sides): inside {rate_in:.0f}, outside {rate_out:.0f}, ratio {rate_in/rate_out:.1f}x")
# sensitivities, so every ratio ever shown is reproducible and named:
city = 108250; tot_pop_in = 52815
r_in_tot  = tot_in  / (months/12) / tot_pop_in * 1000
r_out_tot = tot_out / (months/12) / (city - tot_pop_in) * 1000
print(f"  sensitivity - total population both sides: inside {r_in_tot:.0f}, outside {r_out_tot:.0f}, ratio {r_in_tot/r_out_tot:.1f}x")
print(f"  deprecated mixed-denominator version (perm inside vs total outside): {rate_in/r_out_tot:.1f}x - superseded, not used in the report")
print(f"per 1,000 total residents inside: {tot_in/(months/12)/tot_pop_in*1000:.0f}")
print(f"permanent share: {100*perm_in/city:.1f}% of city; complaints share {100*share:.1f}%")

# ---- chart 1: calls/night by period ----
per = fp["periods"]
order = ["winter break (deep)", "summer break (deep)", "term (core)", "move-in (Aug 18-31)"]
labels = ["Winter break\n(Dec 22–Jan 8)", "Summer break\n(Jun–Jul)", "School in session\n(term core)", "CU move-in\n(Aug 18–31)"]
inside = [per[k]["in_per_night"] for k in order]
outside = [per[k]["out_per_night"] for k in order]
x = range(len(order)); w = 0.38
fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=200)
b1 = ax.bar([i - w/2 for i in x], inside, w, color=INK, label="Within a 15-minute walk of the university district")
b2 = ax.bar([i + w/2 for i in x], outside, w, color=LIGHT, label="Rest of Boulder")
for b in b1: ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.15, f"{b.get_height():.1f}", ha="center", fontsize=9, color=INK, fontweight="bold")
for b in b2: ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.15, f"{b.get_height():.1f}", ha="center", fontsize=9, color=LIGHT)
ax.set_xticks(list(x)); ax.set_xticklabels(labels, fontsize=9.5)
ax.set_ylabel("Noise complaints per night", fontsize=10)
ax.spines[["top","right"]].set_visible(False)
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_title("When the students leave, the noise leaves", fontsize=13, color=INK, fontweight="bold", loc="left", pad=12)
plt.tight_layout(); plt.savefig(f"{ASSETS}/chart_fingerprint.png"); plt.close()

# ---- chart 2: monthly inside-walkshed complaints ----
mk = sorted(fp["monthly"].keys())[:-1]  # drop partial final month (data ends Aug 14)
vals = [fp["monthly"][k]["inside"] for k in mk]
dates = [datetime.date(int(k[:4]), int(k[5:]), 15) for k in mk]
fig, ax = plt.subplots(figsize=(9.2, 4.2), dpi=200)
ax.plot(dates, vals, color=INK, lw=1.8, marker="o", ms=3)
# shade winter+summer breaks
for y in (2023, 2024, 2025, 2026):
    ax.axvspan(datetime.date(y,6,1), datetime.date(y,7,31), color=BRASS, alpha=0.13, lw=0)
    ax.axvspan(datetime.date(y-1,12,22), datetime.date(y,1,8), color=BRASS, alpha=0.22, lw=0)
ax.set_ylabel("Complaints per month, inside the walkshed", fontsize=9.5)
ax.spines[["top","right"]].set_visible(False)
ax.set_title("The academic calendar, written in noise complaints", fontsize=13, color=INK, fontweight="bold", loc="left", pad=12)
ax.text(0.995, 0.97, "shaded: university breaks", transform=ax.transAxes, ha="right", va="top", fontsize=8.5, color=BRASS)
ax.set_xlim(datetime.date(2023,1,1), datetime.date(2026,8,31))
plt.tight_layout(); plt.savefig(f"{ASSETS}/chart_calendar.png"); plt.close()
print("charts saved ->", ASSETS)
