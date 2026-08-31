#!/usr/bin/env python3
"""All website copy for quietenjoymentproject.org, in one editable place.

Edit text here; run build_site.py to regenerate the site. Data (watch-list
numbers, charts, stats) comes from the analysis pipeline, not from this file.
"""

SITE = {
    'name': 'The Quiet Enjoyment Project',
    'domain': 'quietenjoymentproject.org',
    'email': 'yourneighbor@quietenjoymentproject.org',
    'dispatch': '303-441-3333, option 8',
    # Set once the Dropbox folder share link exists:
    'source_data_link': '',
    # A report is published only once its PDF sits in pipeline-input/. The August
    # 2026 report is held back until the pending BPD records request is folded in;
    # drop the final PDF in with this exact filename and rebuild to publish it.
    'reports': {
        'aug2026': 'August 2026 University Hill Noise Report.pdf',
        'oct2025': 'October 2025 University Hill Noise Report.pdf',
    },
}

NAV = [
    ('index.html', 'Home'),
    ('reports.html', 'Reports'),
    ('watch-list.html', 'Watch List'),
    ('know-the-law.html', 'Know the Law'),
    ('health.html', 'Noise & Health'),
    ('asks.html', "What We're Asking For"),
    ('residents.html', 'For Residents'),
    ('data.html', 'Source Data'),
    ('support.html', 'Support'),
    ('about.html', 'About'),
]

FOOTER = (
    'The Quiet Enjoyment Project · An independent, resident-run organization — not affiliated with the '
    'University Hill Neighborhood Association, the University of Colorado, or the City of Boulder · '
    'Boulder, Colorado · <a href="mailto:{email}">{email}</a> · Data from City of Boulder open records. '
    'This site is general information, not legal advice. Launched August 2026 — an initial version; '
    'thoughtful feedback and corrections welcome, and we fix errors promptly.'
)

# --------------------------------------------------------------- email signup
# The signup form renders wherever `mode` is set, and quietly falls back to the
# mailto invitation the site used before while it is blank — so the site never
# ships a form that goes nowhere.
#
#   mode = 'iframe'  Embed a page that hosts your provider's own form. This is
#                    the only route Squarespace supports off-Squarespace: make a
#                    Squarespace page holding nothing but a Newsletter block,
#                    point that block at your Email Campaigns mailing list, and
#                    put the page's URL in `action`. Set `height` to whatever
#                    the embedded form needs.
#
#   mode = 'post'    A plain HTML form POST to `action`. Works with Buttondown,
#                    Mailchimp, Formspree and anything else that accepts a
#                    cross-origin form submission. Set `field` if the provider
#                    names the address input something other than 'email', and
#                    list any required hidden inputs in `hidden`.
#
#   mode = ''        No provider wired up yet. Falls back to mailto.
SIGNUP = {
    'mode': '',
    'action': '',
    'field': 'email',
    'hidden': [],                       # (name, value) pairs the provider requires
    'height': 320,                      # iframe mode only
    'heading': 'Get each report when it publishes',
    'blurb': (
        'We send an email when a new report goes out and when the watch list advances — '
        'a few times a year, nothing else.'
    ),
    'button': 'Sign up',
    'placeholder': 'you@example.com',
    'label': 'Email address',
    'fine': 'The list is used for these emails and nothing else, and we never publish resident names. Unsubscribe in one click.',
    'foot_heading': 'Get each report when it publishes',
    # Shown in the footer when mode is 'iframe' (an iframe per page is too heavy).
    'foot_link': 'Get each report when it publishes — <a href="reports.html#signup">join the email list</a>.',
}

