from . import TimingUtil
from . import StrUtils
import time
import os
import hashlib

def timing(f):
  return TimingUtil.CTimingUtil.timing_impl(f)
  
class ParamsError(Exception):
  pass
      
def mstime() -> int:
  return round(time.time() * 1000)

def fssync():
  os.system("sync")


def mpSeed() -> str:
  return "p%d_%d" % (os.getpid(), mstime())

class HasherFactory:
  @staticmethod
  def createHasher():
    return hashlib.sha512()