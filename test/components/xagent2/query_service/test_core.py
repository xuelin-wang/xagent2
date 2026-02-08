from __future__ import annotations

import pytest

from xagent2.query_service.core import Query, answer_query


def test_answer_query_echoes_text():
    result = answer_query(Query(text="hello"))
    assert result.text.startswith("Echo:")


def test_answer_query_rejects_empty():
    with pytest.raises(ValueError):
        answer_query(Query(text="   "))
