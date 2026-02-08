# Development Project

This directory is the development project: a dedicated place for working with
the whole codebase in one environment (REPL, notebooks, quick scripts). It is
separate from production projects under `projects/`.

What belongs here:
- Scratch Python modules for experiments or spike code.
- Notebooks for exploration or demos.
- One-off scripts or helpers that are useful during development.

What does not belong here:
- Production code. Put that in `components/` or `bases/`.
- Project-specific deployment artifacts (those belong under `projects/`).

Notes:
- There are no required files in this directory.
- Workspace-level dependencies live in the root `pyproject.toml`.
