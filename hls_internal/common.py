import os
import time
from urllib.parse import urlparse

def mstime() -> int:
  return round(time.time() * 1000)

def fssync():
  os.system("sync")


def mpSeed() -> str:
  return "p%d_%d" % (os.getpid(), mstime())

def isAbsoluteUrl(url) -> bool:
	return bool(urlparse(url).netloc)

def urlBase(u) -> str:
	return (u[:u.rfind('/')] + "/")

def urlTail(u)->str:
	return u[u.rfind('/'):]

def followUri(baseUri, target) -> str:
	newuri = target
	if not isAbsoluteUrl(target):
		base = urlBase(baseUri)
		newuri = base + target
	return newuri