# ------------------------------------------------------------------- donations
# `url` is the donation link (Stripe payment link). While it is blank every donation spot falls
# back to the mailto ask, exactly as SIGNUP does.
#
# This copy assumes the project's structure: a Colorado nonprofit corporation
# operating as a 501(c)(4) social welfare organization, collecting through
# Stripe payment links on the corporation's own account. (Open Collective was
# evaluated and rejected 2026-08-30: its public transaction ledger attaches
# donor names unless each donor individually opts out, which contradicts the
# amounts-public/names-private policy. A 501(c)(3) fiscal host would likewise
# contradict the tax copy and the lobbying posture.)
#
# Three things to hold true:
#   - 'status' selects the tax wording: 'forming' until articles are filed and
#     Form 8976 is submitted, 'c4' after. Never let the copy get ahead of the
#     paperwork.
#   - Disclosure policy: contribution amounts and expenses are public; donor
#     identities are not published. The corporation publishes its own ledger
#     on this site per the Transparency Policy; `url` should point at the
#     Stripe payment link once it exists.
#   - Colorado's Charitable Solicitations Act keys on soliciting, not on tax
#     status. Registration ($10) is required before soliciting, with an
#     automatic exemption under $25,000 a year or ten or fewer contributors.
DONATE = {
    'url': '',
    'button': 'Donate',
    'heading': 'Support this work',
    'ask': (
        'This project runs on public records, and public records cost money. If what we publish here is '
        'useful to you, you can help pay for it.'
    ),
    'uses_title': 'What your money pays for',
    'uses': [
        ('Records requests.', 'Boulder Police dispatch extracts are fulfilled at a per-request cost, and the '
         'multi-year extracts behind our reports are the largest single expense we have.'),
        ('Publishing.', 'The domain, the hosting, and the data pipeline that refreshes this site every week.'),
        ('Notice to owners.', 'Printing and certified mail when we write to a property owner before anything '
         'escalates — the step that quietly resolves most addresses.'),
    ],
    'firewall_title': 'What a donation does not buy',
    'firewall': (
        'It does not buy a place on the watch list, and it does not buy a way off one. Which properties appear '
        'here is decided by public police records applied on published criteria, with no discretionary step — and '
        'we publish the data so that anyone can run the same criteria and get the same list. Nobody who funds this '
        'project can add an address or remove one. If that is what you were hoping to buy, we would rather you '
        'kept your money.'
    ),
    # Flip to 'c4' the day the corporation exists and Form 8976 is filed — not
    # before. Until then 'forming' is the only accurate description, and
    # claiming a status we do not yet hold is the exact error the rest of this
    # page exists to avoid.
    'status': 'forming',
    'tax_title': 'Tax status, plainly',
    'tax_short_forming': 'Not a charity, not tax-exempt — contributions are not tax-deductible.',
    'tax_forming': (
        'The Quiet Enjoyment Project is not a charity and is not, today, a tax-exempt organization. We make no '
        '501(c)(3) claim. Contributions are not tax-deductible, and nobody here will tell you otherwise — if a '
        'deduction is what you are after, this is not the place for it. We are a resident-run organization in the '
        'middle of its paperwork: incorporating as a Colorado nonprofit corporation, to operate as a 501(c)(4) '
        'social welfare organization. Neither step changes the answer on deductibility — 501(c)(4) gifts are not '
        'deductible either, by design — and we will update this page when the paperwork is done, not before.'
    ),
    'tax_short_c4': 'A 501(c)(4), not a charity — contributions are not tax-deductible.',
    'tax_c4': (
        'The Quiet Enjoyment Project is a Colorado nonprofit corporation operating as a 501(c)(4) social welfare '
        'organization. That makes the organization tax-exempt, and it also means contributions are not '
        'tax-deductible. We make no 501(c)(3) claim and will not be making one — if a deduction is what you are '
        'after, this is not the place for it. We chose this structure deliberately: it lets us argue for changes '
        'in the law without a ceiling on how hard, and it lets the organization itself stand behind this work — '
        'in print and, where a chronic property leaves no alternative, in court. We would rather be free to do '
        'both than be able to offer you a write-off.'
    ),
    'ledger': (
        'We publish a ledger on this site of every contribution amount and every expense. You can see what this '
        'project runs on and what it spends without having to ask us.'
    ),
    'privacy_title': 'Amounts public, names private',
    'privacy': (
        'Every contribution amount and every expense goes on the public ledger — including whether this project '
        'runs on many small gifts or a few large ones, which you should want to know. Donor identities are the '
        'one thing we do not publish: this is a small neighborhood where landlords, tenants, and neighbors all '
        'know each other, and supporting noise enforcement should not cost anyone a relationship. What makes that '
        'compatible with everything else on this site is that there is nothing here for money to buy — the watch '
        'list is mechanical, and no donor of any size can put an address on it or take one off.'
    ),
    # Shown on the reports page — the point where someone has just read the work.
    'short': (
        'These reports are built from records we pay for. If they are useful to you, you can help cover the cost.'
    ),
    'foot_link': '<a href="support.html">Support this work</a>',
    'alt': 'Prefer to arrange it directly, or want to give something other than money? Write to <a href="mailto:{email}">{email}</a>.',
}

