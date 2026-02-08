# Components

Components contain the core business logic. They are designed to be reusable
and have no knowledge of how the system is deployed.

What belongs here:
- Domain logic, application services, and core rules.
- Data access logic that is independent of a specific deployment context.
- Reusable utilities that represent meaningful business concepts.

What does not belong here:
- Entry points or wiring (put those in `bases/`).
- Project-specific configuration or deployment artifacts.
