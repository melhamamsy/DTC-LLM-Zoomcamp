from prefect import flow, task
import pytest
from prefect.testing.utilities import prefect_test_harness

@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield

@task
def my_favorite_task():
    return 42

@flow
def my_favorite_flow():
    val = my_favorite_task()
    return val

def test_my_favorite_flow():
    assert my_favorite_flow() == 42

def test_my_favorite_task():
    assert my_favorite_task.fn() == 42