HOME = {
    'headline': 'Every Boulder home comes with a legal right to quiet enjoyment.',
    'headline_2': 'Quiet is a right, not a request.',
    'mission': (
        'The Quiet Enjoyment Project restores residential quality of life in Boulder neighborhoods '
        'affected by chronic noise — beginning on University Hill — through publishing public data, '
        'resident education, property-owner accountability, and enforcement of laws already on the books.'
    ),
    'stat_block': (
        'Noise complaints on University Hill hit record levels in 2026 — up 50% over last year, despite '
        'increased police enforcement. Half of all complaints happen in just fifteen hours a week. A small '
        'set of repeat addresses drives the problem. We publish who, where, and when — from the city’s own data.'
    ),
    'doors': [
        ('I live here', 'Your call to dispatch is a data point that counts. Learn how to make it count more.', 'residents.html'),
        ('I own or manage property', 'Your property may have a complaint record you have never seen. Check the list, and learn how to come off it.', 'watch-list.html'),
        ('Show me the data', 'Read the reports. Every number is reproducible from public data.', 'reports.html'),
    ],
}

REPORTS = {
    'intro': (
        'We publish a data-driven report series on noise in Boulder’s University Hill neighborhood, built '
        'from Boulder Police dispatch records and the City of Boulder open-data portal. Every figure can be '
        'independently reproduced; our analysis data available on request.'
    ),
    'items': [
        ('August 2026 University Hill Noise Report', 'aug2026',
         'Complaints hit record levels despite an enforcement surge; tickets doubled but follow only 1 call in 21; '
         'the houses named in Report #1 went quiet and new houses took their place. Publishing shortly — we are '
         'folding in a pending Boulder Police records request first.'),
        ('October 2025 University Hill Noise Report', 'oct2025',
         'Three years of data: 37% of the problem from 24 addresses; enforcement failing to deter chronic offenders.'),
    ],
    'findings_title': 'Key findings at a glance',
    'findings': [
        'Complaints are concentrated: a few dozen addresses of 2,049 in the initial zone of focus drive most of the problem.',
        'The problem is predictable: 49% of complaints occur Thursday–Saturday, 9 p.m.–2 a.m.',
        'Consequences work: every house named in our first report saw complaints collapse. Deterrence rotates to '
        'whoever is not being watched — which is why the watch list is permanent.',
        'Enforcement is improving but thin: citations doubled in 2026, yet warnings still outnumber tickets five to one.',
    ],
}

