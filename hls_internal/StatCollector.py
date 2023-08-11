import m3u8
import asyncio
import traceback
import time
from urllib.parse import urlparse
from .PlaylistStat import *
from .common import *


class StatCollector:
	def __init__(self, follow: bool = True) -> None:
		self.statWriters = []
		self.follow = follow

	def setup(self, statWriters) -> bool:
		if not statWriters:
			raise ValueError("invalid writer")
		self.statWriters = statWriters
		return True

	async def processUrl(self, url: str) -> bool:
		mprint("process %s" % url)
		if not self.statWriters:
			raise ValueError("run before setup")
		ret = True
		stats = await self.getPlaylistStat(url)
		if Globals.flow:
			Globals.flowResults["stat"] = []
		for s in stats:
			ret &= not s.invalid
			writeRc = True
			if Globals.flow:
				Globals.flowResults["stat"].append(s.toDict(True))
			else:
				for writer in self.statWriters:
					if writer:
						writeRc &= await writer.write(s)
				if not writeRc:
					eprint("cannot write to writer")
		return ret

	async def runLoop(self, url: str) -> bool:
		rc = True
		try:
			while True:
				rc &= await self.processUrl(url)
				await asyncio.sleep(1)
		except KeyboardInterrupt:
			eprint("Interrupted..")
		except Exception as e:
			eprint("error: ", str(e))
			rc = False
		return rc

	async def getPlaylistStat(self, url: str):
		if not self.statWriters:
			raise ValueError("run before setup")
		mprint("stat for %s" % url)
		stat = PlaylistStat()
		stat.url = url
		stat.bandwidth = 0
		stat.loadDuaration = 0.0
		stat.duration = 0

		# test content
		ct = contentType(url)
		if not isHLS(ct):
			stat.invalid = True
			stat.invalidReason = "target content type is %s" % str(ct)
			return [stat]

		try:
			before = time.time()
			playlist = m3u8.load(url, timeout=3.0)
			stat.loadDuaration = (time.time()-before)
		except Exception as e:
			stat.invalid = True
			stat.invalidReason = str(e)
			return [stat]
		rc = []
		stat.variant = playlist.is_variant
		if playlist.is_variant and self.follow:
			for sub in playlist.playlists:
				mprint("download %s with bandwidth %s" % (sub.uri, sub.stream_info.bandwidth))
				newuri = sub.uri
				if not isAbsoluteUrl(sub.uri):
					base = urlBase(url)
					newuri = base + sub.uri
				l = await self.getPlaylistStat(newuri)
				if l is None:
					raise ValueError("unexpected stat list")
				for item in l:
					if item is None:
						raise ValueError("unexpected stat item")
					item.bandwidth = sub.stream_info.bandwidth
					rc.append(item)
					stat.duration += item.duration

		else:
			stat.lastPlaylist = playlist.dumps()
			stat.duration = playlist.target_duration
			stat.seq = playlist.media_sequence
		rc.append(stat)
		return rc