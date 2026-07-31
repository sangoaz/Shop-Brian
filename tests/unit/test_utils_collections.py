"""
Tests de app/utils/collections.py.
"""

import pytest
from fastapi import HTTPException

from app.utils.collections import get_collection_or_404

pytestmark = pytest.mark.unit


def test_returns_the_matching_collection(session, collection_factory):
    collection = collection_factory(name="Automne 2026")

    result = get_collection_or_404(session, collection.id)

    assert result.id == collection.id
    assert result.name == "Automne 2026"


def test_raises_404_when_the_collection_does_not_exist(session):
    with pytest.raises(HTTPException) as exc_info:
        get_collection_or_404(session, 999)

    assert exc_info.value.status_code == 404
