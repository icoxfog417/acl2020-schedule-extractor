import os
import pytest


@pytest.fixture(scope="class")
def path_to_anthology(request):
    path = os.path.join(os.path.dirname(__file__), "data/2020.acl-main.0.pdf")
    request.cls._path = path
