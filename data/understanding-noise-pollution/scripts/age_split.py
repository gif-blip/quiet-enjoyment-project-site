# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
# Census inputs: download the public 2020 bulk files for Colorado and unzip into
#   ./census/co_pl  <- https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/Colorado/co2020.pl.zip
#   ./census/co_dhc <- https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/Colorado/co2020.dhc.zip
# The county totals printed below (330,758 residents; 12,094 university group
# quarters) verify a correct download.
# Age structure of the walkshed household population, from the 2020 DHC bulk
# file. Finds table P12 (sex by age, 49 cells) empirically by structural
# fingerprint on the Boulder County row (total=330,758; total=male+female;
# male bins sum to male total), then extracts per-block age bins, subtracts
# group quarters (from the PL pull, matched by GEOCODE), aggregates in-walkshed.
import json, re, zipfile

CENSUS = "./census"
DATA = "."  # package root
COUNTY_POP = 330758

# --- geo file: LOGRECNO -> GEOCODE for county row + Boulder County blocks ---
county_logrec = None
blocks = {}          # LOGRECNO -> (geocode, lon, lat)
with open(f"{CENSUS}/co_dhc/cogeo2020.dhc", encoding="latin-1") as f:
    for line in f:
        p = line.rstrip("\n").split("|")
        sumlev, logrec, geocode = p[2], p[7], p[9]
        if sumlev == "050" and geocode.endswith("08013") or (sumlev == "050" and "08013" in geocode[:9]):
            if p[4] == "00":  # GEOCOMP total
                county_logrec = logrec
        elif sumlev == "100" and geocode.startswith("08013"):  # DHC blocks are SUMLEV 100
            lat = lon = None
            for tok in p[-10:]:
                try: v = float(tok)
                except ValueError: continue
                if tok.startswith("+") and 36 <= v <= 42: lat = v
                elif tok.startswith("-") and -110 <= v <= -101: lon = v
            if lat and lon:
                blocks[logrec] = (geocode, lon, lat)
print(f"county LOGRECNO: {county_logrec}; blocks: {len(blocks)}")

# --- find P12: scan segments for county row, test 49-cell windows ---
def county_row(seg):
    with open(f"{CENSUS}/co_dhc/co{seg:05d}2020.dhc", encoding="latin-1") as f:
        for line in f:
            p = line.rstrip("\n").split("|")
            if p[4] == county_logrec:
                return p
    return None

hit = None
for seg in range(1, 45):
    row = county_row(seg)
    if not row: continue
    vals = []
    for x in row[5:]:
        try: vals.append(int(x))
        except ValueError: vals.append(None)
    for off in range(len(vals) - 48):
        w = vals[off:off+49]
        if None in w: continue
        if (w[0] == COUNTY_POP and w[0] == w[1] + w[25]
                and w[1] == sum(w[2:25]) and w[25] == sum(w[26:49])):
            hit = (seg, off)
            print(f"P12 found: segment {seg}, data-offset {off}")
            print(f"  county: total {w[0]:,} male {w[1]:,} female {w[25]:,}")
            break
    if hit: break
assert hit, "P12 not found"
seg, off = hit

# --- per-block age bins ---
# window indices (0-based within the 49): male u5..15-17 = 2..5; 18-19,20,21,22-24 = 6..9
# female offsets +24: u5..15-17 = 26..29; 18-24 = 30..33
def bins(w):
    u18   = sum(w[2:6])  + sum(w[26:30])
    a1824 = sum(w[6:10]) + sum(w[30:34])
    a25p  = w[0] - u18 - a1824
    return u18, a1824, a25p

age = {}   # geocode -> (total, u18, 18-24, 25+)
with open(f"{CENSUS}/co_dhc/co{seg:05d}2020.dhc", encoding="latin-1") as f:
    for line in f:
        p = line.rstrip("\n").split("|")
        if p[4] in blocks:
            w = [int(x) for x in p[5+off:5+off+49]]
            geocode = blocks[p[4]][0]
            age[geocode] = (w[0], *bins(w))
print(f"blocks with age data: {len(age)}")
cty_tot = sum(v[0] for v in age.values())
print(f"county check: {cty_tot:,} (expect {COUNTY_POP:,})")

# --- GQ per block from the PL pull (GEOCODE-keyed) ---
plgeo, plpop = {}, {}
with open(f"{CENSUS}/co_pl/cogeo2020.pl", encoding="latin-1") as f:
    for line in f:
        p = line.rstrip("\n").split("|")
        if p[2] == "750" and p[9].startswith("08013"):
            plgeo[p[7]] = p[9]
gq = {}
with open(f"{CENSUS}/co_pl/co000032020.pl", encoding="latin-1") as f:
    for line in f:
        p = line.split("|")
        if p[4] in plgeo:
            gq[plgeo[p[4]]] = (int(p[5]), int(p[12]))  # (GQ total, university)

# --- walkshed aggregate ---
kmz = zipfile.ZipFile("./data/cu_walkshed_15min.kmz")
kml = kmz.read([n for n in kmz.namelist() if n.endswith(".kml")][0]).decode()
rings = []
for cb in re.findall(r"<coordinates>(.*?)</coordinates>", kml, re.S):
    pts = [(float(q.split(",")[0]), float(q.split(",")[1])) for q in cb.split() if len(q.split(",")) >= 2]
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

T = dict(tot=0, u18=0, a1824=0, a25p=0, gq_all=0, gq_uni=0)
for logrec, (geocode, lon, lat) in blocks.items():
    if geocode not in age or age[geocode][0] == 0: continue
    if not pip(lon, lat, walk): continue
    t, u, a, o = age[geocode]
    ga, gu = gq.get(geocode, (0, 0))
    T["tot"] += t; T["u18"] += u; T["a1824"] += a; T["a25p"] += o
    T["gq_all"] += ga; T["gq_uni"] += gu

hh = T["tot"] - T["gq_all"]
hh_1824 = T["a1824"] - T["gq_uni"]          # dorm residents assumed 18-24
hh_25p  = T["a25p"] - (T["gq_all"] - T["gq_uni"])  # other GQ assumed 25+
perm = T["u18"] + hh_25p
print(f"""
=== 15-minute walkshed, 2020 census ===
total residents:                 {T['tot']:,}
  university GQ (dorms):         {T['gq_uni']:,}
  other GQ:                      {T['gq_all']-T['gq_uni']:,}
household population:            {hh:,}
  under 18:                      {T['u18']:,}
  18-24 (household, ex-dorm):    {hh_1824:,}
  25+   (household, ex-otherGQ): {hh_25p:,}
PERMANENT-RESIDENT PROXY (children + household 25+): {perm:,}
  = {100*perm/108250:.1f}% of city pop; student-age household renters {hh_1824:,} ({100*hh_1824/hh:.1f}% of household pop)
""")
json.dump({"walkshed": T, "household": hh, "hh_18_24_exdorm": hh_1824,
           "hh_25plus": hh_25p, "under18": T["u18"], "permanent_proxy": perm,
           "definition": "permanent = under-18 + household 25+; every household 18-24 counted as student (conservative); dorm GQ assumed 18-24, other GQ assumed 25+",
           "source": "2020 DHC P12 blocks + 2020 PL P5 GQ, centroid-in-walkshed"},
          open("./data/walkshed_age_split_2026-08-31.json", "w"), indent=1)
print("saved -> ./data/walkshed_age_split_2026-08-31.json")
