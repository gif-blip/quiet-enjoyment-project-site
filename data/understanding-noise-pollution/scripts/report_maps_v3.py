# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# KMZ-style kernel heat maps (600-ft disc stamps, warm ramp) for the report,
# replacing the hexbin pairs. Also: ladder "0" -> "zero", spring-semester trend.
import json, re, zipfile, datetime, math
import numpy as np
from scipy.ndimage import convolve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

DATA = "."  # package root
DATA = "./data"
ASSETS = "./figures"
INK = "#1C2B39"

# ramps sampled from the KMZ overlay look
# alpha-ramped so the street underlay shows through where there is no heat
BROWN = LinearSegmentedColormap.from_list("qepbrown",
    [(1,1,1,0), (0.953,0.890,0.788,0.55), (0.867,0.710,0.494,0.8),
     (0.725,0.478,0.231,0.9), (0.541,0.290,0.114,1), (0.42,0.176,0.055,1)])
GRAY = LinearSegmentedColormap.from_list("qepgray",
    [(1,1,1,0), (0.91,0.91,0.91,0.55), (0.74,0.74,0.74,0.8),
     (0.54,0.54,0.54,0.9), (0.30,0.30,0.30,1), (0.15,0.15,0.15,1)])

# ---------- geometry ----------
kmz = zipfile.ZipFile("./data/cu_walkshed_15min.kmz")
kml = kmz.read([n for n in kmz.namelist() if n.endswith(".kml")][0]).decode()
rings = []
for cb in re.findall(r"<coordinates>(.*?)</coordinates>", kml, re.S):
    pts = [(float(p.split(",")[0]), float(p.split(",")[1])) for p in cb.split() if len(p.split(",")) >= 2]
    if len(pts) > 3: rings.append(pts)
walk = max(rings, key=len)
wx = [p[0] for p in walk]; wy = [p[1] for p in walk]

# ---------- street underlay (OSM arteries incl. campus-bounding streets) ----------
import json as _json
_st = _json.load(open("./data/streets_osm_arterials.json"))
STREETS = []
for _w in _st.get("elements", []):
    if _w.get("type") != "way" or "geometry" not in _w: continue
    hw = _w.get("tags", {}).get("highway", "")
    lw = 0.9 if hw in ("motorway", "trunk") else 0.55
    STREETS.append(( [g["lon"] for g in _w["geometry"]], [g["lat"] for g in _w["geometry"]], lw ))

def pip(x, y, poly):
    inside = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

# ---------- calls (wall-clock epochs) ----------
calls = json.load(open("./data/noiseb_calls_citywide_2023-01_2026-08.json"))
rows = []
for c in calls:
    a = c["attributes"]
    if re.match(r"^45XX\s+19TH", (a.get("Address") or "").upper()): continue
    g = c.get("geometry") or {}
    if "x" not in g: continue
    dt = datetime.datetime.fromtimestamp(a["Response_Date"]/1000, datetime.timezone.utc)
    night = (dt - datetime.timedelta(hours=6)).date()
    rows.append((night, g["x"], g["y"]))

D = datetime.date
TERM_CORE   = [(D(y,9,5),  D(y,11,15)) for y in (2023,2024,2025)] + \
              [(D(y,2,1),  D(y,4,15))  for y in (2023,2024,2025,2026)]
WINTER_DEEP = [(D(2022,12,22), D(2023,1,8)), (D(2023,12,22), D(2024,1,8)),
               (D(2024,12,22), D(2025,1,8)), (D(2025,12,22), D(2026,1,7))]
SPRING_BREAKS = [(D(2023,3,27), D(2023,4,2)), (D(2024,3,25), D(2024,3,31)),
                 (D(2025,3,24), D(2025,3,30)), (D(2026,3,16), D(2026,3,22))]
def inw(d, wins): return any(a <= d <= b for a, b in wins)
def nights(wins, lo, hi):
    n = 0
    for a, b in wins:
        s, e = max(a, lo), min(b, hi)
        if s <= e: n += (e - s).days + 1
    return n
lo = min(r[0] for r in rows); hi = max(r[0] for r in rows)
n_term = nights(TERM_CORE, lo, hi) - nights(SPRING_BREAKS, D(2023,2,1), D(2026,4,15)); n_wint = nights(WINTER_DEEP, lo, hi)

# ---------- rentals ----------
parc = json.load(open("./data/rental_licenses_parcels_2026-08.json"))
parc = parc["features"] if isinstance(parc, dict) else parc
rpts = []
for f in parc:
    rr = (f.get("geometry") or {}).get("rings")
    if not rr: continue
    xs = [p[0] for p in rr[0]]; ys = [p[1] for p in rr[0]]
    rpts.append((sum(xs)/len(xs), sum(ys)/len(ys)))

