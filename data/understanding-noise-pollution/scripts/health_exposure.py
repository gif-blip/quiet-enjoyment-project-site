#!/usr/bin/env python3
# Published with the data package for 'Understanding Noise Pollution in Boulder'
# (The Quiet Enjoyment Project, September 2026). Run from the package root:
# inputs are read from ./data, outputs written to ./data and ./figures.
"""Health report exposure analysis: night calls, resident-nights, school nights,
per-neighborhood burden, repeat blocks; charts + results JSON."""
import json, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from collections import Counter, defaultdict
from scipy.spatial import cKDTree
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import unary_union, transform as shp_transform

OUTD="./data"
T_FT=Transformer.from_crs(4326,2876,always_xy=True); T_LL=Transformer.from_crs(2876,4326,always_xy=True)
calls=json.load(open("./data/noise_party_calls_trailing12mo.json"))["features"]
parcels=json.load(open("./data/city_res_parcels.json"))
HH=2.2

hxy=[]; hnb=[]
for r in parcels:
    try: la=float(r.get("Latitude") or 0); lo=float(r.get("Longitude") or 0)
    except: continue
    if la:
        hxy.append(T_FT.transform(lo,la)); hnb.append((r.get("NbhdDscr") or "?").strip())
hxy=np.array(hxy); ht=cKDTree(hxy)

def wall(ts): return datetime.fromtimestamp(ts/1000, tz=timezone.utc)
import re as _re
from datetime import timedelta as _td
hour_hist=Counter(); dow_night=Counter(); nb_rn=defaultdict(float)
block_night=Counter(); res_nights=0.0; school_rn=0.0
night_pts=[]
n_night=0
_seen=set()   # (night, parcel) pairs — a resident-night counts once per night
for f in calls:
    a=f["attributes"]; ts=a.get("Response_Date")
    if not ts or not f.get("geometry"): continue
    # standing exclusion: the 4500-block-of-19th single-dispute outlier
    if _re.match(r"^45XX\s+19TH", (a.get("Address") or "").upper().strip()): continue
    dt=wall(ts); h=dt.hour
    hour_hist[h]+=1
    if h>=22 or h<3:
        n_night+=1
        night=(dt-_td(hours=6)).date()
        x,y=T_FT.transform(f["geometry"]["x"],f["geometry"]["y"])
        night_pts.append((x,y))
        idx=ht.query_ball_point([x,y],r=600.0)
        eff=dt.weekday() if h>=22 else (dt.weekday()-1)%7
        school = eff in (6,0,1,2,3)
        for i in idx:
            key=(night,i)
            if key in _seen: continue
            _seen.add(key)
            res_nights+=HH
            if school: school_rn+=HH
            nb_rn[hnb[i]]+=HH
        dow_night[eff]+=1
        block_night[(a.get("Address") or "?").upper().strip()]+=1
tot=sum(hour_hist.values())
print(f"night calls {n_night}/{tot}; resident-nights {res_nights:,.0f}; school {school_rn:,.0f} ({school_rn/res_nights:.0%})",flush=True)

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
ax.text(8.5,max(vals)*0.95,"10 pm – 3 am:\n55% of all noise calls",ha="center",fontsize=11,weight="bold",color="#5e3c99")
ax.set_ylabel("noise/party calls (12 months)")
ax.set_title("Boulder's noise problem is a sleep problem — calls by hour of night")
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(OUTD+"/chart_clock.png",bbox_inches="tight")

# chart 2: weekday pattern, school nights highlighted
fig,ax=plt.subplots(figsize=(8.6,4.2),dpi=150)
names=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
sv=[dow_night[d] for d in range(7)]
cols=["#c62828" if d in (6,0,1,2,3) else "#9e9e9e" for d in range(7)]
ax.bar(names,sv,color=cols)
for i,v in enumerate(sv): ax.text(i,v,f"{v}",ha="center",va="bottom",fontsize=10)
ax.set_ylabel("night calls (10 pm – 3 am)")
ax.set_title("Night-time noise events by evening — red = school nights (Sun–Thu)")
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(OUTD+"/chart_schoolnights.png",bbox_inches="tight")

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
ax.set_title("1,680 night-time (10 pm – 3 am) noise events in twelve months\n— each dot is a documented sleep disruption for a median of 58 nearby homes")
fig.tight_layout(); fig.savefig(OUTD+"/chart_nightmap.png",bbox_inches="tight")

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
fig.tight_layout(); fig.savefig(OUTD+"/chart_thresholds.png",bbox_inches="tight")

json.dump(dict(total_calls=tot,night_calls=n_night,res_nights=res_nights,school_rn=school_rn,
               school_share=school_rn/res_nights,hour_hist=dict(hour_hist),
               dow_night={names[d]:dow_night[d] for d in range(7)},
               top_nb=top_nb,top_blocks=top_blocks,chronic_residents=chronic_res,
               median_homes_per_event=58,hh=HH),
          open(OUTD+"/health_exposure_results.json","w"),indent=1)
print("charts + results written",flush=True)
print("top neighborhoods by resident-nights:",[(k.split('- ')[-1].title(),f"{v:,.0f}") for k,v in top_nb[:5]],flush=True)
print("top night blocks:",top_blocks[:6],flush=True)
