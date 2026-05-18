# QA Checklist — Stage 4
*Pre-delivery gates. Every fail = back to Stage 3, not in-place patch.*

---

## Scope discipline

- [ ] No sequence copy, email structure, subject lines, or LinkedIn message scaffolding present anywhere in outputs.
- [ ] No listbuilding query language (NAICS codes, size band filters, geo tiers) in outputs — those belong downstream.
- [ ] No qualification rules or disqualification logic — downstream.
- [ ] Workspace Context contains exactly the four output types: company description, segment list, role taxonomy, value artifacts pointer.

## Citation gates (no invention)

- [ ] Every fact in `OUT_Workspace_Context.md` traces to an `INT_*` file or a URL.
- [ ] Every job / pain / gain in a Segment VPC traces to a quote or observation in `INT_Voice_Quotes.md` or `INT_Segment_Hypotheses.md`.
- [ ] Every job / pain / gain in a Role VPC traces to `INT_Role_Observations.md` or `INT_Voice_Quotes.md`.
- [ ] Every pain reliever and gain creator in a VPC and in `OUT_Value_Artifacts.md` points to (a) a numbered pain or gain in a VPC, and (b) a feature in `INT_Product_Facts.md`.
- [ ] Every example company and every example person verifiable on the public web.

## VPC completeness

- [ ] Each promoted segment has its own `Segment_<Name>_VPC.md` file.
- [ ] Each segment VPC has all six VPC sections filled (Jobs / Pains / Gains / Pain Relievers / Gain Creators / Products & Services) OR explicit `n/a — see Open Questions §X` with a logged reason.
- [ ] Each segment names champion, decision maker, AND influencer roles.
- [ ] Each promoted role has its own `Role_<Name>_VPC.md` file.
- [ ] Each role VPC carries `Evidence level` filled.
- [ ] Each role VPC has Responsibilities (Jobs), What gets praised (Gains), What gets punished (Pains), KPIs, Pain Relievers, Gain Creators, and the "how exactly we help this role" paragraph all filled.

## Examples gates

- [ ] Every segment has ≥5 example companies with fit / borderline / exclude verdicts and one-line reasons.
- [ ] Every role has 2–3 example real people with resolving LinkedIn URLs.
- [ ] Antiprofile is non-empty for every role.

## Value Artifacts gates

- [ ] `OUT_Value_Artifacts.md` exists.
- [ ] Features inventory is non-empty and each row cites `INT_Product_Facts.md`.
- [ ] Every Pain Reliever statement points to a specific pain in a Segment or Role VPC.
- [ ] Every Gain Creator statement points to a specific gain in a Segment or Role VPC.
- [ ] Cross-reference matrix (segments × roles) is filled.
- [ ] Outreach-ready snippets (§8) cover every segment × role-tier combination needed for the engagement.
- [ ] vs-alternatives section (§6) has 2–4 named alternatives with honest tradeoffs.

## Voice gates

- [ ] Workspace Context §1 ToV uses the client's vocabulary (cross-check 5+ phrases against `INT_Voice_Quotes.md`).
- [ ] No banned word from `INT_Anti_Claims.md` appears in any output.

## Anti-claims / editorial gates

- [ ] Every `INT_Anti_Claims.md` entry appears in `OUT_Workspace_Context.md` §4.
- [ ] On Tier 0 runs, the §4 meta-note about empty anti-claims is present.

## Tier discipline gates

- [ ] Tier scope declared at the top of `OUT_Workspace_Context.md` (v1 / v2 / v3).
- [ ] Every Role VPC `Evidence level` matches tier composition (Tier 0 → LOW; +Tier 1 → MEDIUM; +Tier 2 → HIGH).
- [ ] On Tier 0 runs, Workspace Context §1 ToV carries the "inferred from formal-register sources" note.
- [ ] When Tier 1 / Tier 2 arrive, change log in Workspace Context §7 records what reflowed.

## Open Questions gates

- [ ] Every unresolved item is in Workspace Context §6 with full structure.
- [ ] No Open Question silently closed by guessing.
- [ ] On Tier 0 runs, count is in the 20–30 range.
- [ ] AM briefed on Open Questions before delivery.

## Delivery gates

- [ ] Notion snapshots created for Workspace Context, each Segment VPC, each Role VPC, and Value Artifacts as subpages under the client page.
- [ ] On Tier 0 runs, all subpage titles prefixed `⚠️ v0.1 — public sources only`.
- [ ] `<client>_notion.md` memory reference updated with subpage IDs.
- [ ] AM has scheduled a client call to walk Open Questions before any downstream skill starts.
- [ ] Change log entry added to Workspace Context §7.

---

## Anti-pattern auto-fail

Reject the output if any of these is true:
- A Segment VPC missing either the customer-profile side (Jobs/Pains/Gains) or the value-map side (Relievers/Creators/Features).
- A Role VPC that doesn't include responsibilities, praise dimensions, AND punishment dimensions.
- A Pain Reliever or Gain Creator in `OUT_Value_Artifacts.md` that doesn't trace to a specific pain/gain in a VPC.
- A segment described without naming all three role tiers (champion + DM + influencer).
- Any sequence copy, email structure, listbuilding query, or qualification rule in any output.
- Empty antiprofile on any role.
- Empty Open Questions list.
- Outrizz Exhibit content copied wholesale into Workspace Context or any VPC file.
