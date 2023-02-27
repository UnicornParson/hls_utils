import m3u8
import asyncio
import traceback
import time
from urllib.parse import urlparse
from .PlaylistStat import *

def isAbsoluteUrl(url) -> bool:
	return bool(urlparse(url).netloc)

def urlBase(u) -> str:
	return (u[:u.rfind('/')] + "/")

def urlTail(u)->str:
	return u[u.rfind('/'):]

class StatCollector:
	def __init__(self) -> None:
		self.statWriters = []

	def setup(self, statWriters) -> bool:
		if not statWriters:
			raise ValueError("invalid writer")
		self.statWriters = statWriters
		return True

	async def processUrl(self, url: str) -> bool:
		if not self.statWriters:
			raise ValueError("run before setup")
		ret  = True
		stats = await self.getPlaylistStat(url)
		for s in stats:
			ret &= not s.invalid
			writeRc = True
			for writer in self.statWriters:
				if writer:
					writeRc &= await writer.write(s)
			if not writeRc:
				print("cannot write to writer")
		return ret

	async def runLoop(self, url: str) -> bool:
		rc = True
		try:
			while True:
				rc &= await self.processUrl(url)
				await asyncio.sleep(1)
		except KeyboardInterrupt:
			print("Interrupted..")
		except Exception as e:
			print("error: ", str(e))
			rc = False
		return rc

	async def getPlaylistStat(self, url: str):
		if not self.statWriters:
			raise ValueError("run before setup")
		print("stat for ", url)
		stat = PlaylistStat()
		stat.url = url
		stat.bandwidth = 0
		stat.loadDuaration = 0.0
		try:
			before = time.time()
			playlist = m3u8.load(url)
			stat.loadDuaration = (time.time()-before)
		except Exception as e:
			stat.invalid = True
			stat.invalidReason = str(e)
			return [stat]
		rc = []
		stat.variant = playlist.is_variant
		if playlist.is_variant:
			for sub in playlist.playlists:
				print("download ", sub.uri, " with bandwidth ", sub.stream_info.bandwidth)
				newuri = sub.uri
				if not isAbsoluteUrl(sub.uri):
					base = urlBase(url)
					newuri = base + sub.uri
				l = await self.getPlaylistStat(newuri)
				if l == None:
					raise ValueError("unexpected stat list")
				for item in l:
					if item == None:
						raise ValueError("unexpected stat item")
					item.bandwidth = sub.stream_info.bandwidth
					rc.append(item)
					stat.duration += item.duration
			rc.append(stat)
		else:
			stat.lastPlaylist = playlist.dumps()
			stat.duration = playlist.target_duration
			stat.seq = playlist.media_sequence
			rc.append(stat)
		return rc