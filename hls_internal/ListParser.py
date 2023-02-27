import asyncio
import aiofiles
import aiohttp
from aiohttp import ClientSession
import urllib

def isUrl(path:str)->bool:
	return urllib.parse.urlparse(path).scheme not in ["", "file"]

class ListData():
	def __init__(self) -> None:
		self.items = []
		self.ok = False
		self.reason = ""

class Parser():
	def __init__(self) -> None:
		pass

	async def readRaw(self, url:str)->str:
		if not url:
			return ("", "not url")
		raw = ""
		err = ""
		if isUrl(url):
			print("load %s as remote file" % url)
			async with aiohttp.ClientSession() as session:
				async with session.get(url) as response:
					if response.status == 200:
						raw = await response.text()
						err = ""
					else:
						err = "status %d, text %s" % (response.status, raw)
						raw = ""
		else:
			#TODO: read local file
			pass
		return (raw, err)

	async def load(self, url:str)->list:
		ret = ListData()
		if not url:
			ret.reason = "no url"
			return ret
		rc = await self.readRaw(url)
		if rc[1] or not rc[0]:
			ret.reason = rc[1]
			ret.ok = False
			return ret
		print(rc[0])
		ret.items = rc[0].splitlines()
		ret.ok = True
		return ret