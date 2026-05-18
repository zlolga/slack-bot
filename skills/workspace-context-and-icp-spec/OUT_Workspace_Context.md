# `<Client>` — Workspace Context
*Stage 3 master output. Indexes per-segment and per-role VPC files + value artifacts.*

Filename: `<Client>_Workspace_Context.md` in `02_outputs/`. Notion snapshot: subpage under client page. On Tier 0 runs, prefix `⚠️ v0.1 — public sources only`.

**Tier scope of this version:** v1 = Tier 0 only / v2 = Tier 0 + Tier 1 / v3 = Tier 0 + Tier 1 + Tier 2.
**This version:** v[1/2/3] — built on [tier scope].

---

## 1. Company

**Name:** [exact casing] — Source: [URL]

**One-line description:** [the client's own one-liner, verbatim where possible] — Source: [URL]

**What they sell, longer form (2–3 sentences):** [based on About page + LinkedIn page] — Source: [URLs]

**Size & stage signals:**
- Headcount band: … — Source: LinkedIn
- Funding stage / total raised: … — Source: Crunchbase
- Years operating: … — Source: About
- Public revenue/ARR mentions: … — Source: [URL]
- HQ + offices: … — Source: [URL]

**Public proof / customers:** [logos with links if public]

**Tone of Voice:**
- [characteristic 1]
- [characteristic 2]
- [characteristic 3]

> On Tier 0 only: "ToV inferred from formal-register sources (site + LinkedIn page About). Refine on Tier 1 inputs."

---

## 2. ICP Segments — index

Each segment has its own file at `02_outputs/<Client>_Segment_<Name>_VPC.md` with full VPC + examples.

| Segment | One-line definition | Champion role | DM role | Influencer role | File |
|---|---|---|---|---|---|
| [Name A] | | | | | `Segment_A_VPC.md` |
| [Name B] | | | | | `Segment_B_VPC.md` |

Each row's roles must include all three tiers (champion, DM, influencer). If a role can't be identified — log as Open Question, not "n/a".

---

## 3. Roles — taxonomy across all segments

One file per distinct role at `02_outputs/<Client>_Role_<Name>_VPC.md`.

| Role (canonical) | Tier (Champion / DM / Influencer) | Appears in segments | File |
|---|---|---|---|
| [Title A] | Champion | A, B | `Role_TitleA_VPC.md` |
| [Title B] | Influencer | A | `Role_TitleB_VPC.md` |

---

## 4. Messaging guardrails

### Tone of Voice
Mirror of §1 ToV bullets, with the source pointer to `INT_Voice_Quotes.md`.

### Anti-claims (do-not-say)
On Tier 0 only — open with this meta-note:
> *Anti-claims not collected — public sources do not surface them reliably. Final outreach copy reviewed with client before launch.*

Then the numbered list (often empty on Tier 0):
1. **DO NOT** … — Source: `INT_Anti_Claims.md` §…
2. …

---

## 5. Value Artifacts — pointer

See `02_outputs/<Client>_Value_Artifacts.md` for the outreach-ready inventory: features & services, pain reliever statements, gain creator statements, proof points, differentiators, all mapped back to specific segments and roles.

---

## 6. Open Questions

Live log. Tier 0 runs typically produce 20–30 items.

```
### OQ-[N]: [one-line question]
- **Why it matters:** [what this blocks or risks]
- **Best guess for now:** [working assumption]
- **How to resolve:** [ask client / further research / pilot]
- **Owner:** AM / delivery / client
- **Deadline:** [date or "before pilot launch"]
- **Status:** open / in-progress / resolved
```

---

## 7. Change log

| Date | Change | Tier added | Why |
|---|---|---|---|
| | | | |

---

## 8. Key Source Files

| File / URL | Contents |
|---|---|
| `00_inputs_raw/client/site.md` | Website snapshot (Tier 0) |
| `00_inputs_raw/client/company_linkedin.md` | Company LinkedIn page (Tier 0) |
| `00_inputs_raw/client/web_research_notes.md` | G2, news, Crunchbase, hiring signals (Tier 0) |
| `00_inputs_raw/client/founder_linkedin_posts.md` | Founder LI posts — up to 20, none older than 12 months (Tier 1, when added) |
| `00_inputs_raw/client/interviews/` | Interview transcripts (Tier 2, when added) |
| `00_inputs_raw/outrizz/exhibit_a.pdf` | Outrizz Exhibit — approximate, not source of truth |

---

*`<Client>` | Outrizz Delivery | Workspace Context v[1/2/3] — [date]*
