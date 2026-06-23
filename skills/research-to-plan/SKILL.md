---
name: research-to-plan
description: "Turn a fuzzy problem statement or research question into a concrete, actionable implementation plan. Use this skill when the user wants to: explore solution options before committing code, produce a scoped plan for a modeling or pipeline task, investigate trade-offs between approaches, or convert a stakeholder ask into technical steps. Trigger when the user says 'research how to', 'what's the best way to', 'help me plan', 'I need to figure out', or describes a problem without a clear implementation path yet."
---

# Research to Plan

Convert a vague problem or question into a scoped, sequenced implementation plan the user can execute or hand off.

## When to Use

- User has a problem but no clear approach yet
- Multiple technical options exist and trade-offs need surfacing
- A stakeholder ask needs decomposing into engineering steps
- User wants a plan before writing any code

Do **not** use this skill if the user already has a clear approach and just needs implementation help. Jump straight to coding in that case.

---

## Step 1: Problem Framing

Before researching anything, establish a shared understanding of the problem. If the user's message is ambiguous on any of these, ask — one question at a time:

1. **What decision or outcome does this plan need to unlock?** (e.g., "ship a churn model to production", "replace manual feature engineering with an automated pipeline")
2. **What constraints are fixed?** (data already collected, framework already chosen, deadline, team size)
3. **What's the acceptable scope?** (POC only, full production, v1 with room to iterate)
4. **What does success look like?** (specific metric, behavior, deliverable)

Do not proceed to research until you have a clear problem statement that names: the outcome, the constraints, and the success criterion.

---

## Step 2: Option Space Mapping

Identify 2–4 plausible approaches. For each, state:

- **What it is** — one sentence
- **Key trade-off** — the main reason to choose it vs. the alternatives
- **When it breaks down** — the condition under which this approach fails
- **Estimated effort** — rough order of magnitude (hours / days / weeks)

Present the options in a table before recommending. Do not jump to a recommendation without laying out the space first.

**Format:**

| Approach | Trade-off | Fails when | Effort |
|----------|-----------|------------|--------|
| ... | ... | ... | ... |

---

## Step 3: Recommendation

State a single recommended approach and explain why in 2–3 sentences. Reference the user's specific constraints. If the recommendation depends on something you don't know (e.g., data volume, team skill), state the condition explicitly: "If X, go with A; if Y, go with B."

---

## Step 4: Implementation Plan

Produce a sequenced step list. Each step must have:

- A **verb + noun** label (e.g., "Profile training data", "Validate feature pipeline")
- A **verify** check — a concrete observable outcome that confirms the step is done
- A **dependency** note if the step can't start until another is complete

**Format:**
```
1. [Step name]
   - verify: [what you check to confirm it's done]
   - depends on: [step N, if applicable]

2. [Step name]
   - verify: [...]
```

Aim for 5–10 steps. If more than 10 are needed, group into phases.

---

## Step 5: Open Questions and Risks

List 2–5 things that could derail the plan that the user should resolve before starting:

- Missing information (data not yet available, schema unknown)
- Assumptions that need validation (expected signal may not exist)
- External dependencies (AWS access, stakeholder approval, another team's API)

---

## Output Artifacts

After running this skill, the user should have:

| Artifact | Path | Purpose |
|----------|------|---------|
| Implementation plan (this conversation) | — | Paste into ticket or doc |
| Options table | — | Reference when revisiting trade-offs |
| Open questions | — | Prioritize before sprint starts |

If the plan is substantial (>7 steps), offer to write it to `docs/plans/<slug>.md` for persistence.

---

## Quality Gates

Before delivering the plan:

- [ ] Problem statement is specific enough to evaluate if the plan succeeded
- [ ] At least 2 options were considered (even if one was immediately dismissed)
- [ ] Every step has a verify check
- [ ] Open questions are enumerated, not left implicit

---

## Common Failure Modes

- **Jumping to a specific tool before framing** — if you name a library before the problem is stated, you've skipped the option space and may be anchoring the user to a suboptimal choice
- **Steps without verify checks** — unverifiable steps create ambiguity about when the project is done
- **Ignoring constraints** — a perfect technical plan that ignores the user's real constraints (timeline, existing stack) wastes time
- **Over-scoping** — plans with 20 steps that try to solve everything at once never get started

---

## Example Invocation

```
/research-to-plan

I need to build a churn model for our SaaS product. We have 18 months of event logs 
in Redshift, about 50k accounts. The model needs to score accounts weekly and surface 
top-10 at-risk accounts to the CS team. No ML infrastructure exists yet.
```

Expected output: framing confirmation, options table (e.g., logistic regression vs. gradient boosting vs. survival model), recommended approach, 8-step plan, 3 open questions.
