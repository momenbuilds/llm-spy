from __future__ import annotations

import pytest

from llmspy.storage import Storage


@pytest.fixture()
def store(tmp_path):
    return Storage(tmp_path / "test.db")
