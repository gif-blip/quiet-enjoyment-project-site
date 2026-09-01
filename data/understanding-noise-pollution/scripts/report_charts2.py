# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# v2 graphics + trend re-run for the intro report.
#  A. map pair 1: noise heat (brown) | licensed rentals (grayscale), CU walkshed ring
#  B. map pair 2: noise per-night, school in session | school breaks (same scale)
#  C. per-parcel bar: complaints per licensed rental, inside ring vs rest (12 mo)
#  D. hourly distribution of complaints
#  E. "what it takes" waffle: 600 calls -> 5 violations -> 0 licenses reviewed
#  F. trend numbers: yearly + school-year totals
import json, re, zipfile, datetime, math, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

DATA = "."  # package root
DATA = "./data"
ASSETS = "./figures"
INK = "#1C2B39"; BRASS = "#A98643"
BROWN = LinearSegmentedColormap.from_list("qepbrown", ["#FFFFFF", "#D9BE9C", "#8a5a2b", "#3d2817"])
GRAY  = LinearSegmentedColormap.from_list("qepgray",  ["#FFFFFF", "#c9c9c9", "#8a8a8a", "#2b2b2b"])

# ---------- geometry ----------
kmz = zipfile.ZipFile("./data/cu_walkshed_15min.kmz")
kml = kmz.read([n for n in kmz.namelist() if n.endswith(".kml")][0]).decode()
rings = []
for cb in re.findall(r"<coordinates>(.*?)</coordinates>", kml, re.S):
    pts = [(float(p.split(",")[0]), float(p.split(",")[1])) for p in cb.split() if len(p.split(",")) >= 2]
    if len(pts) > 3: rings.append(pts)
walk = max(rings, key=len)
wx = [p[0] for p in walk]; wy = [p[1] for p in walk]

def pip(x, y, poly):
    inside = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

# ---------- calls ----------
calls = json.load(open("./data/noiseb_calls_citywide_2023-01_2026-08.json"))
rows = []
for c in calls:
    a = c["attributes"]
    if re.match(r"^45XX\s+19TH", (a.get("Address") or "").upper()): continue
    g = c.get("geometry") or {}
    if "x" not in g: continue
    dt = datetime.datetime.fromtimestamp(a["Response_Date"]/1000, datetime.timezone.utc)  # ArcGIS epoch = local wall clock stored as UTC
    night = (dt - datetime.timedelta(hours=6)).date()
    rows.append((night, g["x"], g["y"], dt.hour))
print(f"usable calls: {len(rows)}")

D = datetime.date
TERM_CORE   = [(D(y,9,5),  D(y,11,15)) for y in (2023,2024,2025)] + \
              [(D(y,2,1),  D(y,4,15))  for y in (2023,2024,2025,2026)]
BREAKS_DEEP = [(D(2022,12,22), D(2023,1,8)), (D(2023,12,22), D(2024,1,8)),
               (D(2024,12,22), D(2025,1,8)), (D(2025,12,22), D(2026,1,8))] + \
              [(D(y,6,1), D(y,7,31)) for y in (2023,2024,2025,2026)]
def inw(d, wins): return any(a <= d <= b for a, b in wins)
def nights(wins, lo, hi):
    n = 0
    for a, b in wins:
        s, e = max(a, lo), min(b, hi)
        if s <= e: n += (e - s).days + 1
    return n
lo = min(r[0] for r in rows); hi = max(r[0] for r in rows)
n_term = nights(TERM_CORE, lo, hi); n_break = nights(BREAKS_DEEP, lo, hi)

# ---------- rentals ----------
parc = json.load(open("./data/rental_licenses_parcels_2026-08.json"))
parc = parc["features"] if isinstance(parc, dict) else parc
rpts = []
for f in parc:
    rr = (f.get("geometry") or {}).get("rings")
    if not rr: continue
    xs = [p[0] for p in rr[0]]; ys = [p[1] for p in rr[0]]
    rpts.append((sum(xs)/len(xs), sum(ys)/len(ys)))
print(f"licensed rental parcels: {len(rpts)}")
r_in  = sum(1 for x, y in rpts if pip(x, y, walk))
r_out = len(rpts) - r_in

rn = json.load(open("./data/rental_noise_calls_trailing12mo.json"))
c_in = c_out = 0
for f in rn:
    a = f["attributes"]
    if re.match(r"^45\d\d\s+19TH", (a.get("address") or "").upper()): continue
    if a.get("lat") is None: continue
    (c_in, c_out)  # noqa
    if pip(a["lng"], a["lat"], walk): c_in += 1
    else: c_out += 1
rate_in = c_in / r_in; rate_out = c_out / r_out
print(f"rentals inside ring: {r_in:,}; outside: {r_out:,}")
print(f"complaints at rentals 12mo: inside {c_in:,}, outside {c_out:,}")
print(f"per-parcel: inside {rate_in:.3f}, outside {rate_out:.3f}, ratio {rate_in/rate_out:.1f}x")

# ---------- extents ----------
xs = sorted(r[1] for r in rows); ys = sorted(r[2] for r in rows)
x0, x1 = xs[int(.005*len(xs))], xs[int(.995*len(xs))-1]
y0, y1 = ys[int(.005*len(ys))], ys[int(.995*len(ys))-1]
pad = 0.004
EXT = (x0-pad, x1+pad, y0-pad, y1+pad)
ASP = 1/math.cos(math.radians(40.02))

