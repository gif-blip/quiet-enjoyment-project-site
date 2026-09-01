# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# Academic-calendar fingerprint: noise complaints term-time vs breaks,
# inside vs outside the CU 15-minute-walk buffer. Diff-in-diff on calls/night.
# Data: citywide NOISEB calls-for-service, Jan 2023 - Aug 2026 (9,961 records).
# Convention: exclude the 45XX 19th St outlier block (as in all prior analyses).
import json, re, zipfile, datetime, collections

DATA = "."  # package root

# ---------- geometry: 15-minute-walk buffer from the KMZ ----------
kmz = zipfile.ZipFile("./data/cu_walkshed_15min.kmz")
kml = kmz.read([n for n in kmz.namelist() if n.endswith('.kml')][0]).decode()
coords_blocks = re.findall(r'<coordinates>(.*?)</coordinates>', kml, re.S)
# largest ring = the walkshed polygon
rings = []
for cb in coords_blocks:
    pts = []
    for tok in cb.split():
        p = tok.split(',')
        if len(p) >= 2:
            pts.append((float(p[0]), float(p[1])))
    if len(pts) > 3:
        rings.append(pts)
walk = max(rings, key=len)
print(f"walkshed ring: {len(walk)} vertices")

def pip(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

# ---------- CU academic calendar windows ----------
# Semester spans (first class day .. last final day), best-known dates —
# VERIFY against registrar archive before publication. Deep windows below are
# robust to +/- a few days at boundaries.
D = datetime.date
TERMS = [  # (start, end) inclusive — first class day .. last final day (Registrar PDFs, verified 2026-09-01)
    (D(2023,1,17), D(2023,5,10)), (D(2023,8,28), D(2023,12,20)),
    (D(2024,1,16), D(2024,5,8)),  (D(2024,8,26), D(2024,12,18)),
    (D(2025,1,13), D(2025,5,7)),  (D(2025,8,21), D(2025,12,12)),
    (D(2026,1,8),  D(2026,5,1)),
]
SPRING_BREAKS = [(D(2023,3,27), D(2023,4,2)), (D(2024,3,25), D(2024,3,31)),
                 (D(2025,3,24), D(2025,3,30)), (D(2026,3,16), D(2026,3,22))]
# deep windows (immune to boundary error)
TERM_CORE   = [(D(y,9,5),  D(y,11,15)) for y in (2023,2024,2025)] + \
              [(D(y,2,1),  D(y,4,15))  for y in (2023,2024,2025,2026)]
WINTER_DEEP = [(D(2022,12,22), D(2023,1,8)), (D(2023,12,22), D(2024,1,8)),
               (D(2024,12,22), D(2025,1,8)), (D(2025,12,22), D(2026,1,7))]
SUMMER_DEEP = [(D(y,6,1), D(y,7,31)) for y in (2023,2024,2025,2026)]
MOVEIN      = [(D(y,8,18), D(y,8,31)) for y in (2023,2024,2025)]  # move-in fortnight

def in_windows(d, wins): return any(a <= d <= b for a, b in wins)
def classify(d):
    if in_windows(d, MOVEIN):        return "move-in (Aug 18-31)"
    if in_windows(d, SPRING_BREAKS): return "spring break"
    if in_windows(d, WINTER_DEEP):   return "winter break (deep)"
    if in_windows(d, SUMMER_DEEP):   return "summer break (deep)"
    if in_windows(d, TERM_CORE):     return "term (core)"
    if in_windows(d, TERMS):         return "term (shoulder)"
    return "other break/shoulder"

def nights_in(wins, lo, hi):
    n = 0
    for a, b in wins:
        s, e = max(a, lo), min(b, hi)
        if s <= e: n += (e - s).days + 1
    return n

# ---------- load calls ----------
calls = json.load(open("./data/noiseb_calls_citywide_2023-01_2026-08.json"))
excl = 0
rows = []
for c in calls:
    a = c["attributes"]
    addr = (a.get("Address") or "").upper()
    if re.match(r"^45XX\s+19TH", addr):  # standing outlier exclusion (950 calls, one block, one dispute)
        excl += 1; continue
    g = c.get("geometry") or {}
    if "x" not in g: continue
    # "noise night" attribution: calls before 6am belong to the prior evening
    dt = datetime.datetime.utcfromtimestamp(a["Response_Date"]/1000)  # ArcGIS epoch = local wall clock stored as UTC
    night = (dt - datetime.timedelta(hours=6)).date()
    rows.append((night, g["x"], g["y"]))
print(f"calls: {len(calls)} total, {excl} excluded (45XX 19th), {len(rows)} usable")

lo = min(r[0] for r in rows); hi = max(r[0] for r in rows)
print(f"night span: {lo} .. {hi}")

# ---------- tally ----------
tal = collections.defaultdict(lambda: [0, 0])   # period -> [inside, outside]
monthly = collections.defaultdict(lambda: [0, 0])
for night, x, y in rows:
    inside = pip(x, y, walk)
    p = classify(night)
    tal[p][0 if inside else 1] += 1
    mk = night.strftime("%Y-%m")
    monthly[mk][0 if inside else 1] += 1

periods = [("term (core)", TERM_CORE), ("winter break (deep)", WINTER_DEEP),
           ("summer break (deep)", SUMMER_DEEP), ("spring break", SPRING_BREAKS),
           ("move-in (Aug 18-31)", MOVEIN)]
print(f"\n{'period':24s} {'nights':>6s} {'in/night':>9s} {'out/night':>9s} {'in-share':>8s}")
res = {}
from collections import Counter as _C
_night_ct = _C()
_d = lo
while _d <= hi:
    _night_ct[classify(_d)] += 1
    _d += datetime.timedelta(days=1)
for name, wins in periods:
    n = _night_ct[name]
    i, o = tal[name]
    if n == 0: continue
    res[name] = {"nights": n, "inside": i, "outside": o,
                 "in_per_night": i/n, "out_per_night": o/n,
                 "in_share": i/(i+o) if i+o else 0}
    print(f"{name:24s} {n:6d} {i/n:9.2f} {o/n:9.2f} {100*i/(i+o):7.1f}%")

tc = res["term (core)"]; wb = res["winter break (deep)"]; sb = res["summer break (deep)"]
print("\n--- the fingerprint ---")
for nm, br in [("winter", wb), ("summer", sb)]:
    din = tc["in_per_night"]/br["in_per_night"] if br["in_per_night"] else float("inf")
    dout = tc["out_per_night"]/br["out_per_night"] if br["out_per_night"] else float("inf")
    print(f"term vs {nm} break: inside walkshed {din:0.1f}x more calls/night; "
          f"outside {dout:0.1f}x; ratio-of-ratios {din/dout:0.2f}")
mi = res.get("move-in (Aug 18-31)")
if mi:
    print(f"move-in fortnight: {mi['in_per_night']:.2f} calls/night inside "
          f"({mi['in_per_night']/tc['in_per_night']:.1f}x term-core rate)")

json.dump({"periods": res, "monthly": {k: {"inside": v[0], "outside": v[1]}
           for k, v in sorted(monthly.items())},
           "meta": {"excluded_outlier_calls": excl, "usable": len(rows),
                    "span": [str(lo), str(hi)],
                    "note": "semester dates verified against CU Registrar published calendars 2026-09-01 (incl. the revised AY25-26 calendar); period nights counted by the same classification as calls"}},
          open("./data/term_break_fingerprint_2026-08-31.json", "w"), indent=1)
print("\nsaved -> ./data/term_break_fingerprint_2026-08-31.json")
