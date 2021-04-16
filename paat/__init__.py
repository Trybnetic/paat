"""
PAAT - Physical Activity Analysis Toolbox
=========================================

The physical activity analysis toolbox (PAAT) is a comprehensive toolbox to
analyse raw acceleration data.

"""

import os
import sys
from pip._vendor import pkg_resources


__author__ = ('Marc Weitz, Shaheen Syed, Alexander Horsch')
__author_email__ = 'marc.weitz@uit.no'
__version__ = '0.1.0'
__license__ = 'MIT'
__description__ = ('A comprehensive toolbox to analyse and model physical '
                   'activity data')
__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Information Analysis',
    ]


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
               "Python version: {}\n"
               "PAAT version: {}\n\n").format(sys.version.split()[0], __version__)

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
            osinfo += "{} {}MiB/{}MiB\n".format(identifier, used, total)

    osinfo += "\n"

    deps = ("Dependencies\n"
            "------------\n")

    deps += "\n".join("{pkg.__name__}: {pkg.__version__}".format(pkg=__import__(dep))
                      for dep in dependencies)

    print(header + general + osinfo + deps)
