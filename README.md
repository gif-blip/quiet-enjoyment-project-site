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

## Email signup

The signup form is off until a provider is wired up. Until then every signup
spot on the site falls back to the mailto invitation it used before, so the site
never ships a form that goes nowhere.

Configure it in one place — `SIGNUP` in `pipeline/site_content.py` — then rebuild.
Two modes:

- **`mode = 'iframe'`** — the Squarespace route. Squarespace has no public form
  endpoint another domain can post to, so the only supported way to use an Email
  Campaigns mailing list from here is to build a Squarespace page containing
  nothing but a Newsletter block, point that block at the list, and put the
  page's URL in `action`. Set `height` to fit the embedded form.
- **`mode = 'post'`** — a plain form POST to `action`, for any provider that
  accepts a cross-origin submission (Buttondown, Mailchimp, Formspree). Set
  `field` if the provider names the address input something other than `email`,
  and list any required hidden inputs in `hidden`.

The form renders on the home, reports, and For Residents pages, and in the
footer of every page. In `iframe` mode the footer shows a link to the form on
the reports page instead — an iframe on all nine pages is too heavy.

## Donations

`DONATE` in `pipeline/site_content.py` holds the ask. While `url` is blank the
support page and the reports block show the mailto ask instead of a Donate
button, so nothing points at a collection page that does not exist yet. Set
`url` to the Open Collective page and rebuild to switch it on.

The ask appears on its own `support.html` page, in a short block on the reports
page, as a paragraph on About, and as a footer link site-wide. The footer link
renders whether or not `url` is set, because the support page carries the mailto
ask on its own.

Two things to re-check before soliciting publicly:

- **`DONATE['status']` must not get ahead of the paperwork.** It selects the tax
  copy: `'forming'` says the project is not yet tax-exempt and is organising as
  a 501(c)(4); `'c4'` says it is one. Flip it the day the entity exists and
  Form 8976 is filed, not before — claiming exempt status not yet held is the
  precise error the rest of the support page exists to avoid.
- **Fiscal hosting changes the tax answer.** Both copy variants say gifts are not
  deductible, which holds for an independent collective and for a 501(c)(4).
  Being fiscally hosted by a 501(c)(3) would make gifts deductible through the
  host, and both variants would then be wrong.
- **Colorado's Charitable Solicitations Act keys on soliciting, not on tax
  status.** Registration with the Secretary of State is generally required
  before soliciting, with an exemption under $25,000 a year in gross
  contributions or ten or fewer contributors in the fiscal year.

`pipeline/archive/` holds an immutable monthly snapshot of the city's
rental-property calls feed. That feed is a rolling 365-day window, so without
these snapshots exact-address history would be lost permanently.

`pipeline/history.json` holds fixed per-address counts by report year from the
2022–2025 records-request extract. History does not change, so it is frozen.
