import os

import pytest

from paat import io


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope="module")
def test_root_path():
    return os.path.join(os.path.pardir, os.path.dirname(__file__))


@pytest.fixture(scope="module")
def file_path(test_root_path):
    return os.path.join(test_root_path, 'resources/10min_recording.gt3x')


@pytest.fixture(scope="module")
def load_gt3x_file(file_path):
    return io.read_gt3x(file_path, rescale=True, pandas=True)
