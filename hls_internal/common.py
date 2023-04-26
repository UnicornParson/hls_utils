import os
import time
from urllib.parse import urlparse
import aiofiles
import aiohttp
import shutil

def mstime() -> int:
  return round(time.time() * 1000)

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
				print(url, " done")
				ret.ok = True
				ret.time = time.time() - start
				if ret.time > 0:
					ret.speed = ret.size / ret.time
				return ret
			ret.ok = False
	ret.time = time.time() - start
	return ret