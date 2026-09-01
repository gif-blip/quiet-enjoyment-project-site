#!/usr/bin/env python3
# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data (JSON) and ./figures (charts).
"""Health report exposure analysis: night calls, resident-nights, school nights,
per-neighborhood burden, repeat blocks; charts + results JSON.

v1.4 corrections (Sept 2026, after adversarial review):
 - the parcel file contains duplicated ParcelNo rows (23,133 rows, ~20,629 unique
   parcels); parcels are now DEDUPLICATED BY ParcelNo before counting, and the
   resident-night seen-set is keyed on (night, ParcelNo) — this lowers the
   resident-night proxy from 173,441 to ~154,048;
 - the median nearby-homes-per-event figure is now COMPUTED (previously a stale
   hard-coded 58; correct value ~54 on unique parcels);
 - chart annotations (night share, night-call count) are computed, not literals;
 - "school nights" is reported two ways: the Sun-Thu weekday shortcut (labeled as
   such) and a calendar-true version gated on actual BVSD student days.
"""
import json, math, statistics
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime, timezone, date, timedelta
from collections import Counter, defaultdict
from scipy.spatial import cKDTree
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import unary_union, transform as shp_transform
import os

OUTD="./data"; FIGD="./figures"
os.makedirs(FIGD, exist_ok=True)
T_FT=Transformer.from_crs(4326,2876,always_xy=True); T_LL=Transformer.from_crs(2876,4326,always_xy=True)
calls=json.load(open("./data/noise_party_calls_trailing12mo.json"))["features"]
parcels=json.load(open("./data/city_res_parcels.json"))
HH=2.2

# ---- dedupe parcels by ParcelNo (the city file repeats some parcels up to 8x) ----
hxy=[]; hnb=[]; hpid=[]
_seen_pid=set(); n_raw=0; n_nopid=0
for j,r in enumerate(parcels):
    try: la=float(r.get("Latitude") or 0); lo=float(r.get("Longitude") or 0)
    except: continue
    if not la: continue
    n_raw+=1
    pid=(str(r.get("ParcelNo") or "").strip())
    if not pid:
        pid=f"_row{j}"; n_nopid+=1
    if pid in _seen_pid: continue
    _seen_pid.add(pid)
    hxy.append(T_FT.transform(lo,la)); hnb.append((r.get("NbhdDscr") or "?").strip()); hpid.append(pid)
print(f"parcels: {n_raw} usable rows -> {len(hpid)} unique ParcelNo ({n_raw-len(hpid)} duplicate rows dropped; {n_nopid} rows had no ParcelNo)")
hxy=np.array(hxy); ht=cKDTree(hxy)

# ---- BVSD student-day calendar (2025-26 published calendar + 2026-27 start) ----
def _drange(a,b):
    d=a
    while d<=b:
        yield d; d+=timedelta(days=1)
_no_school=set()
for a,b in [(date(2025,9,1),date(2025,9,2)),(date(2025,10,13),date(2025,10,14)),
            (date(2025,11,10),date(2025,11,11)),(date(2025,11,24),date(2025,11,28)),
            (date(2025,12,22),date(2026,1,2)),(date(2026,1,5),date(2026,1,5)),
            (date(2026,1,19),date(2026,1,19)),(date(2026,2,16),date(2026,2,17)),
            (date(2026,3,16),date(2026,3,20))]:
    _no_school.update(_drange(a,b))
def is_student_day(d):
    if d.weekday()>=5: return False
    if date(2025,8,13)<=d<=date(2026,5,21): return d not in _no_school
    if d>=date(2026,8,12): return True     # BVSD 2026-27 first day
    return False

