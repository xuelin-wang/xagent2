# Bases

Bases define how the system is delivered (entry points and runtime wiring).
They assemble components into runnable applications, services, or executables.

What belongs here:
- Entry points (CLI, web server, worker, etc.).
- Composition code that wires components together.
- Thin runtime configuration and integration glue.

What does not belong here:
- Business logic (put that in `components/`).
- Shared libraries used across many bricks (those are components).