def panel(ax, pts, cmap, vmax=None, weightper=None):
    hb = ax.hexbin([p[0] for p in pts], [p[1] for p in pts], gridsize=46,
                   extent=EXT, cmap=cmap, mincnt=1, linewidths=0.1)
    if weightper:
        hb.set_array(hb.get_array()/weightper)
    if vmax: hb.set_clim(0, vmax)
    ax.plot(wx, wy, color=INK, lw=1.4, ls=(0, (5, 3)))
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3])
    ax.set_aspect(ASP); ax.axis("off")
    return hb

# (map pairs now built by report_maps_v3.py — removed here so they are not overwritten)

# C) per-parcel bars
fig, ax = plt.subplots(figsize=(7.4, 3.6), dpi=200)
bars = ax.barh(["Rest of Boulder", "Inside the CU walkshed"], [rate_out, rate_in],
               color=["#8FA3B3", "#8a5a2b"], height=0.55)
for b, v in zip(bars, [rate_out, rate_in]):
    ax.text(v + 0.008, b.get_y()+b.get_height()/2, f"{v:.2f}", va="center",
            fontsize=12, fontweight="bold", color=INK)
ax.set_xlabel("Noise complaints per licensed rental, past 12 months", fontsize=10)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title(f"Same license, {rate_in/rate_out:.1f}x the noise complaints",
             fontsize=13, color=INK, fontweight="bold", loc="left", pad=12)
plt.tight_layout(); plt.savefig(f"{ASSETS}/chart_rental_rate.png"); plt.close()

# D) hourly distribution
hours = collections.Counter(r[3] for r in rows)
order = list(range(12, 24)) + list(range(0, 12))   # noon->noon
vals = [hours.get(h, 0) for h in order]
labels = [f"{(h-1)%12+1}{'p' if h>=12 else 'a'}" for h in order]
fig, ax = plt.subplots(figsize=(9.0, 3.8), dpi=200)
cols = ["#8a5a2b" if (h >= 22 or h < 3) else "#D9BE9C" for h in order]
ax.bar(range(24), vals, color=cols)
ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels([labels[i] for i in range(0, 24, 2)], fontsize=9)
ax.set_ylabel("Complaints", fontsize=9.5)
ax.axvline(order.index(23) - 0.5, color=INK, lw=1, ls=":")
ax.text(order.index(23) - 0.7, max(vals)*0.97, "city quiet hours begin 11pm", rotation=90,
        va="top", ha="right", fontsize=8.5, color=INK)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("The calls come when the city sleeps", fontsize=13, color=INK,
             fontweight="bold", loc="left", pad=12)
night_share = sum(hours.get(h, 0) for h in (22, 23, 0, 1, 2)) / len(rows)
ax.text(0.995, 0.95, f"10pm–3am: {100*night_share:.0f}% of all complaints",
        transform=ax.transAxes, ha="right", va="top", fontsize=10, color="#8a5a2b", fontweight="bold")
plt.tight_layout(); plt.savefig(f"{ASSETS}/chart_hourly.png"); plt.close()

# E) waffle — what it takes to put one license at risk
fig, ax = plt.subplots(figsize=(9.6, 4.4), dpi=200)
ax.axis("off")
COLS, ROWS_ = 40, 15   # 600 dots
for i in range(600):
    r_, c_ = divmod(i, COLS)
    ax.plot(c_*1.0, -r_*1.0, "o", ms=4.4, color="#8a5a2b", alpha=0.85)
ax.text(COLS/2 - 0.5, 2.6, "600 neighbor phone calls", ha="center", fontsize=15,
        fontweight="bold", color=INK)
ax.text(COLS/2 - 0.5, 1.2, "each dot: one late-night call to police, at the university district's enforcement rate",
        ha="center", fontsize=9.5, color=INK)
ax.text(COLS + 3.0, -ROWS_/2 + 0.5, "→", fontsize=26, color=INK, ha="center")
for j in range(5):
    ax.plot(COLS + 6.6, -1.2 - j*1.9, "s", ms=11, color=INK)
ax.text(COLS + 6.6, -12.4, "5 documented\nviolations — the\nchronic-nuisance\nthreshold", ha="center", va="top", fontsize=9.5, color=INK)
ax.text(COLS + 10.8, -ROWS_/2 + 0.5, "→", fontsize=26, color=INK, ha="center")
ax.text(COLS + 16.4, -ROWS_/2 + 0.5, "zero", fontsize=34, fontweight="bold", color="#8a5a2b", ha="center", va="center")
ax.text(COLS + 15.8, -12.4, "chronic-nuisance\ndesignations in the\ncampus districts", ha="center", va="top", fontsize=9.5, color=INK)
ax.set_xlim(-1.5, COLS + 21); ax.set_ylim(-ROWS_ - 4.5, 5)
plt.tight_layout(); plt.savefig(f"{ASSETS}/chart_ladder.png", facecolor="white"); plt.close()

# F) trend numbers
def year_counts(yr, end=None):
    cw = wk = 0
    for night, x, y, hr in rows:
        if night.year != yr: continue
        if end and night > end: continue
        cw += 1
        if pip(x, y, walk): wk += 1
    return cw, wk
print("\n--- TREND (citywide ex-outlier / CU walkshed) ---")
for yr in (2023, 2024, 2025):
    print(yr, year_counts(yr))
print("2025 through Aug 14:", year_counts(2025, D(2025, 8, 14)))
print("2026 through Aug 14:", year_counts(2026, D(2026, 8, 14)))
def span_counts(a, b):
    cw = wk = 0
    for night, x, y, hr in rows:
        if a <= night <= b:
            cw += 1
            if pip(x, y, walk): wk += 1
    return cw, wk
print("school years (Aug 15-May 31), citywide/walkshed:")
for y in (2023, 2024, 2025):
    print(f"  {y}-{y+1}:", span_counts(D(y, 8, 15), D(y+1, 5, 31)))
print("charts saved")
