---
name: workspace-context-and-icp-spec
description: Use at the start of any Outrizz engagement (new client or new track) to build a workspace context — company description, ICP segments, roles within segments (including influencers), Value Proposition Canvas mapping per segment and per role, and solution value artifacts for outreach. Triggers on "new client", "new segment", "ICP", "roles", "workspace context", "VPC", "value proposition". Does not produce sequences, listbuilding queries, or qualification methodology — those are separate downstream skills that consume this skill's outputs.
license: Outrizz proprietary
---

# Workspace Context and ICP Spec

Pre-outreach skill. Builds the **workspace context** — the conceptual map of the client's company, who they sell to, and how their solution maps to those buyers' jobs / pains / gains.

**What this skill produces (and only this):**
- Company description.
- ICP segments.
- Roles inside segments (champion + decision maker + influencer).
- Value Proposition Canvas per segment.
- Value Proposition Canvas per role — what the role is responsible for, what gets them praise, what gets them punished, and how the product specifically helps them.
- Solution value artifacts (features & services, pain relievers, gain creators) — outreach-ready value statements derived from the VPCs above.

---

## 1. Companion files

| File | Purpose |
|---|---|
| `INT_Voice_Quotes.md` | Verbatim language from public sources. Primary source for Tone-of-Voice and pain phrasing. |
| `INT_Product_Facts.md` | Verifiable facts only — specs, customers, geo, size signals — each cited to a URL. Source for Features & Services. |
| `INT_Anti_Claims.md` | "Do not say X" with source. Thin by default; populates from Tier 2 inputs. |
| `INT_Segment_Hypotheses.md` | First-pass segment guesses from public sources, with example companies and a verification matrix. |
| `INT_Role_Observations.md` | Role / title / authority patterns mined from LinkedIn, customer logos, job ads. |
| `OUT_Workspace_Context.md` | Master output: company description + segment list + role taxonomy + messaging guardrails + open questions. Indexes the per-segment and per-role files. |
| `OUT_Segment_VPC.md` | Per-segment template: VPC (jobs / pains / gains → pain relievers / gain creators) + example companies. |
| `OUT_Role_VPC.md` | Per-role template: responsibilities, praise/punishment, VPC mapping, example real people, antiprofile. |
| `OUT_Value_Artifacts.md` | Outreach-ready: features inventory + pain reliever statements + gain creator statements + proof points + differentiators, mapped back to segments and roles. |
| `QA_Checklist.md` | Pre-delivery gates. |

---

## 2. When to use

- New Outrizz client just signed.
- Existing client adds a new ICP / segment.
- Pilot results require ICP to be re-spec'd.
- A downstream skill is blocked because "we don't really know who we're targeting / why they'd care".

Do not use for: sequence drafting, listbuilding execution, lead qualification.

---

## 3. Inputs — three tiers

### Tier 0 — Base (always available, ships v1)

The minimum we always have. Enough to deliver v1 of Workspace Context + Segment VPCs + Role VPCs + Value Artifacts.

- **Client website** — homepage, About, Product/Solution, Customers, Pricing, Resources.
- **Company LinkedIn page** — About, Products, Updates, headcount band, Locations.
- **Web research around the client:**
  - Reviews: G2, Capterra, Trustpilot, AppStore/PlayStore, Glassdoor.
  - News & press: trade press, Crunchbase News.
  - Funding & size signals: Crunchbase, public ARR/revenue mentions, SEC filings if relevant, headcount on LinkedIn.
  - Hiring signals: Greenhouse / Workable / Lever job ads.
  - Customer & partnership signals: customer logos + case studies on customer-side websites + press releases naming the client.
  - Competitor / category context: G2 "compared to" pages, analyst writeups.
- **Outrizz internals (if available):** MSA, any Exhibit-A-style starting sketch, AM handoff notes. Approximate, not source of truth.

**What Tier 0 produces:** Workspace Context v1, per-segment VPC v1, per-role VPC v1, Value Artifacts v1, Open Questions list (**at most 10 items — only the highest-impact ones**). All role VPCs marked `Evidence level: LOW`. Notion subpage titles prefixed `⚠️ v0.1 — public sources only`.

### Tier 1 — Additive (public-facing voice content)

Strengthens Tone of Voice and supplements facts. Not a precondition.

- Founder LinkedIn posts (up to 20 posts, none older than 12 months).
- Company LinkedIn posts (up to 20 posts, none older than 12 months).
- Founder / team podcasts and public interviews.
- Conference talks / webinars publicly available.

**What Tier 1 changes:** ToV becomes evidence-backed instead of inferred. `INT_Product_Facts.md` and `INT_Voice_Quotes.md` get more rows. `INT_Anti_Claims.md` may gain first real entries. Role VPCs upgrade to MEDIUM where buyer-side public material now exists.

### Tier 2 — Highest evidence (often never arrives)

Client-provided raw materials.

- Founder / sales / CS interview transcripts.
- Pitch decks / investor decks.
- Demo videos.
- Internal case studies, CRM exports.
- Internal positioning / brand guidelines.
- Meeting notes.

**What Tier 2 changes:** Anti-claims populate properly. Segment and role hypotheses validate against real buyer data. VPC pains/gains move from inferred to evidenced. Role VPCs upgrade to HIGH. `⚠️ v0.1` warning comes off.

### 3.4 Folder convention

```
/Documents/Claude/Projects/<Client> Project/
├── 00_inputs_raw/
│   ├── client/     ← Tier 0: site + LI page + web research saves; later: posts, podcasts, decks
│   └── outrizz/    ← MSA, Exhibit (if any), AM handoff
├── 01_intermediate/   ← INT_* outputs
└── 02_outputs/        ← OUT_* artifacts (versioned: v1 from T0, v2 with T1, v3 with T2)
```

