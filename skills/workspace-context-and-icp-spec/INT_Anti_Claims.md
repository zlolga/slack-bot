# INT — Anti-Claims
*Stage 2. Every "do not say X" with source and reason.*

Default state on Tier 0 runs: empty except for the gap meta-entry. That's expected — anti-claims usually live in Tier 2 materials (meeting notes, interviews) we don't have yet.

---

## Rule

An anti-claim only goes here with a citation. Sources by tier:

- **Tier 0:** very rare. Occasionally About / FAQ pages have explicit "we are not…" statements.
- **Tier 1:** founder LinkedIn posts where they correct framing ("we keep getting called X — we're actually Y").
- **Tier 2:** the main source — interviews, meeting notes, internal positioning docs.

If none exist, log the meta-entry below.

---

## Meta-entry (default for Tier 0 runs)

```
- **GAP:** Anti-claims not collected — Tier 0 only (no founder posts mined and no client-provided meeting notes or interviews).
  - Risk: outreach may include framings the client has rejected internally.
  - Mitigation: final sequence draft reviewed with client before launch.
  - Removal trigger: this entry is removed when Tier 2 inputs arrive AND `INT_Anti_Claims.md` has ≥3 real entries, OR client signs off after reviewing draft.
```

Surfaced in `OUT_Project_Context.md` §9 as Editorial Decision #1 on Tier 0 deliveries.

---

## Entry format (when sources exist)

```
- **DO NOT:** [forbidden language / claim / framing]
  - Why: [reason]
  - Source: "[verbatim quote]" — [URL or file], [date] | tier: 1/2
  - Applies to: [Email 1 / all emails / LinkedIn / all channels]
  - Replacement: [what to say instead]
```

---

## Common categories

- Words/labels to avoid.
- Number/claim sequencing rules.
- Brand / competitor mention rules.
- Tone / register bans.
- Channel-specific bans.
