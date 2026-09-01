# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# Census inputs: download the public 2020 bulk files for Colorado and unzip into
#   ./census/co_pl  <- https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/Colorado/co2020.pl.zip
#   ./census/co_dhc <- https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/Colorado/co2020.dhc.zip
# The county totals printed below (330,758 residents; 12,094 university group
# quarters) verify a correct download.
# Permanent vs student population inside CU walkshed / half-mile buffer,
# from the 2020 PL 94-171 bulk file (keyless). Blocks (SUMLEV 750) in Boulder
# County; join P1 (file 1) + P5 group quarters (file 3) by LOGRECNO; block
# internal-point-in-polygon against both buffers.
import json, re, zipfile

CENSUS = "./census"
DATA = "."  # package root

def load_ring(kmz_path):
    kmz = zipfile.ZipFile(kmz_path)
    kml = kmz.read([n for n in kmz.namelist() if n.endswith(".kml")][0]).decode()
    rings = []
    for cb in re.findall(r"<coordinates>(.*?)</coordinates>", kml, re.S):
        pts = [(float(p.split(",")[0]), float(p.split(",")[1])) for p in cb.split() if len(p.split(",")) >= 2]
        if len(pts) > 3: rings.append(pts)
    return max(rings, key=len)

walk = load_ring("./data/cu_walkshed_15min.kmz")
half = load_ring("./data/cu_halfmile_buffer.kmz")

def pip(x, y, poly):
    inside = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

# --- geo file: blocks in Boulder County, with internal point ---
geo = {}   # LOGRECNO -> (lon, lat)
with open(f"{CENSUS}/co_pl/cogeo2020.pl", encoding="latin-1") as f:
    for line in f:
        p = line.rstrip("\n").split("|")
        if p[2] != "750":  # SUMLEV block
            continue
        geocode = p[9]
        if not geocode.startswith("08013"):
            continue
        logrec = p[7]
        lat = lon = None
        for tok in p[-10:]:  # INTPTLAT/INTPTLON live near the end
            try:
                v = float(tok)
            except ValueError:
                continue
            if tok.startswith("+") and 36 <= v <= 42: lat = v
            elif tok.startswith("-") and -110 <= v <= -101: lon = v
        if lat and lon:
            geo[logrec] = (lon, lat)
print(f"Boulder County blocks located: {len(geo)}")

# --- file 1: P0010001 total pop ---
pop = {}
with open(f"{CENSUS}/co_pl/co000012020.pl", encoding="latin-1") as f:
    for line in f:
        p = line.split("|")
        if p[4] in geo:
            pop[p[4]] = int(p[5])

# --- file 3: P5 group quarters (P0050001 total GQ ... P0050008 university housing) ---
gq = {}
with open(f"{CENSUS}/co_pl/co000032020.pl", encoding="latin-1") as f:
    for line in f:
        p = line.split("|")
        if p[4] in geo:
            gq[p[4]] = (int(p[5]), int(p[12]))  # (GQ total, university student housing)
print(f"pop joined: {len(pop)}, gq joined: {len(gq)}")
print(f"county pop check: {sum(pop.values()):,} (expect ~330,758)")
uni_total = sum(v[1] for v in gq.values())
print(f"county university-GQ check: {uni_total:,}")

# --- aggregate ---
for name, ring in [("15-minute walkshed", walk), ("half-mile buffer", half)]:
    tot = g_all = g_uni = blocks = 0
    for logrec, (lon, lat) in geo.items():
        if pop.get(logrec, 0) == 0: continue
        if pip(lon, lat, ring):
            blocks += 1
            tot += pop[logrec]
            a, u = gq.get(logrec, (0, 0))
            g_all += a; g_uni += u
    hh = tot - g_all
    print(f"\n=== {name} ===")
    print(f"blocks: {blocks}")
    print(f"total residents (2020):            {tot:,}")
    print(f"  university housing (dorm GQ):    {g_uni:,}")
    print(f"  all group quarters:              {g_all:,}")
    print(f"  household population:            {hh:,}")
    print(f"shares of city pop 108,250: total {100*tot/108250:.1f}%, household {100*hh/108250:.1f}%")
    if name.startswith("15"):
        out = {"walkshed_total": tot, "university_gq": g_uni, "all_gq": g_all,
               "household_pop": hh, "blocks": blocks}

json.dump(out, open("./data/walkshed_population_2026-08-31.json", "w"), indent=1)
print("\nsaved -> ./data/walkshed_population_2026-08-31.json")
