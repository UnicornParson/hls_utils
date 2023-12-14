import aiofiles
import aiohttp
import m3u8
from urllib.parse import urlparse
from .common import *
import logging

class PlaylistMapping:
	def __init__(self, size:int = 2048):
		# (seq, remotename, fname)
		self.q = []
		self.maxSize = size
		self.seq = 0

	def __contains__(self, item: str):
		for i in self.q:
			if i[1] == item:
				return True
		return False

	def put(self, remotename, fname):
		self.seq += 1
		self.q.append((self.seq, remotename, fname))
		while len(self.q) >= self.maxSize:
			self.q.pop()

	def size(self):
		return len(self.q)

class Downloader:
	def __init__(self) -> None:
		self.playlist = None
		self.saveMeta = False

	async def downloadPlaylist(self, url: str, mapper = None) -> bool:
		try:
			logging.info("try to open %s" % url)
			self.playlist = m3u8.load(url)
		except Exception as e:
			logging.error("cannot download %s reason %s" % (url, str(e)))
			return False
		ret = True
		if not self.playlist:
			logging.error("no playlist")
			return False
		playlistName = "./%d_pid%d_" % (mstime(), os.getpid())
		if self.playlist.is_variant:
			playlistName += "variant_%s" % os.path.basename(urlparse(url).path)
			if self.saveMeta:
				if Globals.zipdata:
					playlistName += ".gz"
				saveToFile(self.playlist.dumps(), playlistName, Globals.zipdata)
			for sub in self.playlist.playlists:
				newuri = sub.uri
				if not isAbsoluteUrl(sub.uri):
					base = urlBase(url)
					newuri = base + sub.uri
				logging.info("download %s with bandwidth %3.1f " % (newuri, sub.stream_info.bandwidth))
				rc = await self.downloadPlaylist(newuri)
				ret &= rc
			return ret

		playlistName += "final_%s" % os.path.basename(urlparse(url).path)
		if self.saveMeta:
			if Globals.zipdata:
				playlistName += ".gz"
			saveToFile(self.playlist.dumps(), playlistName, Globals.zipdata)
		for segment in self.playlist.segments.by_key(None):
			segmenturl = followUri(url, segment.uri)
			u = urlparse(segmenturl)
			
			p = "./%d_pid%d_%s" % (mstime(), os.getpid(), os.path.basename(u.path))
			logging.info(" download %s to %s" % (segmenturl, p))
			if mapper:
				if segmenturl in mapper:
					logging.info("%s already downloaded. skip" % segmenturl)
					print("SKIP %s" % segmenturl)
					continue
				mapper.put(segmenturl, p)

			print("DL %s" % segmenturl)
			dlrc = await downloadFile(segmenturl, p)
			logging.info(str(dlrc))
			ret &= dlrc.ok

		mprint("target_duration %s" % str(self.playlist.target_duration))
		return ret