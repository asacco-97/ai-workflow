---
description: AWS-aware patterns for ML engineering.
---

# AWS

**Credentials:**
- Never hardcode AWS credentials. Use IAM roles (instance profiles, ECS task roles) in compute environments. Use `~/.aws/credentials` or environment variables locally — never in code.
- Do not log boto3 session credentials, presigned URLs, or bucket paths containing account IDs to MLflow or memory files.

**Data access:**
- Prefer reading from S3 with versioned object keys or dataset manifests. Avoid `s3://bucket/latest/` paths — "latest" is ambiguous and breaks reproducibility.
- Before writing to S3 in a pipeline, confirm the destination bucket and prefix with the user.

**Compute:**
- Log the instance type and region to MLflow when running on AWS compute.
- If using SageMaker, log the training job name and S3 output path as MLflow tags.
