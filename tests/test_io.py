import os

import numpy as np

from paat import io

TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/test_file.gt3x')

def test_read_gt3x():
    time, acceleration, meta = io.read_gt3x(FILE_PATH_SIMPLE)
