"""
PAAT - Physical Activity Analysis Toolbox
=========================================

The physical activity analysis toolbox (PAAT) is a comprehensive toolbox to
analyze raw acceleration data. We developed all code mainly for analyzing
ActiGraph data (GT3X files) in large sample study settings where manual annotation
and analysis is not feasible.

This package has been developed and is maintained by researchers at UiT - the
arctic university of Norway and was supported by the High Northern
Population Studies, an interdisciplinary initiative to improve the health of
future generations. The purpose of this package is to make our research on raw
accelerometry easier accessible to other researchers. Most methods implemented
in this package have been described in scientific papers which are usually
cited in the function's description. If you are using any of these methods in
your research, we would be grateful if you cite the corresponding original paper(s).
"""

import os
import sys
import platform

from . import estimates, features, io, preprocessing, sleep, wear_time

# Expose API functions
from .estimates import calculate_pa_levels, create_activity_column
from .features import calculate_actigraph_counts, calculate_vector_magnitude, calculate_brond_counts, calculate_enmo
from .io import read_gt3x, read_metadata
from .calibration import calibrate
from .sleep import detect_time_in_bed_weitz2024
from .wear_time import detect_non_wear_time_naive, detect_non_wear_time_hees2011, detect_non_wear_time_syed2021

try:
    from packaging.requirements import Requirement
except ModuleNotFoundError:  # this should only happend during setup phase
    Requirement = None

try:
    from importlib import metadata
    __version__ = metadata.version(__package__)
    show_deps = True
except metadata.PackageNotFoundError:
    import toml
    __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"] + "dev"
    show_deps = False


def sysinfo():
    """
    Prints system the dependency information
    """
    out = ("PAAT Information\n"
              "=================\n\n")

    out += ("General Information\n"
               "-------------------\n"
               f"Python version: {sys.version.split()[0]}\n"
               f"PAAT version: {__version__}\n\n")

    uname = platform.uname()
    out += ("Operating System\n"
              "----------------\n"
              "OS: {s.system} {s.machine}\n"
              "Kernel: {s.release}\n").format(s=uname)

    if uname.system == "Linux":
        _, *lines = os.popen("free -m").readlines()
        for identifier in ("Mem:", "Swap:"):
            memory = [line for line in lines if identifier in line]
            if len(memory) > 0:
                _, total, used, *_ = memory[0].split()
            else:
                total, used = '?', '?'
            out += f"{identifier} {used}MiB/{total}MiB\n"

    out += "\n"

    if show_deps:
        out += ("Dependencies\n"
                "------------")
        for dep in [dep.split(" ")[0] for dep in metadata.requires("paat")]:
            out += f"\n{dep}: {metadata.version(dep)}"

    print(out)
