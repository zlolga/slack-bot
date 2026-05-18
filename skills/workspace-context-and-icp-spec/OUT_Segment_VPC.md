# Segment VPC — `<Client> — <Segment Name>`
*One file per promoted segment. Filename: `<Client>_Segment_<Name>_VPC.md` in `02_outputs/`.*

Value Proposition Canvas at the segment (organization / buying-unit) level. Pair with the role-level VPCs in `<Client>_Role_<Name>_VPC.md`.

---

## 0. Segment header

**Segment name:** [Name]

**One-line definition:** [active voice, specific enough that a listbuilder downstream can sanity-check a company against it]

**Why this is a distinct segment (vs adjacent ones):** [1–2 sentences]

**Roles inside this segment:**
- Champion: [role] → see `<Client>_Role_<role>_VPC.md`
- Decision Maker: [role] → see `<Client>_Role_<role>_VPC.md`
- Influencer: [role] → see `<Client>_Role_<role>_VPC.md`

---

## 1. Customer Profile (the segment's reality)

### 1.1 Jobs — what they're trying to get done

Three categories. List 3–6 items each; mark `[F]` functional, `[S]` social, `[E]` emotional.

- [F] [job 1] — Source: [URL]
- [S] [job 2] — Source: [URL]
- [E] [job 3] — Source: [URL]

### 1.2 Pains — bad outcomes, obstacles, risks

What gets in the way of the jobs, what they already hate, what they fear.

- [pain 1] — Source: [URL or `INT_Voice_Quotes.md` §pain]
- [pain 2]
- …

Rule: pull from real customer-side reviews / case studies / pain quotes where possible. Generic marketing pains don't qualify.

### 1.3 Gains — outcomes they want, benefits they expect

What they'd celebrate. What "good" looks like for this segment.

- [gain 1] — Source: [URL]
- [gain 2]
- …

---

## 2. Value Map (the client's offering, for this segment)

### 2.1 Pain Relievers — how the product alleviates the specific pains in §1.2

Each reliever points back to a numbered pain.

- Relieves Pain #1 by: [mechanism / capability] — Backed by feature: [feature name in `INT_Product_Facts.md`]
- Relieves Pain #2 by: …
- …

### 2.2 Gain Creators — how the product produces the gains in §1.3

- Creates Gain #1 by: [mechanism / capability] — Backed by feature: …
- Creates Gain #2 by: …
- …

### 2.3 Products & Services — features that deliver the relievers / creators above

Pull from `INT_Product_Facts.md`. Only the features relevant to *this* segment.

| Feature / service | Source | Maps to (Relievers / Creators) |
|---|---|---|
| | INT_Product_Facts | Reliever #1, Creator #2 |
| | | |

---

## 3. Fit profile (for downstream listbuilding handoff)

Not a listbuilding spec — just the signals a listbuilder will need.

- **Observable structural signals:** [size band / sector / multi-site / etc.]
- **Observable behavioral signals:** [hiring patterns / press signals / hours / customer mix]
- **Closed-gap competitors** (segments where our value is already covered): [list with reason]

---

## 4. Example companies

| Company | Verdict | Why |
|---|---|---|
| | fit / borderline / exclude | one-line reason |

≥5 `fit` from public research. If you can't reach 5 — segment is hypothetical → Open Questions in master `Workspace_Context.md` §6.

---

## 5. Open questions specific to this segment

| Question | Resolution path |
|---|---|

---

*Segment owner: [name] | Evidence: Tier [0/1/2] | Last validated: [date]*
