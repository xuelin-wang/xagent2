from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Query:
    text: str


@dataclass(frozen=True)
class Answer:
    text: str
    created_at: datetime


def answer_query(query: Query) -> Answer:
    """
    Dummy "answer" generator for a user query.
    In a real system this could call a search index or an LLM.
    """
    normalized = query.text.strip()
    if not normalized:
        raise ValueError("query text cannot be empty")
    reply = f"Echo: {normalized}"
    return Answer(text=reply, created_at=datetime.now(timezone.utc))
