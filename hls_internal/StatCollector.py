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

	async def processUrl(self, url: str, tryMedia: bool) -> bool:
		mprint("process %s" % url)
		if not self.statWriters:
			raise ValueError("run before setup")
		ret = True
		stats = await self.getPlaylistStat(url, tryMedia)
		if Globals.flow:
			Globals.flowResults["stat"] = []
		for s in stats:
			ret &= not s.invalid
			if tryMedia and not s.variant:
				ret &= (bool(s.media) and ("ok" in s.media) and (s.media["ok"]))
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
				rc &= await self.processUrl(url, True)
				await asyncio.sleep(1)
		except KeyboardInterrupt:
			eprint("Interrupted..")
		except Exception as e:
			eprint("error: ", str(e))
			rc = False
		return rc

	async def getPlaylistStat(self, url: str, tryMedia: bool):
		if not self.statWriters:
			raise ValueError("run before setup")
		mprint("stat for %s" % url)
		stat = PlaylistStat()
		stat.url = url
		stat.bandwidth = 0
		stat.loadDuaration = 0.0
		stat.duration = 0
		stat.size = 0
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
			stat.size = len(playlist.dumps())
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
			stat.media = await self.tryMedia(playlist, url) if tryMedia else {}
			stat.lastPlaylist = playlist.dumps()
			stat.duration = playlist.target_duration
			stat.seq = playlist.media_sequence
		rc.append(stat)
		return rc

	async def tryMedia(self, playlist, base_url) -> dict:
		rc = {}
		if not playlist.segments:
			rc["ok"] = False
			rc["reason"] = "No Segmants"
			return rc
		last_seg = playlist.segments[-1]
		last_seg_uri = last_seg.uri
		if not isAbsoluteUrl(last_seg.uri):
			base = urlBase(base_url)
			last_seg_uri = base + last_seg.uri
		tmp_target = tmpFname()
		if (last_seg_uri.startswith("/")):
			raise ValueError("invalid url [%s], base [%s], segment [%s]" % (last_seg_uri, urlBase(base_url), last_seg.uri))
		last_stat = await downloadFile(last_seg_uri, tmp_target)
		rc["try"] = last_stat.toDict()
		rc["ok"] = last_stat.ok
		return rc
