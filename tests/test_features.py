import os
import tempfile

import numpy as np
import h5py
import pytest

from paat import io, features

TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/10min_recording.gt3x')


@pytest.fixture
def data():
    return io.read_gt3x(FILE_PATH_SIMPLE, rescale=True, pandas=True)


def test_actigraph_counts(data):
    counts_1s = features.actigraph_counts(data, 100, 1)
    counts_10s = features.actigraph_counts(data, 100, 10)
    counts_1min = features.actigraph_counts(data, 100, 60)


def test_brond_counts(data):
    brond_counts = features.brond_counts(data[["Y", "X", "Z"]].values.T, 100, 1)
