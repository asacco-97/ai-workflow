---
description: State modeling assumptions explicitly before or alongside code.
---

# Modeling assumptions

Before or alongside any modeling code, state:

- **Target definition** — exactly how the target variable is computed, from which table, and over what time window.
- **Feature-to-target timing** — confirm that all features are available at the prediction point in time (no look-ahead).
- **Population scope** — which entities are in scope and which are excluded, and why.
- **IID assumption** — whether observations can be treated as independent. If not, note the dependency structure (e.g., repeated measures, geographic clustering).
- **Stationarity** — for time-series models, whether the process is assumed stationary and over what window.

Assumptions are not optional. If you cannot state them, do not train the model.