WATCH = {
    'intro': (
        'These are the University Hill addresses with the highest police noise-complaint volumes, from Boulder '
        'Police dispatch records and the City of Boulder open-data portal, with owners of record from the Boulder '
        'County Assessor. The list is updated quarterly and published in full in our report series.'
    ),
    'disclaimer_title': 'What this list is — and is not',
    'disclaimer': (
        'A dispatched complaint is a resident call that police logged against an address. It is not, by itself, a '
        'finding that the law was violated. We publish complaint counts because they are the best available public '
        'measure of where chronic noise comes from — and because under Boulder’s chronic-nuisance ordinance '
        '(B.R.C. ch. 10-2.5), five documented violations in a year — no citation required under the 2024 ordinance — can cost a rental property its license. Owners: if you '
        'believe any figure here is wrong, write to <a href="mailto:{email}">{email}</a> and we will review and '
        'correct promptly. If the noise stops, your address comes off this list — publicly.'
    ),
    'as_of_prefix': 'Complaint window:',
    'as_of_suffix': 'Counted over complete calendar months only, from the City of Boulder open-data portal. '
                    'The underlying data is refreshed weekly; this list advances when a month closes, so an '
                    'address near the threshold cannot appear and disappear from week to week.',
    'criteria': 'Published criterion: an address appears here when police logged six or more noise '
                'complaints against it during the twelve complete calendar months shown above. That '
                'threshold is applied mechanically to the public data — there is no editorial step, and no '
                'one can add or remove an address. Anyone can reproduce this list by applying the same rule '
                'to the same feed.',
    'current_title': 'Current watch list',
    'off_title': 'Off the list',
    'off_intro': (
        'Deterrence works. These addresses led our October 2025 report and have since gone quiet. '
        'We are glad to see them here.'
    ),
    'owners_title': 'For owners and managers',
    'owners': (
        'If your property is on this list, you have probably already received our certified letter. The fastest way '
        'off: a noise addendum in the lease, no outdoor amplified sound, and a manager who answers the phone on '
        'weekend nights. We would much rather celebrate your exit from this list.'
    ),
}

LAW = {
    'intro': (
        'Most people — including many students, owners, and even officers — are wrong about what Boulder noise law '
        'actually says. The short version: it is stricter, and easier to enforce, than almost anyone believes.'
    ),
    'sections': [
        ('If you can hear it from 100 feet, it’s a violation',
         'Since 2022, amplified sound audible 100 feet beyond the property line at night (11 p.m.–7 a.m.), or 200 feet '
         'during the day, is a citable violation — no decibel meter, no complaining neighbor required. An officer can '
         'pace the distance and write the ticket (B.R.C. 5-9-6; Ordinance 8531). Every resident present at a house '
         'generating amplified noise is legally responsible for it. Police have the choice to drive around '
         'neighborhoods and issue tickets.'),
        ('The decibel limits are health standards',
         'Boulder’s residential limits — 55 dB(A) daytime, 50 dB(A) night (B.R.C. 5-9-3) — descend from the U.S. EPA’s '
         'health-based exposure levels and match World Health Organization thresholds. Colorado state law is stricter '
         'still: its nighttime limit begins at 7 p.m. (C.R.S. 25-12-103). <a href="health.html">More on the health page.</a>'),
        ('Repeat complaints reach the rental license',
         'Under Boulder’s chronic-nuisance ordinance (B.R.C. ch. 10-2.5, 2024), a single-family rental with five or more '
         'documented nuisance violations in a year (counted Aug. 1–Jul. 31; no citation is required, and police-documented '
         'warnings are evidence of violations) can be designated a chronic nuisance property — '
         'triggering a mandatory abatement plan and rental-license consequences up to revocation.'),
        ('Residents can sue — and reach the owner',
         'Colorado’s Noise Abatement Act lets any resident ask a district court to shut down a noise nuisance and enjoin '
         'not just the people making the noise but the owner, lessee, or agent of the property from permitting it '
         '(C.R.S. 25-12-104; see <em>Hobbs v. City of Salida</em>, 2025 CO 50).'),
        ('If you’re hosting a party',
         'We are not against parties. We are against your speakers in our bedrooms. Keep amplified sound indoors, '
         'reasonably loud, keep doors and windows shut, wind it down by 11, and nobody calls anyone. A noise ticket in '
         'Boulder can run up to $2,650 per violation — each day is a separate violation — and it follows every resident '
         'of the house, not just the person at the aux cord.'),
    ],
    'note': 'This page is general information, not legal advice.',
}

