# Team seats for sales managers, briefing for Harbor Reports

## 0. What this document is

This is a raw input dump, not a finished marketing plan. It captures the product team's full record for Team seats: the written explainer, the comments, the open questions and the "do not claim" guardrails.

Everything here was written by the Harbor Reports product team and describes current designs, not shipped code. Treat the screens as intent.

Three things to carry into any downstream work:

1. Team seats are in closed beta. General release is planned for February 24, 2027. Status in the tracker is in progress.
2. Beta numbers in Section 3 come from the closed beta only. Always label them as beta results. Never present them as results for all customers.
3. Section 5 (open questions) and Section 6 (guardrails) are hard constraints. The three open questions do not block a launch post, but the guardrails apply to every sentence.

## 1. Source record

| Field | Value |
|---|---|
| Task | Team seats: one pipeline report for a whole sales team |
| Status | in progress (closed beta running) |
| Priority | High |
| Target date | February 24, 2027 |
| Owner | Dana, product lead |
| Watchers | Tomas (head of sales success), Priya (marketing lead), Leo (support lead) |

## 2. Comments on the record

Dana, Nov 3, 2026: "Adding Tomas and Priya as followers. The explainer and the beta notes are in the description. Target is late February."

Leo, Nov 4, 2026: "Following for the help center. The invite and role articles will need new text."

No threaded replies on either comment.

## 3. Full product write-up

### TL;DR

Today one person owns a Harbor Reports account and builds the weekly pipeline report alone. A manager who wants numbers from five reps has to ask each rep for an export and combine them by hand. Team seats change that. A manager invites reps, each rep connects their own pipeline export, and the manager sees one weekly report for the whole team that still reads in two minutes.

### The problem, concretely

Nadia runs a team of six reps. Every Monday she needs one page for her director. Four reps email her an export. One forgets and one sends last month's file. She pastes it all into a sheet and builds the page at 9 pm on Sunday.

By Tuesday the director asks which deals slipped. Nadia cannot say, because the sheet only holds totals. The reps never see the report at all.

That is the failure we are fixing. The single report works well. It just was never built for a team.

### What we are building

Three ideas.

1. Invite and connect. A manager sends invites. Each rep connects their own export once, on a refresh schedule the rep picks.
2. One team report. The weekly report rolls every rep into one page, with a view per rep one click away.
3. Simple roles. A manager sees the team. A rep sees their own deals and the team summary, never another rep's deal notes.

The home is a new Team page in settings. It lists seats and shows who has connected and when each export last refreshed.

### What a team seat is, in plain terms

A seat is a named person with their own export and a role. A shared login hides who changed what, and a forwarded PDF is stale when sent. With seats, the software knows whose deals are whose, so the manager's page adds up without a sheet.

### Why this matters to customers

- A manager gets the Monday page without chasing anyone.
- Numbers add up because each deal belongs to one rep.
- A missing export is visible before the report goes out.

### Proof from the closed beta

These are beta results from a closed group, not results for all customers.

- 31 teams took part over 8 weeks.
- Managers reported that building the weekly team page took 52 minutes before team seats and 11 minutes with them.
- 24 of the 31 managers said they would not go back to combining exports by hand.
- The beta group was self selected. Teams ranged from 3 to 15 reps. Results may differ for larger or smaller teams.

### Competitive landscape

| Product | Team reporting today | Where we differ |
|---|---|---|
| Harbor Reports, current | One owner builds one report alone | This project |
| Rival A | Team dashboards, set up by an admin | Closest rival. We need no admin setup |
| Rival B | Forecast roll ups for large sales orgs | Heavy for a small team |
| Rival C | Shared scoreboards for reps | A motivation view, not a manager report |
| Rival D | Quota tracking with manual entry | Reps type numbers in. We read their export |

### How to position it

Team reporting is a known buying need, and Rival A proved it. Our claim is a team report that still reads in two minutes, with no admin and no sheet. Any line about price or plans waits for open question 1.

### Screenshots

Six screens, in the order the product tour shows them.

1. Team page. Seats with a status chip, connected or waiting, and the last refresh time.
2. Invite dialog. A manager adds emails and picks a role, and the dialog says what a rep will see.
3. Rep onboarding. A rep connects an export and previews their own deals before sharing.
4. Team report. Total pipeline, deals that moved, deals that slipped with the rep's reason, and a row per rep.
5. Rep view. The same page, but the rep sees only their own deals in full.
6. Missing export warning. A notice lists reps whose export is older than a week.

### What each type of user gets

Managers get one page and a list of who is late. Reps get their own numbers and the team total. Founders with a small sales team get a weekly page without hiring someone to build it.

### Suggested assets

- A one minute product tour: invite a rep, rep connects, manager opens the team report.
- One GIF of the missing export warning appearing and clearing.
- A blog post on why a weekly team report breaks when one person builds it alone.
- Help center rewrite of the invite and role articles.

### Fact check

Dana owns accuracy, especially on roles, rep visibility, beta numbers, pricing and plan wording.

## 4. Feature reference sheet

| Capability | As designed |
|---|---|
| Scope | One team per account |
| Roles | Manager and rep |
| Team report | One weekly page with a view per rep |
| Rep visibility | Own deals in full, others as totals |
| Missing export warning | Shown when an export is older than a week |
| Beta status | Closed beta only |

## 5. Open questions, unresolved, ask before writing

These three do not block a launch post. Do not write around them. Leave the topics out, or ask first.

| # | Question | Status | Owner |
|---|---|---|---|
| 1 | Pricing and plans. Which plans include team seats and how seats are priced. | Open. Say nothing about price or plans until confirmed. | Dana, product lead |
| 2 | Maximum team size at general release. | Open. Beta teams ran up to 15 reps. | Dana, product lead |
| 3 | Whether the weekly report can be sent to people outside the team. | Open. Do not mention external sharing. | Leo, support lead |

## 6. Guardrails, what not to claim

- Do not say "per-seat pricing". Pricing is undecided.
- Do not say "unlimited seats". A team size limit is not yet set.
- Do not say "available on every plan". Plan gating is not confirmed.
- Do not present beta numbers as results for all customers. Always write "in the closed beta".
- Do not say it is live. Team seats are in closed beta until the release date.

## 7. Approval path

Dana checks accuracy on roles, rep visibility, beta numbers, pricing and plan wording. Priya approves tone before anything is posted.

Approved for marketing: yes, Dana, Nov 12, 2026.