def wall(ts): return datetime.fromtimestamp(ts/1000, tz=timezone.utc)
import re as _re
hour_hist=Counter(); dow_night=Counter(); nb_rn=defaultdict(float)
block_night=Counter(); res_nights=0.0; school_rn_sunthu=0.0; school_rn_bvsd=0.0
night_pts=[]; homes_per_event=[]
n_night=0
_seen=set()   # (night, ParcelNo) pairs — a resident-night counts once per night per parcel
for f in calls:
    a=f["attributes"]; ts=a.get("Response_Date")
    if not ts or not f.get("geometry"): continue
    # standing exclusion: the 4500-block-of-19th single-dispute outlier
    if _re.match(r"^45XX\s+19TH", (a.get("Address") or "").upper().strip()): continue
    dt=wall(ts); h=dt.hour
    hour_hist[h]+=1
    if h>=22 or h<3:
        n_night+=1
        night=(dt-timedelta(hours=6)).date()
        x,y=T_FT.transform(f["geometry"]["x"],f["geometry"]["y"])
        night_pts.append((x,y))
        idx=ht.query_ball_point([x,y],r=600.0)
        homes_per_event.append(len(idx))
        eff=dt.weekday() if h>=22 else (dt.weekday()-1)%7
        sunthu = eff in (6,0,1,2,3)
        bvsd = is_student_day(night+timedelta(days=1))
        for i in idx:
            key=(night,hpid[i])
            if key in _seen: continue
            _seen.add(key)
            res_nights+=HH
            if sunthu: school_rn_sunthu+=HH
            if bvsd: school_rn_bvsd+=HH
            nb_rn[hnb[i]]+=HH
        dow_night[eff]+=1
        block_night[(a.get("Address") or "?").upper().strip()]+=1
tot=sum(hour_hist.values())
night_share=n_night/tot
med_homes=int(statistics.median(homes_per_event)) if homes_per_event else 0
print(f"night calls {n_night}/{tot} ({night_share:.0%}); resident-nights {res_nights:,.0f}; "
      f"Sun-Thu nights {school_rn_sunthu:,.0f} ({school_rn_sunthu/res_nights:.0%}); "
      f"BVSD student-day nights {school_rn_bvsd:,.0f} ({school_rn_bvsd/res_nights:.0%}); "
      f"median unique parcels within 600 ft per night event: {med_homes}",flush=True)

top_nb=sorted(nb_rn.items(),key=lambda kv:-kv[1])[:10]
top_blocks=block_night.most_common(12)
chronic_res=3493*HH

# chart 1: clock histogram
plt.rcParams.update({"font.size":11})
fig,ax=plt.subplots(figsize=(8.6,4.4),dpi=150)
hours=list(range(17,24))+list(range(0,6))
labels=[f"{(h%12) or 12}{'p' if h>=12 else 'a'}" for h in hours]
vals=[hour_hist[h] for h in hours]
cols=["#c9b8e8" if not (h>=22 or h<3) else "#5e3c99" for h in hours]
ax.bar(range(len(hours)),vals,color=cols)
ax.set_xticks(range(len(hours))); ax.set_xticklabels(labels)
ax.axvspan(4.5,12.5,alpha=0.06,color="k")
ax.text(8.5,max(vals)*0.95,f"10 pm – 3 am:\n{night_share:.0%} of all noise calls",ha="center",fontsize=11,weight="bold",color="#5e3c99")
ax.set_ylabel("noise/party calls (12 months)")
ax.set_title("Boulder's noise problem is a sleep problem — calls by hour of night")
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(FIGD+"/chart_clock.png",bbox_inches="tight")

# chart 2: weekday pattern, Sun-Thu highlighted
fig,ax=plt.subplots(figsize=(8.6,4.2),dpi=150)
names=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
sv=[dow_night[d] for d in range(7)]
cols=["#c62828" if d in (6,0,1,2,3) else "#9e9e9e" for d in range(7)]
ax.bar(names,sv,color=cols)
for i,v in enumerate(sv): ax.text(i,v,f"{v}",ha="center",va="bottom",fontsize=10)
ax.set_ylabel("night calls (10 pm – 3 am)")
ax.set_title("Night-time noise events by evening — red = Sunday–Thursday nights")
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(FIGD+"/chart_dow_night_raw.png",bbox_inches="tight")

