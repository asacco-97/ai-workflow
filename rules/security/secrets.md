---
description: Secret and credential handling rules. Always on.
---

# Secrets

- Never write API keys, access tokens, passwords, or credentials in code, config files, notebooks, or memory files.
- Use environment variables for local secrets. Use a secrets manager (AWS Secrets Manager, Vault) for production.
- Ensure `.env` is in `.gitignore` before any other work. Do not commit `.env` files.
- Run `security-privacy-reviewer` before every PR to catch accidental credential exposure.
- If a secret is accidentally committed, treat the credential as compromised immediately — rotate it before attempting to clean the git history.
