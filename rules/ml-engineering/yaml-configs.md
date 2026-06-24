---
description: Hyperparameters and training config live in YAML, not hardcoded in scripts.
---

# YAML configs

- All hyperparameters, data paths, split parameters, and training settings live in a YAML config file. No magic numbers in scripts.
- Config files are versioned in the repo alongside the code that uses them.
- Use `/yaml-config-designer` to scaffold the config schema for a new model.
- The config file path is logged as an MLflow parameter or artifact on every run.
- Config files must not contain secrets, passwords, or connection strings. Use environment variables or a secrets manager for credentials.
