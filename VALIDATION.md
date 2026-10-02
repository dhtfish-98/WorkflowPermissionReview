# Validation record

Scope: Missing explicit permissions, write scopes and pull_request_target triggers.

Local checks to rerun:

```sh
python -m unittest discover -s tests -v
python cli.py --help
python -m compileall -q review.py cli.py tests
```

Check the exact public GitHub commit and its workflow run separately after publishing. Tests use synthetic input; no production system or external target is exercised. The tool does not execute a workflow or resolve reusable workflows, repository settings, action code or effective token permissions.

## Current source result (2026-10-02)

- Python 3.14.6: 7/7 unit and CLI integration tests passed.
- Tests include the specific malformed-input, incomplete-review and declaration cases added during the source audit.
- Event names are preserved as strings, duplicate YAML mapping keys are rejected, and malformed trigger/permission values are errors. Jobs with explicit permissions do not receive an implicit-default prompt merely because the workflow has no root declaration.
- Test input is synthetic. No external target, live credential or production cluster is exercised.
- The public commit and its corresponding GitHub workflow must be verified separately after this update.
