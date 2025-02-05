import os
import time
from urllib.parse import urlparse
import aiofiles
import aiohttp
import shutil
import logging
import pprint
import traceback
import datetime
import requests
from requests import ConnectionError
import random
import sys
import gzip
import io
import tempfile

def saveToFile(text, target, zip = False):
	if zip:
		with gzip.open(target, 'wb') as f:
			with io.TextIOWrapper(f, encoding='utf-8') as encode:
				encode.write(text)
	else:
		with open(target, 'w') as f:
			f.write(text)

def textFromFile(source, zip = False):
	if zip:
		with gzip.open(source, 'rb') as f:
			with io.TextIOWrapper(f, encoding='utf-8') as decoder:
				return str(decoder.read())
	else:
		with open(source, 'r') as f:
			return str(f.read())
class Globals:
	verbose: bool = False
	flow: bool = False
	flowResults: dict = {}
	zipdata: bool = False

def mstime() -> int:
  return round(time.time() * 1000)

def tmpFname() -> str:
	d = tempfile.gettempdir()
	salt = random.uniform(0, 2**30)
	return "%s/hlstmp_%d_%d.tmp" % (d, salt, mstime())

def eprint(msg: str):
	logging.error(msg)
	logging.error(str(traceback.format_exc()))
	if not Globals.flow:
		print("# " + msg, file=sys.stderr)

def mprint(msg: str):
	logging.info(msg)
	if Globals.verbose and not Globals.flow:
		print("# " + msg)

def objprint(msg, obj):
	s = pprint.pformat(obj)
	mprint("%s: [\n%s\n]" % (msg, s))

def fssync():
	os.system("sync")

# https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb
def convert_bytes(num):
	step_unit = 1000.0 #1024 bad the size
	for x in ['B', 'KB', 'MB', 'GB', 'TB']:
		if num < step_unit:
			return "%3.1f %s" % (num, x)
		num /= step_unit

def mpSeed() -> str:
	return "p%d_%d" % (os.getpid(), mstime())

def isAbsoluteUrl(url) -> bool:
	return bool(urlparse(url).netloc) and not url.startswith("/")

def isUrl(url) -> bool:
	return isAbsoluteUrl(url)

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


class DownloadFileStat:
	def __init__(self) -> None:
		self.url = ""
		self.target = ""
		self.ok = False
		self.status = 0
		self.size = 0
		self.time = None
		self.speed = 0.0

	def toDict(self)->dict:
		d = {}
		d["url"] = self.url
		d["target"] = self.target
		d["ok"] = self.ok
		d["status"] = self.status
		d["size"] = self.size
		d["time"] = self.time
		d["speed"] = self.speed
		return d
	def __str__(self) ->str:
		d = self.toDict()
		d["speed"] = str(convert_bytes(d["speed"])) + "/s"
		d["size"] = convert_bytes(d["size"])
		return str(d)

async def downloadFile(url: str, target:str = "")-> DownloadFileStat:
	ret = DownloadFileStat()
	start = time.time()
	ret.url = url
	ret.target = target
	if not target:
		# make tmp 
		ret.target = "./dltmp.%s.%s" % (mpSeed(), os.path.basename(urlparse(url).path))
	tmpname = ret.target + ".part"
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as resp:
				ret.status = resp.status
				if resp.status == 200:
					f = await aiofiles.open(tmpname, mode='wb')
					data = await resp.read()
					ret.size = len(data)
					await f.write(data)
					await f.close()
					shutil.move(tmpname, ret.target)
					mprint(url + " done")
					ret.ok = True
					ret.time = time.time() - start
					if ret.time > 0:
						ret.speed = ret.size / ret.time
					return ret
				ret.ok = False
	except Exception as e:
		eprint("downloadFile exception %s" % str(e))

	ret.time = time.time() - start
	return ret

def randomSleep(start: float , stop: float ):
	d = random.uniform(start, stop)
	mprint("sleep %f seconds" % d)
	time.sleep(d)
def contentType(url: str):
	try:
		resp = requests.head(url, allow_redirects=True, verify=False, timeout=2.50)
	except ConnectionError:
		return None
	except Exception as e:
		# something unexpected
		eprint("head request to %s failed with reason %s" % (url, str(e)))
		return None
	if 'Content-Type' in resp.headers:
		return resp.headers['Content-Type']
	return None

def isHLS(ct: str)-> bool:
	types = ["application/vnd.apple.mpegurl", "application/x-mpegURL"]
	return ct in types

def default_serialize(obj):
	if isinstance(obj, datetime.datetime):
		return obj.isoformat()
	raise TypeError("Type %s not serializable" % type(obj).__name__)