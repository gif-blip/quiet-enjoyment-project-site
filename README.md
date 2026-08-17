# quietenjoymentproject.org

The public website of The Quiet Enjoyment Project — a Boulder, Colorado resident
initiative documenting chronic residential noise and pressing for enforcement of
existing law.

This repository holds the **generated site only**. It is published with GitHub Pages
at https://quietenjoymentproject.org.

Pages are produced from a data pipeline (Boulder Police dispatch records and the
City of Boulder open-data portal) rather than hand-edited, so the tables and charts
here always match the published reports.

Corrections and questions: yourneighbor@quietenjoymentproject.org

## Automated monthly refresh

```bash
python3 pipeline/update.py   # fetch open data, archive snapshot, recompute
python3 pipeline/build.py    # regenerate every page
```

GitHub Actions runs both every Monday and commits any changes
(`.github/workflows/update.yml`); it can also be triggered by hand from the
Actions tab, which is useful during the September peak. No credentials are
required — both City of Boulder feeds are public.

**Cadence, deliberately split.** The city's noise feed updates daily and these
runs are free, so the weekly schedule keeps charts and enforcement figures
current. The published watch list is intentionally slower: `update.py` counts
only complete calendar months, so the list advances when a month closes rather
than every week. That prevents an address sitting near the six-complaint
threshold from flickering on and off — the rule is mechanical, and the list
should look as stable as the rule is.

`pipeline/archive/` holds an immutable monthly snapshot of the city's
rental-property calls feed. That feed is a rolling 365-day window, so without
these snapshots exact-address history would be lost permanently.

`pipeline/history.json` holds fixed per-address counts by report year from the
2022–2025 records-request extract. History does not change, so it is frozen.