HEALTH = {
    'intro': (
        'Boulder’s noise limits are not taste standards. They are health standards — and the science behind them has '
        'only gotten stronger since they were written.'
    ),
    'points': [
        ('Where 55/50 come from.',
         'The limits trace to the U.S. EPA’s 1974 determination of the outdoor level "requisite to protect the public '
         'health and welfare with an adequate margin of safety" (55 dB), and to World Health Organization guidance '
         'identifying 55 dB as the threshold of serious annoyance.'),
        ('Nights matter most.',
         'WHO’s health-based night guideline is 40 dB — ten decibels below Boulder’s night limit. WHO places the '
         'thresholds for hypertension and heart-attack risk at 50 dB at night: exactly where Boulder’s limit begins. '
         'There is no margin of safety in our night limit.'),
        ('What the medicine shows.',
         'Chronic noise exposure raises ischemic heart disease risk about 8% per 10 dB (rated high-quality evidence in '
         'WHO’s systematic review). Sleep disruption begins at levels as low as 33 dB at the pillow — harm does not '
         'require waking. A 5 dB increase in chronic exposure was associated with a two-month reading delay in children.'),
        ('The bass problem.',
         'Standard meters under-count bass. At equal readings, bass-heavy amplified music is roughly 3–6 dB more '
         'intrusive than ordinary noise — a party that "complies" on a meter can still be shaking a neighbor’s windows. '
         'Colorado state noise law reflects this.'),
    ],
    'close': (
        'More than half of University Hill’s noise complaints occur during sleeping hours. The people absorbing that '
        'exposure include children, night-shift workers, the ill, and the elderly.'
    ),
    'citations': [
        ('U.S. EPA, Levels Document (1974)', 'https://www.nonoise.org/library/levels74/levels74.htm'),
        ('WHO, Guidelines for Community Noise (1999)', 'https://www.ruidos.org/Noise/WHO_Noise_guidelines_4.html'),
        ('WHO, Night Noise Guidelines for Europe (2009)', 'https://www.polisnetwork.eu/wp-content/uploads/2019/06/who-night-noise-guidelines.pdf'),
        ('WHO, Environmental Noise Guidelines for the European Region (2018)', 'https://www.who.int/europe/publications/i/item/9789289053563'),
        ('Basner et al., The Lancet 383:1325 (2014)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3988259/'),
        ('van Kempen et al., IJERPH 15:379 (2018) — WHO cardiovascular review', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5858448/'),
        ('Leventhall, Noise & Health 6(23):59 (2004) — low-frequency noise', 'https://pubmed.ncbi.nlm.nih.gov/15273024/'),
    ],
}

ASKS = {
    'intro': (
        'Everything on this page can be done under laws Boulder already has. Nothing requires a new ordinance, a new '
        'budget line of any size, or a court. These are the specific administrative changes we have formally asked for '
        '— and where each one stands.'
    ),
    'scope_title': 'A note on scope, for readers inside and outside government',
    'scope': (
        'Everything on this page can be done under ordinances Boulder already has — not one item below needs a new '
        'law, and we think that is the most useful thing we can tell you about it. Where the data convinces us that '
        'an ordinance itself should change, we do advocate for that, and we label it as what it is rather than '
        'folding it in with the administrative asks. You will always be able to tell which kind of ask you are '
        'reading.'
    ),
    'feedback': (
        'These recommendations are an initial version, published August 2026. They will be revised as the data and the '
        'city’s response develop, and we are actively seeking thoughtful feedback — especially disagreement — from '
        'residents, officers, city staff, property owners, and students: <a href="mailto:{email}">{email}</a>.'
    ),
    'groups': [
        ('Of City Council', [
            ('Make proactive noise patrol standing policy — not one sergeant’s briefing. Officers drive the Hill '
             'Thursday–Saturday, 9 p.m.–2 a.m., disperse nuisance parties on observation, and cite on the 100/200-foot '
             'audibility standard. Every word of that is already law (B.R.C. 5-9-6, 5-3-11).', 'Requested Aug. 2026'),
            ('Staff the Hill team through the peak. Its current shift ends at 10 p.m. — the hour the complaint curve '
             'takes off.', 'Requested Aug. 2026'),
            ('Publish a quarterly noise-enforcement scorecard: complaints, response times, warnings vs. citations, '
             'officer-initiated citations. The city’s own open-data feed proves this costs almost nothing.', 'Requested Aug. 2026'),
            ('Set an enforcement policy: second verified complaint at the same address within 12 months brings a '
             'citation, not another warning.', 'Requested Aug. 2026'),
        ]),
        ('Of Boulder Police', [
            ('Patrol proactively, as the Hill sergeant has already directed — no call, no meter, and no complainant are '
             'required to shut down and cite an audible party.', 'Requested Aug. 2026'),
            ('Treat resident sound-meter readings and authenticated video as the corroborating evidence the code '
             'already permits.', 'Requested Aug. 2026'),
            ('Cite, don’t warn, at repeat addresses. A warning at a house with double-digit complaints is not '
             'enforcement; it is scheduling.', 'Requested Aug. 2026'),
        ]),
        ('Of the City Attorney', [
            ('Open chronic-nuisance review (B.R.C. 10-2.5) of every address reaching five documented violations in the '
             'Aug. 1–Jul. 31 nuisance year, and use the abatement-agreement and rental-license tools written for '
             'exactly this pattern.', 'Requested Aug. 2026'),
            ('Publish the number of noise citations prosecuted and their outcomes, so residents can see whether '
             'tickets survive court.', 'Requested Aug. 2026'),
        ]),
        ('Of the University of Colorado', [
            ('Route every off-campus noise citation into the student conduct process systematically — as the University '
             'of Arizona does with police citation records, and Miami University does in Ohio.', 'Requested Aug. 2026'),
            ('Fix or suspend the Party Registration System, and publish its outcomes the way Fort Collins does '
             '(97.5% of registered parties citation-free).', 'Requested Aug. 2026'),
        ]),
        ('Of property owners', [
            ('A noise addendum in every lease, no outdoor amplified sound, and a manager who answers the phone on '
             'weekend nights. The way off the watch list is open and public.', 'Ongoing'),
        ]),
    ],
    'close': (
        'We will mark each item Done when it happens — and say so in the next report. The list is short on purpose. '
        'None of it is hard. All of it is overdue.'
    ),
}

RESIDENTS = {
    'title': 'Report it — every call counts',
    'intro': (
        'Enforcement runs on the record, and the record is built one dispatch call at a time. Even when no officer '
        'comes, your call becomes a data point at that address — and the data is what drives chronic-nuisance '
        'designations, rental-license review, and our reports.'
    ),
    'steps': [
        'Call Boulder police dispatch (non-emergency): <strong>303-441-3333, option 8</strong>. Give the exact address. '
        'Ask for the incident number.',
        'If the party is registered with CU, dispatch phones the host, who has 20 minutes to shut it down before an '
        'officer is sent. Ask dispatch to tell you whether it was registered, and call back if the noise continues '
        'past the window.',
        'If an officer responds, you can ask to be contacted, and you can state that you are willing to be named — '
        'tickets are far more likely when a resident stands behind the complaint. (Since 2022, officers can also cite '
        'with no complainant at all.)',
        'Log it with us: forward your incident number and a one-line description to '
        '<a href="mailto:{email}">{email}</a>. If the noise is chronic, tell us the address — it goes into the same '
        'data pipeline as our reports.',
    ],
    # Sits under the signup form: the list and a chronic-address report are two
    # different asks, and the form only covers the first.
    'report_address': (
        'Dealing with a chronic problem address? Write to <a href="mailto:{email}">{email}</a> and tell us '
        'directly — it goes into the same data pipeline as our reports. We never publish resident names, and we '
        'handle what you send with care. One honest limit: files can be reached by legal process, ours included, '
        'so we promise discretion, not immunity — send what you are comfortable having on file.'
    ),
    'join_title': 'Join',
    'join': (
        'We publish each report to an email list, coordinate through a neighborhood group, and are building the '
        'evidence base for owner accountability. Write to us to join the list; if you are dealing with a chronic '
        'problem address, tell us directly. Our reports name properties, never callers, and we never publish '
        'resident names. We will also be straight about the one limit: like anyone’s files, ours can be reached '
        'by legal process if a case ever goes to court — so we promise care and discretion, not immunity, and we '
        'would rather you know that before you write than after.'
    ),
}

ABOUT = {
    'mission_title': 'Mission',
    'mission': (
        'The Quiet Enjoyment Project works to restore residential quality of life in Boulder neighborhoods affected by '
        'recurrent excessive noise, through public data, education, voluntary compliance, and public-interest '
        'enforcement of existing law. The name is the legal term: every lease and every home in Colorado carries a '
        'right to quiet enjoyment, and Boulder’s own code makes disrupting the quiet enjoyment of a home an offense '
        '(B.R.C. 5-9-5).'
    ),
    'how_title': 'How we work',
    'how': [
        ('Data first:', 'our reports are built from Boulder Police records and the city’s open-data portal, '
         'cross-validated, with methodology published and analysis code available on request.'),
        ('Everyone gets the same rules:', 'our concern is conduct and properties — students, owners, institutions, '
         'and events alike.'),
        ('Escalation, not ambush:', 'education first, owner notice second, city enforcement third, and courts only '
         'for the chronic few after everything else fails.'),
    ],
    'governance_title': 'How we govern this work',
    'governance': [
        ('Corrections come first.', 'Any owner, resident, or official who believes a figure we have published is '
         'wrong can write to us, and we correct promptly and visibly. We publish the underlying data so that anyone '
         'can check our arithmetic without asking our permission.'),
        ('We publish conduct, not people.', 'We name property addresses and owners of record — both matters of '
         'public record — and we do not publish the names of residents, callers, or students. Public officials are '
         'the exception: we name the officials who design and operate the programs we examine, in their official '
         'capacity, as the public record names them — never rank-and-file employees — and any official we name gets '
         'at least two weeks to respond to our findings before publication. Complaint counts are '
         'reported as what they are: calls logged by police, not findings of violation.'),
        ('Court is the last step, and we say up front that we may take it.', 'Education first, owner notice '
         'second, city enforcement third. For the few properties that answer none of that, this project may ask a '
         'court to abate the nuisance — in its own name, or on behalf of affected members — and we would rather '
         'state that plainly than spring it on anyone. What we do not do is practise law or represent individual '
         'residents: a resident pursuing their own claim needs counsel of their own, and we will say so every '
         'time.'),
        ('We say when we are asking to change the law.', 'Most of what we ask for is administrative — enforce and '
         'administer the ordinances Boulder already has, which needs no new legislation. Where the data convinces '
         'us an ordinance itself should change, we advocate for that too, and we label it plainly rather than '
         'mixing it in with the enforcement asks. The distinction is the reader’s to check, not ours to blur.'),
        ('We publish every dollar, but not every name.', 'A 501(c)(4) does not have to disclose anything about '
         'its funding. We post every contribution amount and every expense to a public ledger anyway, because an '
         'organization that publishes other people’s records should show its own — you can see what this project '
         'runs on, and whether any single gift is big enough to matter. Donor identities are the one thing we '
         'keep private: in a neighborhood this small, supporting quiet should not carry a social price. What '
         'keeps that honest is the item below — eligibility is mechanical, so there is nothing a donor could be '
         'buying.'),
        ('Eligibility is entirely public-data-driven.', 'Which properties appear in our reporting is determined '
         'solely by public police records, applied on published criteria. There is no discretionary step and no '
         'editorial judgment about who belongs on the list. Nobody — not the people who run this project, not '
         'anyone who supports it financially — can add a property or remove one. The data decides, and we publish '
         'the data so that anyone can run the same criteria and get the same list.'),
    ],
    'who_title': 'Who we are',
    'who': (
        'Founded by University Hill residents in 2025 after three years of documented escalation in neighborhood noise.'
    ),
    'independence': (
        'The Quiet Enjoyment Project is an independent, resident-run organization. It is not affiliated with the '
        'University Hill Neighborhood Association (UHNA), the University of Colorado, or the City of Boulder, and '
        'it takes no money from any of them.'
    ),
    'contact_title': 'Contact',
    'contact': (
        '<a href="mailto:{email}">{email}</a> — residents, owners, media, corrections, and offers to help all welcome.'
    ),
    'donate_title': 'Support',
    'donate': (
        'This work is paid for by the people it serves. We are not a registered charity, we make no 501(c)(3) '
        'claim, and contributions are not tax-deductible — <a href="support.html">what a donation does and does '
        'not buy</a> is set out in full on the support page.'
    ),
    'feedback': (
        'This website is an initial version, published August 2026. Thoughtful feedback on any of it — the data, the '
        'law, the recommendations — is genuinely welcome at the same address.'
    ),
}

DATA = {
    'intro': (
        'Every number we publish traces to public records you can pull yourself. This page holds the source data behind '
        'each report, exactly as received or downloaded, along with the live public endpoints we use.'
    ),
    'live_title': 'Live public sources (no records request needed)',
    'live': [
        ('City of Boulder Open Data — "Boulder PD Calls For Service"',
         'https://open-data.bouldercolorado.gov/items/125cd571f3ea4e26bc58c12a2da561b3',
         'Every police call since January 2023, updated daily, including noise complaints, first-officer arrival times, '
         'and outcomes.'),
        ('City of Boulder public-safety dashboards', 'https://bouldercolorado.gov/crime-dashboard',
         'The city’s own dashboards, including rental-property calls for service.'),
        ('Boulder County Assessor property search', 'https://maps.bouldercounty.org/boco/PropertySearch/',
         'Owners of record for every property in the county.'),
    ],
    'files_title': 'Report source files',
    # (label, url or '' for not-yet-published, description)
    'files': [
        ('October 2025 report', [
            ('Boulder Police dispatch records, Oct 2022 – Oct 2025 (Excel)',
             'https://www.dropbox.com/scl/fi/cou41tywcdwiqm3psb1bu/CFS-Noise-Complaints-102022-102025.xlsx?rlkey=mt2zeoov4v1rzcvo2ldtm1rz8&dl=0',
             'The dispatch extract obtained by records request: every noise call for service citywide, with incident '
             'number, timestamp, problem type, and address.'),
            ('University Hill impact zone — 2,049 addresses (CSV)',
             'https://www.dropbox.com/scl/fi/psf07na38gkcinz7d7f47/University-Hill-Noise-impact-zone.csv?rlkey=hhzvyvbg6b5q53yq7cal3z5lx&dl=0',
             'The address list defining the study area, exported from the Boulder County Assessor.'),
            ('Analysis workbook, Oct 2022 – Oct 2025 (Excel)',
             'https://www.dropbox.com/scl/fi/2r8ze1a92vust2qqatnjp/Noise-complaints-analysis-October-2022-2025.xlsx?rlkey=eyesdft5e5unp72quqfpwtjo3&dl=0',
             'Every pivot, year table, and top-offender list behind the October 2025 report.'),
        ]),
        ('August 2026 report', [
            ('Noise calls for service, Jan 2023 – Aug 2026 (CSV)', '',
             'Snapshot of the city open-data feed as downloaded Aug. 15, 2026 — 9,961 calls with arrival times '
             'and outcomes.'),
            ('Rental-property noise calls, trailing 365 days (CSV)', '',
             'Exact-address noise calls at licensed rentals, from the city’s rental-property feed.'),
        ]),
    ],
    'notes_title': 'Notes on the data',
    'notes': (
        'Police dispatch records contain incident numbers, timestamps, problem type, and addresses only — no caller '
        'information of any kind. A dispatched complaint is a logged resident call, not a finding of violation. A data '
        'dictionary describing every file and field is included in the folder.'
    ),
}
