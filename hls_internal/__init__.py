import sys
import os
from importlib.metadata import *
def has_pkg(name: str) -> bool:
    try:
        return bool(version(name))
    except PackageNotFoundError:
        return False
    except Exception as e:
        print("unexpected pkg error %s" % str(e))
    return False

internalbindir = os.path.dirname(os.path.abspath(__file__))
commonPath = internalbindir + "/../common"
sys.path.append(commonPath)
import common
from . import StatCollector
from . import DbWriter
from . import ListScanner
from . import HLSDownloader
from . import ListParser
