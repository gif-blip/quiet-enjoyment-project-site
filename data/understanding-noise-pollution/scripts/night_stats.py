# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# Sharper nightly framings for the report: Thu-Sat term rates, 10pm-3am rates,
# worst nights, minutes-between-complaints during peak windows.
import json, re, zipfile, datetime, collections
DATA = "."  # package root

kmz = zipfile.ZipFile("./data/cu_walkshed_15min.kmz")
kml = kmz.read([n for n in kmz.namelist() if n.endswith(".kml")][0]).decode()
rings = []
for cb in re.findall(r"<coordinates>(.*?)</coordinates>", kml, re.S):
    pts = [(float(p.split(",")[0]), float(p.split(",")[1])) for p in cb.split() if len(p.split(",")) >= 2]
    if len(pts) > 3: rings.append(pts)
walk = max(rings, key=len)
def pip(x, y, poly):
    inside = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

D = datetime.date
TERM_CORE = [(D(y,9,5), D(y,11,15)) for y in (2023,2024,2025)] + \
            [(D(y,2,1), D(y,4,15)) for y in (2023,2024,2025,2026)]
def inw(d, wins): return any(a <= d <= b for a, b in wins)

calls = json.load(open("./data/noiseb_calls_citywide_2023-01_2026-08.json"))
by_night = collections.Counter()          # walkshed calls per night
night_window = collections.Counter()      # walkshed 10pm-3am calls per night
for c in calls:
    a = c["attributes"]
    if re.match(r"^45XX\s+19TH", (a.get("Address") or "").upper()): continue
    g = c.get("geometry") or {}
    if "x" not in g or not pip(g["x"], g["y"], walk): continue
    dt = datetime.datetime.fromtimestamp(a["Response_Date"]/1000, datetime.timezone.utc)
    night = (dt - datetime.timedelta(hours=6)).date()
    by_night[night] += 1
    if dt.hour >= 22 or dt.hour < 3:
        night_window[night] += 1

# term-core nights by weekday
lo, hi = min(by_night), max(by_night)
def daterange(a, b):
    d = a
    while d <= b:
        yield d
        d += datetime.timedelta(days=1)
term_nights = [d for a, b in TERM_CORE for d in daterange(a, b)]
thu_sat = [d for d in term_nights if d.weekday() in (3, 4, 5)]   # Thu, Fri, Sat
sun_wed = [d for d in term_nights if d.weekday() not in (3, 4, 5)]
r_thu_sat = sum(by_night.get(d, 0) for d in thu_sat) / len(thu_sat)
r_sun_wed = sum(by_night.get(d, 0) for d in sun_wed) / len(sun_wed)
nw_thu_sat = sum(night_window.get(d, 0) for d in thu_sat) / len(thu_sat)
nw_all_term = sum(night_window.get(d, 0) for d in term_nights) / len(term_nights)
print(f"TERM-CORE walkshed: Thu-Sat {r_thu_sat:.1f}/night (10pm-3am: {nw_thu_sat:.1f} -> one every {300/nw_thu_sat:.0f} min)")
print(f"TERM-CORE walkshed: Sun-Wed {r_sun_wed:.1f}/night")
print(f"TERM-CORE all nights, 10pm-3am only: {nw_all_term:.2f}/night")

# worst nights
worst = by_night.most_common(8)
print("\nworst single nights (walkshed):")
for d, n in worst: print(f"  {d} ({d.strftime('%a')}): {n}")

# September weekends specifically
sep_wknd = [d for d in term_nights if d.month == 9 and d.weekday() in (4, 5)]
print(f"\nSeptember Fri+Sat avg: {sum(by_night.get(d,0) for d in sep_wknd)/len(sep_wknd):.1f}/night")

# window sizes for like-for-like note
print(f"\nterm-core nights in span: {len([d for d in term_nights if lo<=d<=hi])}; per year ~147")
