# WorkflowPermissionReview

Review selected token permissions and triggers in an owner-supplied GitHub Actions workflow. It runs locally, does not contact targets, and reports review prompts instead of exploit instructions.

## Input and checks

- Input: GitHub Actions YAML from a system you own or are authorized to inspect.
- Checks: Missing explicit permissions, write scopes and pull_request_target triggers.
- Output: rule, local location and short note. No source snippets, credential values or log identities are printed.

## Run

```sh
python -m pip install -r requirements.txt
python cli.py ./owned-input
python cli.py ./owned-input --json
python -m unittest discover -s tests -v
```

Exit code 0 means no findings, 1 means review findings, 2 means invalid input or read failure. A clean result is not a security guarantee. The input file is read through a bounded regular-file descriptor with a 4 MiB limit.

## Boundaries

The tool does not execute a workflow or resolve reusable workflows, repository settings, action code or effective token permissions. Work only on local, authorized inputs. The analysis does not send data to a service or modify the inspected files.

## Source and policy context

- Technical reference: https://docs.github.com/en/actions/reference/security/secure-use
- See [ORIGIN.md](ORIGIN.md) for implementation provenance and [VALIDATION.md](VALIDATION.md) for checks performed.
- CVP eligibility depends on a real, legitimate defensive task affected by Claude's cyber safeguards and the applicant's organization/identity review; this repository alone does not establish eligibility or approval. [Anthropic CVP guidance](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet).

## Reviewed input behavior

Event names are preserved as strings, duplicate YAML mapping keys are rejected, and malformed trigger/permission values are errors. Jobs with explicit permissions do not receive an implicit-default prompt merely because the workflow has no root declaration.
