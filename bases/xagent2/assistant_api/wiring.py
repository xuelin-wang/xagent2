from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from xagent2.identity.core import IdentityConfig, IdentityService
from xagent2.query_service.core import answer_query
from .adapters import (
    InMemorySessionStore,
    InMemoryUserRepo,
    SimplePasswordHasher,
    UtcClock,
    UuidLikeIdGenerator,
)


from typing import Callable


@dataclass(frozen=True)
class Container:
    identity: IdentityService
    answer_query: Callable


def build_container() -> Container:
    # In-memory skeleton wiring. Swap these adapters later (Postgres/Redis/etc.)
    users = InMemoryUserRepo()
    sessions = InMemorySessionStore()
    hasher = SimplePasswordHasher()
    ids = UuidLikeIdGenerator()
    clock = UtcClock()
    cfg = IdentityConfig()

    identity = IdentityService(
        config=cfg,
        users=users,
        sessions=sessions,
        hasher=hasher,
        ids=ids,
        clock=clock,
    )
    return Container(identity=identity, answer_query=answer_query)
