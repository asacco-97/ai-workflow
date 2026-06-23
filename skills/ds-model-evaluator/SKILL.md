---
name: ds-model-evaluator
description: "Review and evaluate a data science model, modeling plan, or ML design document across four pillars — data quality & leakage, model framework, validation strategy, and feasibility. ALWAYS use this skill when the user: asks to review or check a model, notebook, or script; mentions a train/test gap or unexpected metrics; asks whether their CV or split is correct; asks about data leakage or look-ahead bias; shares a design or architecture doc for an ML system; wants a sanity check before presenting or shipping; asks if a Bayesian model's priors, pooling, or diagnostics look right. Invoke proactively when the user shares model code, a notebook path, or a design doc without explicitly asking for review — they almost always want one. Works on scripts, notebooks, design docs, or verbal descriptions; will ask targeted questions if context can't be determined from the file."
---

# Data Science Model Evaluator

Evaluate a modeling approach or implementation for correctness, soundness, and feasibility before work continues.

## Step 1: Identify Input Type and Establish Context

This skill handles three input types. Identify which one you have — it changes what you read and what questions you ask.

**A. Architecture or design document** (e.g., a spec, design doc, PRD, or written modeling plan)
- Read the document fully before doing anything else
- The review is design-level: evaluate decisions, flag underspecified areas, and ask about anything left open
- You do not have code to audit, so focus on whether the described approach is sound and complete

**B. Script or notebook** (e.g., `.py`, `.ipynb`, `.R`, Stan/PyMC model file)
- Read the file and scan for: data loading paths, feature construction, train/test split logic, model definition, and evaluation code
- Infer domain, data structure, and model type from the code where possible
- **If any of the three required context items (domain, data structure, model type) cannot be determined from the code, ask the user — one question at a time — before proceeding.** Common gaps in scripts: no comments on what the target means, data loaded from a path with no schema, model type obvious but business context unclear.
- Also ask about anything that's a config placeholder or hardcoded value that changes the review (e.g., `TEST_SIZE = 0.2` with no comment on why, or a prior written as `Normal(0, 10)` with no justification).

**C. Verbal description or no file** (user describes the setup in their message)
- Work from what's provided and ask for the three required context items if missing

---

### Required context (all three needed before reviewing)

You need three things before beginning the four-pillar review: **domain**, **data location/structure**, and **model type**.

For each one you cannot determine from the input, ask the user directly — one question at a time:

- Domain (e.g., finance, healthcare, e-commerce, operations, scientific research)?
- Data: what does it look like — shape, key columns, target variable?
- Model type: classification, regression, time series forecasting, clustering, ranking, anomaly detection, Bayesian estimation, or something else?

Don't begin the four-pillar review until all three are known.

---

## Step 2: Four-Pillar Review

Work through each pillar in order. Leakage is the most dangerous failure mode — treat it as a blocker when found.

---

### Pillar 1: Data & Leakage

The goal: confirm the model can only see information that will be available at prediction time.

**Target leakage** — does any feature encode the target (directly or through a proxy)?
- Watch for features derived from the target, collected after the event, or representing the same construct under a different name.

**Temporal leakage** — for any time-structured data, does the split respect chronological order?
- Is the train/test boundary a point in time, not a random sample?
- Are lag features, rolling statistics, or time-based aggregations computed without crossing the split?

**Preprocessing leakage** — is any transformation (scaling, encoding, imputation, PCA) fit on the full dataset before splitting?
- This contaminates the test set with information from test rows. Preprocessing must be fit on training data only.

**Feature construction leakage** — are any features computed using knowledge of what happens in the future relative to the prediction point?

**Proxy/identifier leakage** — are timestamps, IDs, zip codes, or other near-identifiers included that correlate with the target for reasons unrelated to the signal?

**Population mismatch** — is the training population representative of the population the model will score on? Watch for survivorship bias, sample selection, or temporal distribution shift.

---

### Pillar 2: Model Framework

Check whether the algorithm family and configuration match the problem structure.

- Is the algorithm appropriate for the feature types (numeric, categorical, text, image) and target type?
- **Time series**: is the model respecting temporal structure, or treating rows as exchangeable? Standard tree/linear models applied naively to time series often fail here.
- **Clustering**: is the distance metric appropriate for the feature space? Is the number of clusters principled or arbitrary?
- **Classification**: is the decision threshold considered separately from model training? Accuracy is often a misleading metric.
- Is model complexity matched to sample size? A deep model on 500 rows is a red flag; a linear model on a highly non-linear problem is another.
- Is there a simpler baseline the model should be compared against (mean predictor, heuristic rule, last-value carry-forward)? If not, it's impossible to know whether the model is adding value.
- Are hyperparameters tuned, or sitting at framework defaults?

**If the model is Bayesian (PyMC, Stan, NumPyro, Bambi, etc.), evaluate these additional concerns:**

- **Likelihood specification**: does the chosen likelihood match the data-generating process? (e.g., Binomial for count/total data, NegativeBinomial for overdispersed counts, StudentT for heavy-tailed residuals). A misspecified likelihood produces valid-looking inference on the wrong model.
- **Priors on parameters**: are priors weakly informative on a meaningful scale, or are they effectively flat? Flat priors (e.g., `Normal(0, 10)` on a logit scale, or `Uniform(0, 1)` on a rate with little data) can produce posteriors that are dominated by the prior's tails and fail to regularize small-data groups.
- **Prior predictive check**: was a prior predictive check run before fitting? Simulating from the prior reveals whether it produces plausible data ranges before any observations are seen. Skipping this means the prior's implications are unknown.
- **Pooling structure**: given grouped/hierarchical data, is the pooling choice justified?
  - *No pooling* (separate model per group) ignores shared information and fails for small groups.
  - *Complete pooling* (single shared parameter) ignores group-level variation.
  - *Partial pooling* (hierarchical prior) borrows strength across groups proportional to data sparsity — typically the right default when group sizes vary widely.
