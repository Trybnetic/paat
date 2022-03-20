"""
PAAT - Physical Activity Analysis Toolbox
=========================================

The physical activity analysis toolbox (PAAT) is a comprehensive toolbox to
analyze raw acceleration data. We developed all code mainly for analyzing
ActiGraph data (GT3X files) in large sample study settings where manual annotation
and analysis is not feasible.

"""

import os
import sys
from importlib import metadata

from pip._vendor import pkg_resources
import toml

from . import estimates, features, io, preprocessing, sleep, wear_time

# Expose API functions
from .estimates import calculate_pa_levels, create_activity_column
from .features import calculate_actigraph_counts, calculate_vector_magnitude, calculate_brond_counts
from .io import read_gt3x
from .sleep import detect_sleep_weitz2022, detect_time_in_bed_weitz2022
from .wear_time import detect_non_wear_time_naive, detect_non_wear_time_hees2011, detect_non_wear_time_syed2021

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"] + "dev"



def sysinfo():
    """
    Prints system the dependency information
    """
    paat = pkg_resources.working_set.by_key["paat"]
    dependencies = [r.project_name for r in paat.requires()]

    header = ("PAAT Information\n"
              "=================\n\n")

    general = ("General Information\n"
               "-------------------\n"
               f"Python version: {sys.version.split()[0]}\n"
               f"PAAT version: {__version__}\n\n")

    uname = os.uname()
    osinfo = ("Operating System\n"
              "----------------\n"
              "OS: {s.sysname} {s.machine}\n"
              "Kernel: {s.release}\n").format(s=uname)

    if uname.sysname == "Linux":
        _, *lines = os.popen("free -m").readlines()
        for identifier in ("Mem:", "Swap:"):
            memory = [line for line in lines if identifier in line]
            if len(memory) > 0:
                _, total, used, *_ = memory[0].split()
            else:
                total, used = '?', '?'
            osinfo += f"{identifier} {used}MiB/{total}MiB\n"

    osinfo += "\n"

    deps = ("Dependencies\n"
            "------------\n")

    deps += "\n".join("{pkg.__name__}: {pkg.__version__}".format(pkg=__import__(dep))
                      for dep in dependencies)

    print(header + general + osinfo + deps)
