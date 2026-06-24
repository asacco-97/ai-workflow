---
description: Training runs must be reproducible given the same config and data.
---

# Reproducibility

- Set random seeds explicitly for all stochastic components (numpy, random, PyMC/JAX sampler, sklearn splitters). Log the seed to MLflow.
- Pin dependency versions in `requirements.txt` or `pyproject.toml`. No unpinned `>=` constraints for modeling libraries.
- Data preprocessing steps must be deterministic. If a step is stochastic, the seed must be fixed and logged.
- The config file used for a run is an artifact. Keep it so any run can be reproduced from its MLflow entry.
- If a run cannot be reproduced from its MLflow entry and config, treat it as unreliable.
