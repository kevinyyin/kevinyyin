import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)  # tests use repo-relative paths (profile/, data/)


@pytest.fixture
def contrib():
    with open(os.path.join(ROOT, "tests", "fixtures", "contributions.json")) as f:
        return json.load(f)
