# xagent2

This repository is a Python Polylith workspace generated from the official
Python Polylith documentation.

Workspace layout:
- `components/` holds core business logic (reusable, deployment-agnostic).
- `bases/` wires components into runnable entry points.
- `projects/` defines deployable artifacts (apps, services, packages).
- `development/` is the dev project for experiments, REPL work, and notebooks.

See the folder-level READMEs for more detail.

Workspace tooling files:
- Root `pyproject.toml` defines the workspace-level Python environment used for
  local development (shared dependencies, build wiring for workspace sources,
  and test settings).
- Root `uv.lock` is the lockfile for that root environment. It pins resolved
  dependency versions so installs are reproducible across machines/CI.
- `development/` is still useful for dev-only code artifacts (scratch modules,
  notebooks, helper scripts), while environment/dependency management stays at
  the root.

Polylith docs (architecture, language-agnostic):
```text
https://polylith.gitbook.io/polylith
https://polylith.gitbook.io/polylith/architecture/2.1.-workspace
https://polylith.gitbook.io/polylith/architecture/2.2.-base
https://polylith.gitbook.io/polylith/architecture/2.3.-component
https://polylith.gitbook.io/polylith/architecture/2.4.-development
https://polylith.gitbook.io/polylith/architecture/2.6.-project
```
