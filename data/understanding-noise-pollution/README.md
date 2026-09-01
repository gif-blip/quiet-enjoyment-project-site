# Understanding Noise Pollution in Boulder — Data Package
**The Quiet Enjoyment Project · September 2026 · Version 1.2**

This package contains the datasets, scripts, and figures behind the report
*Understanding Noise Pollution in Boulder* (QEP, September 2026), published per
the report's transparency commitment. Every number derived from these datasets
can be re-derived by running the scripts; the citation and disposition figures
rest on police records published separately (see below). Questions and corrections:
yourneighbor@quietenjoymentproject.org — we publish corrections promptly and
prominently if we err.

`checksums.txt` carries a SHA-256 hash of every other file in the package so
that any copy can be verified against the published original.

## What's in the package

**data/**
| File | What it is | Source |
|---|---|---|
| `noiseb_calls_citywide_2023-01_2026-08.json` | All 9,961 citywide noise complaints (problem type NOISEB), Jan 1 2023 – Aug 14 2026, hundred-block precision | City of Boulder open-data ArcGIS feed, pulled 2026-08-15 |
| `rental_noise_calls_trailing12mo.json` | Noise calls at licensed rental properties (exact address), trailing 365 days | City of Boulder "Rental Property Calls for Service" open-data feed, pulled 2026-08-15 |
| `rental_licenses_parcels_2026-08.json` | 10,830 active licensed-rental parcels with polygon geometry. License-holder name and company fields have been removed — the analysis uses only geometry, address, and license status, and we minimize personal data as a rule; the unabridged layer is the City's own public dataset | City of Boulder rental-license GIS layer, pulled 2026-08 |
| `cu_walkshed_15min.kmz` | The CU walkshed: a 0.75-mile straight-line buffer around the university-district boundary (≈ a 15-minute walk) | QEP, from the City's official subcommunity polygon |
| `streets_osm_arterials.json` | Boulder arterial streets drawn on the maps | © OpenStreetMap contributors, ODbL; Overpass extract 2026-08-31 |
| `walkshed_population_2026-08-31.json` | Walkshed population and group-quarters split | 2020 census PL 94-171, block level (see scripts) |
| `walkshed_age_split_2026-08-31.json` | Walkshed household population by age; the permanent-resident count | 2020 census DHC table P12, block level (see scripts) |
| `term_break_fingerprint_2026-08-31.json` | Complaints per night by academic period, inside/outside the walkshed | Derived; see `term_break_analysis.py` |
| `health_exposure_results.json` | Resident-night proximity estimates (173,441/yr, parcel-night deduplicated, outlier excluded; 46% Sun–Thu) | Derived; see `health_exposure.py` |
| `noise_party_calls_trailing12mo.json` | The 3,043 party/noise calls underlying the health exposure figures | City of Boulder open data |
| `city_res_parcels.json` | Residential parcel points (parcel number, coordinates, land sqft, assessor neighborhood — no owner information) used for the households-within-earshot join | Boulder County Assessor, pulled 2026-08-22 |
| `citylimits.json` | City of Boulder boundary polygon | City of Boulder GIS |
| `cu_halfmile_buffer.kmz` | Half-mile campus ring (reported for comparison) | QEP |

**scripts/** — the analysis code, as run, with file paths rewritten to the
package layout: run any script from the package root and it reads `./data`
and writes `./data` and `./figures`. The census
scripts (`permanent_pop2.py`, `age_split.py`) expect the public 2020 census
PL 94-171 and DHC bulk files for Colorado unzipped into `./census/` — the
download URLs are in each script's header (~220 MB, not duplicated here) —
and reproduce the published aggregates exactly; the county totals printed by
each script (330,758 residents; 12,094 university group quarters) verify a
correct download.

**figures/** — every chart in the report, at publication resolution.

## Where each headline number comes from

| Claim in the report | Data | Script |
|---|---|---|
| 70% of complaints inside the CU walkshed (6,297 of 9,011) | noiseb + walkshed | `report_stats.py` |
| 10.9 complaint calls/night Thu–Sat in term; one per 44 min; Sept weekends 19; highest night in dataset 38 (Oct 30, 2025) | noiseb + walkshed | `night_stats.py` |
| Term 6.0/night (73%) vs winter break 1.0; move-in fortnight 10.2 (78%) | noiseb + walkshed | `term_break_analysis.py` |
| School-year trend 1,408 → 1,515 → 1,777; spring 2026 +24% | noiseb + walkshed | `report_charts2.py`, `report_maps_v3.py` |
| 3.5x complaints per rental inside the walkshed (0.26 vs 0.07) | rental calls + rental parcels + walkshed | `report_charts2.py` |
| 28,010 permanent residents (26% of city population, 36% of its permanent residents), incl. 3,957 children; 4.1x per-permanent-resident rate (matched proxies both sides) | census blocks + walkshed + citylimits | `permanent_pop2.py`, `age_split.py` |
| 55% of complaints 10 p.m.–3 a.m.; hourly distribution | noiseb | `report_charts2.py` |
| ~173,000 resident-nights within earshot of a nighttime call (proximity estimate); 46% Sun–Thu | party/noise calls + parcels | `health_exposure.py` |
| Maps (noise vs rentals; session vs winter break) | noiseb + rentals + walkshed + OSM streets | `report_maps_v3.py` |

**Citation and disposition figures** (1 citation per 25 complaints in South
Boulder vs 1 per 128 in the university district; the barking-dog comparison;
warnings-per-summons) derive from Boulder Police records produced to QEP under
the Colorado Criminal Justice Records Act, three-year window ending October
2025. Those source extracts are published separately on our Source Data page
(quietenjoymentproject.org/data.html) — they are larger than this package and
shared in their original form.

## Conventions and notes

- **The excluded block.** One residential block — the 4500 block of 19th
  Street — generated 950 complaints (9.5% of the citywide total) from a single
  ongoing dispute unrelated to the report's subject. It is excluded from every
  figure; the raw data here includes it, and every script applies the
  exclusion in code, so the choice is visible and reversible.
- **Timestamps.** The city's ArcGIS feeds store local wall-clock times in
  epoch fields; the scripts read them accordingly. Calls before 6 a.m. are
  attributed to the prior night.
- **Academic windows.** Term-core Sep 5–Nov 15 and Feb 1–Apr 15
  (ex-spring-break); deep winter break Dec 22–Jan 8. Rates are per night, so
  unequal window lengths compare like-for-like.
- **Privacy and data minimization.** Every record here comes from a source
  the government itself publishes: City of Boulder open-data feeds (which
  carry incident numbers, timestamps, coordinates, and — in the rental-calls
  feed — exact incident addresses, exactly as the City publishes them),
  Boulder County Assessor parcel records, federal census aggregates, and
  OpenStreetMap. The package contains no student records, no University
  production data, and no information about complainants (none exists in
  these sources). Where a source field was not needed for the analysis and
  named individuals — the rental layer's license-holder fields — we removed
  it; the unabridged layer remains available from the City. Incident
  addresses identify properties, not people, and joining these files adds
  nothing beyond what the City's own portal already permits. The
  organizational contact details in this README are published deliberately.

## Licenses and attribution

- City of Boulder open data: per the City's open-data terms.
- U.S. Census Bureau data: public domain.
- Street geometry: © OpenStreetMap contributors, Open Database License (ODbL).
- QEP scripts, derived datasets, and figures: Creative Commons Attribution 4.0
  (CC BY 4.0) — reuse freely with attribution to The Quiet Enjoyment Project.

*The Quiet Enjoyment Project · quietenjoymentproject.org ·
yourneighbor@quietenjoymentproject.org · 885 Arapahoe Avenue, Boulder, CO 80302*
