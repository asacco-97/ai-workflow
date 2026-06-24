---
description: Rules for Bayesian and probabilistic modeling.
---

# Bayesian modeling

**Before specifying a model:**
- State the prior for each parameter and justify it (domain knowledge, literature, or weakly informative).
- State the likelihood and why it matches the data-generating process.
- Document the hierarchical structure if applicable: what is pooled, what is not, and why.

**During sampling:**
- Always run at least 2 chains. Confirm R-hat < 1.01 and ESS > 400 for all parameters of interest.
- Check divergences. If divergences exceed 0.1% of post-warmup draws, the model geometry is problematic — do not proceed without addressing it.
- Run prior predictive checks before conditioning on data.
- Run posterior predictive checks after sampling.

**Reporting:**
- Report posterior means or medians with 89% or 95% credible intervals — not just point estimates.
- If comparing models, use LOO-CV (`az.compare`) not WAIC alone.
- Use `bayesian-reviewer` for a second opinion on priors, pooling decisions, and diagnostics.