- **Posterior predictive check**: does the posterior predictive distribution cover the observed data? Systematic misfit (wrong variance, wrong skew, zero-inflation) indicates model misspecification.
- **MCMC diagnostics**: are R-hat values < 1.01, ESS (bulk and tail) sufficient, and divergences near zero? High divergences signal geometry problems that invalidate the posterior. Check trace plots for chains that haven't mixed.
- **Identifiability**: are there parameter combinations that produce the same likelihood? The most common case in hierarchical models is a global intercept `α` plus group intercepts `α_g` — the likelihood sees only their sum `α + α_g`, so any constant can slide between them without changing predictions. This creates a flat ridge in the posterior that causes slow mixing, low ESS, and unreliable parameter-level interpretation. Standard fixes: (1) sum-to-zero constraint (`ZeroSumNormal` in PyMC, `sum_to_zero_vector` in Stan), (2) reference-level parameterization (fix one group intercept to 0), or (3) a true hierarchical prior `α_g ~ Normal(μ_α, σ_α)` with hyperpriors — the cleanest solution because it resolves the geometry implicitly while enabling partial pooling. Other identifiability traps: multiplicative terms not anchored to a scale, variance parameters that can trade off against one another.

---

### Pillar 3: Validation Strategy

Check whether the evaluation procedure will produce trustworthy estimates of real-world performance.

**Holdout integrity** — is there a true held-out test set that was never touched during model development or selection?

**Cross-validation appropriateness**:
- Time series → walk-forward or time-blocked CV. Shuffled k-fold on time series is a leakage vector.
- Grouped/panel data → group k-fold so the same entity doesn't appear in both train and validation folds.
- Imbalanced classification → stratified k-fold to preserve class ratios.

**Metric alignment** — do the reported metrics map to the business decision?
- For imbalanced classification: precision-recall curves or F1 over accuracy.
- For regression: is RMSE appropriate, or does MAE or MAPE better reflect the loss function?
- For forecasting: are metrics computed per-horizon or aggregated in a way that obscures forecast decay?
- For ranking/retrieval: precision@k, NDCG.

**Baseline comparison** — is there a naive model to benchmark against? If the model can't beat a simple heuristic, the data may not contain the expected signal.

**Preprocessing inside CV** — is preprocessing re-fit inside each fold, or once on the full training set? Fitting outside the CV loop is leakage.

---

### Pillar 4: Feasibility Given Data

Check whether the approach is viable given what's actually available.

- **Sample size**: does the dataset have enough rows to support the model complexity? A rough guide: linear models need ~10–20 observations per feature; tree-based models are more flexible but still need sufficient samples per leaf; neural nets generally need far more. Under-powered setups will show strong in-sample performance and weak generalization.
- **Class imbalance** (for classification): what's the imbalance ratio? At severe imbalance (>20:1), standard training objectives may produce a model that predicts the majority class for everything.
- **Signal presence**: is there a plausible mechanism by which the features predict the target? Has any exploratory analysis confirmed signal exists, or is this speculative?
- **Missing data**: are missings systematic (not at random) rather than random? If so, simple imputation may introduce bias. The missingness pattern itself may be informative.
- **Feature-to-sample ratio**: is the number of features large relative to the sample size? High dimensionality with few samples is a recipe for overfitting.
- **Distribution shift**: is the training window representative of the deployment window? Seasonality, trend, or regime changes can make historical training data misleading.
- **Data freshness**: how recent is the training data? For models that will score on current or future data, stale training data is a risk.

---

## Step 3: Output Format

Structure your review using the following sections. Be specific — name the exact file, function, or line where issues appear when reviewing code.

---

## Verdict
`Ready` / `Needs fixes` / `Not ready` — one line with a one-sentence reason.

## Blocking issues
Issues that must be resolved before results can be trusted (leakage, validation contamination, fundamental framework mismatch). If none, say "None."

## Risks & concerns
Non-blocking issues worth addressing. Organize by pillar: Data, Framework, Validation, Feasibility.

## Recommended next steps
3–5 concrete, prioritized actions specific to this model and dataset.

## Pair with /grill-me
If key modeling decisions are unresolved (algorithm choice, feature engineering approach, target definition, deployment constraints), note them here and suggest the user run `/grill-me` on the modeling plan to stress-test those decisions before continuing.

---

## Calibration guidance

- **Design/architecture doc**: evaluate decisions and flag underspecified areas — don't invent implementation details that aren't there. Ask about open questions explicitly.
- **Script or notebook**: quote specific lines, cells, or function names when calling out issues. If you had to ask clarifying questions before reviewing, note which answers most affected your findings.
- **Verbal description**: be explicit about what you assumed vs. what was stated. Flag assumptions that, if wrong, would change the verdict.
- Prioritize issues by impact on model reliability, not completeness of coverage. A review with three sharp findings is more useful than a list of twenty minor concerns.
- If reviewing a model type outside your domain (e.g., survival models, causal inference, reinforcement learning), say what you're uncertain about rather than guessing.