# chart 3: night-call map
def shoelace(r): return sum(x1*y2-x2*y1 for (x1,y1),(x2,y2) in zip(r,r[1:]+r[:1]))/2
def esri_poly(g):
    rings=[r for r in g.get("rings",[]) if len(r)>=4]
    ps=[Polygon(r).buffer(0) for r in rings if shoelace(r)<0] or [Polygon(r).buffer(0) for r in rings]
    return unary_union(ps)
city=shp_transform(lambda x,y:T_LL.transform(x,y),
    unary_union([esri_poly(f["geometry"]) for f in json.load(open("./data/citylimits.json"))["features"]]))
fig,ax=plt.subplots(figsize=(7.6,8.6),dpi=150)
for g in ([city] if city.geom_type=="Polygon" else city.geoms):
    ax.plot(*g.exterior.xy,color="#333",lw=0.9)
np_ll=[T_LL.transform(x,y) for x,y in night_pts]
ax.scatter([p[0] for p in np_ll],[p[1] for p in np_ll],s=7,alpha=0.28,color="#5e3c99",edgecolors="none")
ax.set_aspect(1/0.766); ax.set_xticks([]); ax.set_yticks([])
ax.set_title(f"{n_night:,} night-time (10 pm – 3 am) noise calls in twelve months\n— each dot within 600 ft of a median of {med_homes} homes (proximity proxy)")
fig.tight_layout(); fig.savefig(FIGD+"/chart_nightmap.png",bbox_inches="tight")

# chart 4: threshold ladder
fig,ax=plt.subplots(figsize=(8.6,3.6),dpi=150)
marks=[(40,"WHO health-based\nnight guideline\n(sleep protection)","#1b7837"),
       (45,"EPA indoor Ldn\n(1974 'Levels' doc)","#5aae61"),
       (50,"Colorado state\nnight limit (from 7 pm)","#e08214"),
       (50.01,"",None),
       (55,"Boulder night limit starts 11 pm;\nWHO interim target —\n'elevated blood pressure,\nheart attacks' above this","#c62828")]
ax.hlines(1,35,80,color="#bbb",lw=3)
for db,lab,c in marks:
    if not lab: continue
    ax.plot([db],[1],marker="v",ms=14,color=c)
    ax.text(db,1.12,f"{int(db)} dB",ha="center",fontsize=11,weight="bold",color=c)
    ax.text(db,0.55,lab,ha="center",fontsize=8.2,color="#333")
ax.text(70,1.25,"a loud house party at the property line:\ntypically 70–90 dB",ha="center",fontsize=9,style="italic",color="#555")
ax.set_xlim(35,92); ax.set_ylim(0.2,1.6); ax.axis("off")
ax.set_title("Every threshold in law descends from health science — and parties blow through all of them")
fig.tight_layout(); fig.savefig(FIGD+"/chart_thresholds_raw.png",bbox_inches="tight")

json.dump(dict(total_calls=tot,night_calls=n_night,night_share=night_share,
               res_nights=res_nights,
               school_rn_sunthu=school_rn_sunthu,school_share_sunthu=school_rn_sunthu/res_nights,
               school_rn_bvsd=school_rn_bvsd,school_share_bvsd=school_rn_bvsd/res_nights,
               hour_hist=dict(hour_hist),
               dow_night={names[d]:dow_night[d] for d in range(7)},
               top_nb=top_nb,top_blocks=top_blocks,chronic_residents=chronic_res,
               median_homes_per_event=med_homes,hh=HH,
               parcel_rows_usable=n_raw,parcel_unique=len(hpid)),
          open(OUTD+"/health_exposure_results.json","w"),indent=1)
print("charts + results written",flush=True)
print("top neighborhoods by resident-nights:",[(k.split('- ')[-1].title(),f"{v:,.0f}") for k,v in top_nb[:5]],flush=True)
print("top night blocks:",top_blocks[:6],flush=True)