# ---------- kernel density grid: 600-ft disc stamp ----------
xs = sorted(r[1] for r in rows); ys = sorted(r[2] for r in rows)
x0, x1 = xs[int(.005*len(xs))] - 0.004, xs[int(.995*len(xs))-1] + 0.004
y0, y1 = ys[int(.005*len(ys))] - 0.004, ys[int(.995*len(ys))-1] + 0.004
NX = 560
ASPECT_LL = math.cos(math.radians(40.02))          # deg-lon shrink factor
NY = int(NX * (y1 - y0) / ((x1 - x0) * ASPECT_LL))
FT600_LAT = 600 / 364000.0                          # ~deg lat per 600 ft
ry_px = FT600_LAT / ((y1 - y0) / NY)
rx_px = (FT600_LAT / ASPECT_LL) / ((x1 - x0) / NX)
yy, xx = np.mgrid[-int(ry_px)-1:int(ry_px)+2, -int(rx_px)-1:int(rx_px)+2]
disc = (((xx/rx_px)**2 + (yy/ry_px)**2) <= 1.0).astype(float)

def density(pts):
    H = np.zeros((NY, NX))
    for x, y in pts:
        if not (x0 <= x <= x1 and y0 <= y <= y1): continue
        i = int((y - y0) / (y1 - y0) * (NY - 1))
        j = int((x - x0) / (x1 - x0) * (NX - 1))
        H[i, j] += 1
    return convolve(H, disc, mode="constant")

def draw(ax, dens, cmap, vmax, title, tcolor):
    for sx, sy, slw in STREETS:
        ax.plot(sx, sy, color="#C4C4C4", lw=slw, zorder=1, solid_capstyle="round")
    ax.imshow(np.power(np.clip(dens/vmax, 0, 1), 0.55), origin="lower",
              extent=(x0, x1, y0, y1), cmap=cmap, vmin=0, vmax=1,
              interpolation="bilinear", aspect=1/ASPECT_LL, zorder=2)
    ax.plot(wx, wy, color=INK, lw=1.5, ls=(0, (5, 3)))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.axis("off")
    ax.set_title(title, fontsize=12.5, color=tcolor, fontweight="bold")

# pair 1: all noise | rentals — each scaled to its own 99.5th pct (style parity)
d_noise = density([(r[1], r[2]) for r in rows])
d_rent  = density(rpts)
fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.6), dpi=200)
draw(axes[0], d_noise, BROWN, np.quantile(d_noise[d_noise>0], 0.998), "Noise complaints, 2023–2026", "#6b2d0e")
draw(axes[1], d_rent,  GRAY,  np.quantile(d_rent[d_rent>0], 0.998),  "Licensed rental properties", "#262626")
fig.text(0.5, 0.015, "Identical 600-ft kernel · dashed line: 15-minute walk from the university district (the CU walkshed)",
         ha="center", fontsize=9.5, color=INK)
plt.tight_layout(rect=[0, 0.035, 1, 1])
plt.savefig(f"{ASSETS}/chart_maps_noise_rentals.png", facecolor="white"); plt.close()

# pair 2: per-night, school in session vs WINTER break — shared zero-based scale
term_dates = [r for r in rows if inw(r[0], TERM_CORE) and not inw(r[0], SPRING_BREAKS)]
d_term = density([(r[1], r[2]) for r in term_dates]) / n_term
d_wint = density([(r[1], r[2]) for r in rows if inw(r[0], WINTER_DEEP)]) / n_wint
VMAX = np.quantile(d_term[d_term>0], 0.998)
fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.6), dpi=200)
draw(axes[0], d_term, BROWN, VMAX, "School in session", "#6b2d0e")
draw(axes[1], d_wint, BROWN, VMAX, "Winter break — students gone", "#6b2d0e")
fig.text(0.5, 0.015, "Noise complaints per night, identical zero-based color scale · dashed line: the CU walkshed",
         ha="center", fontsize=9.5, color=INK)
plt.tight_layout(rect=[0, 0.035, 1, 1])
plt.savefig(f"{ASSETS}/chart_maps_term_break.png", facecolor="white"); plt.close()
print("maps rebuilt (KMZ kernel style)")

# ---------- spring semester trend ----------
SPRINGS = {2023: (D(2023,1,17), D(2023,5,11)), 2024: (D(2024,1,16), D(2024,5,9)),
           2025: (D(2025,1,13), D(2025,5,8)),  2026: (D(2026,1,8), D(2026,5,1))}
print("\nspring semesters (walkshed / citywide ex-outlier):")
for y, (a, b) in SPRINGS.items():
    wk = sum(1 for n, x, yy_ in rows if a <= n <= b and pip(x, yy_, walk))
    cw = sum(1 for n, x, yy_ in rows if a <= n <= b)
    print(f"  spring {y}: {wk} / {cw}")