---

## 4. Outputs

| Output | File | Purpose |
|---|---|---|
| Workspace Context | `<Client>_Workspace_Context.md` | Master doc indexing everything. |
| Segment VPC | `<Client>_Segment_<Name>_VPC.md` (one per segment) | Customer-profile + value-map per segment. |
| Role VPC | `<Client>_Role_<Name>_VPC.md` (one per role across all segments) | Customer-profile + value-map per role. |
| Value Artifacts | `<Client>_Value_Artifacts.md` | Outreach-ready value statements distilled from segment + role VPCs. |

Every output goes to Notion as a subpage under the client page after sign-off.

---

## 5. Process (4 stages, run per tier)

**Stage 1 — Collect (Tier 0).** Pull site + company LinkedIn page. Run the web-research sweep. Place any Outrizz internals in `outrizz/`. Smell test: can you state in one sentence what the client sells, name 5 candidate target companies, and describe size/stage? If not, keep collecting.

**Stage 2 — Extract.** Produce the five `INT_*.md` files. Quote-heavy, citation-mandatory.

**Stage 3 — Draft.** Assemble outputs:
1. `OUT_Workspace_Context.md` — top-level: company description, candidate segments list, candidate roles list (incl. influencer for each segment), messaging guardrails, open questions index.
2. For each promoted segment: `OUT_Segment_VPC.md` filled — jobs / pains / gains on the customer profile side; pain relievers / gain creators / features mapping on the value map side; example companies (fit / borderline / exclude).
3. For each role across all segments: `OUT_Role_VPC.md` filled — responsibilities (jobs), praise dimensions (gains), punishment dimensions (pains), specific pain relievers / gain creators tied to this role's daily life, example real people, antiprofile.
4. `OUT_Value_Artifacts.md` — distill the value map sides of all segment + role VPCs into an outreach-ready inventory.

Every role VPC carries `Evidence level`.

**Stage 4 — Validate.** Run `QA_Checklist.md`.

Time budget for Tier-0-only v1: ~½ to 1 working day for a typical client (one ICP, 2–4 segments, 4–8 roles).

### 5.5 Reflow when Tier 1 / Tier 2 arrives

- **Tier 1 arrives:** save into `client/`. Re-mine `INT_Voice_Quotes.md`. Rewrite Workspace Context §3 (ToV) and feed reinforced facts into Product Facts. Upgrade role VPCs to MEDIUM where buyer-side public material exists. Bump filenames to v2.
- **Tier 2 arrives:** save into `client/`. Reflow all five INT files. Validate segment + role hypotheses against new evidence — promote `hold` items, drop unsupported ones. Anti-claims start populating. Role VPCs upgrade to HIGH where interviews cover the role. Bump to v3; remove `⚠️` prefix.

---

## 6. Hard rules

1. **Scope discipline.** This skill produces workspace context — company + segments + roles + VPC + value artifacts. It does **not** produce sequence copy, email structure, subject lines, listbuilding criteria, or qualification rules. Those are downstream.
2. **No invention.** Every fact in outputs traces to a URL or a client-provided file. Gaps go to Open Questions, never into outputs as fact.
3. **Tier 0 ships v1.** Don't wait for higher tiers.
4. **VPC mandatory per segment AND per role.** Both customer-profile side (jobs/pains/gains) and value-map side (pain relievers/gain creators/features) must be filled — or explicitly marked `n/a — see Open Questions §X` with reason.
5. **Influencer always included.** Each segment lists champion + decision maker + influencer, even when influencer is hard to identify. If you can't name the influencer role, log it as an Open Question.
6. **Examples or it didn't happen.** Each segment ≥5 example companies (fit/borderline/exclude). Each role 2–3 real example people with LinkedIn URLs. If those numbers aren't reachable from public research, the segment/role is hypothetical → Open Questions, not a promoted output.
7. **Value artifacts trace back.** Every pain reliever / gain creator statement in `OUT_Value_Artifacts.md` points to (a) the pain/gain it addresses in a segment or role VPC, and (b) the feature or service that delivers it from `INT_Product_Facts.md`. No dangling claims.
8. **Open Questions is the relief valve — but bounded.** Tier 0 runs produce **at most 10 open questions** — only the ones that materially block downstream listbuilding, sequence-writing, or qualification. Curate ruthlessly: if it doesn't block work, it doesn't get logged. Lower-priority uncertainties go inline as `[?]` notes in the relevant section, not into the OQ list.
9. **Evidence level mandatory on every role VPC** — LOW / MEDIUM / HIGH per tier composition.
10. **Anti-claims empty until Tier 2.** Log the gap; don't simulate.
11. **Warning header until validated.** Notion subpage titles prefixed `⚠️ v0.1 — public sources only` until Tier 2 closes the anti-claims gap and Evidence levels rise.

---

## 7. Handoff to downstream skills

This skill's outputs are consumed by separate skills (not this one):

- **Listbuilding skill** consumes segment example companies + role title variants + antiprofile.
- **Sequence-writing skill** consumes Value Artifacts (pain relievers / gain creators / features) + role VPC praise/punishment + Tone of Voice + anti-claims.
- **Qualification skill** consumes segment definitions + exclusions + role antiprofiles.

If a downstream skill needs information not in these outputs, the gap comes back to this skill — never patched ad-hoc downstream.

---

*Outrizz Delivery | v2.0 — 2026-05-14*
