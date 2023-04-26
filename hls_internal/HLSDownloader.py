import aiofiles
import aiohttp
import m3u8
from urllib.parse import urlparse
from .common import *
import logging

class Downloader:
	def __init__(self) -> None:
		self.playlist = None
	async def downloadPlaylist(self, url: str) -> bool:
		try:
			logging.info("try to open %s" % url)
			self.playlist = m3u8.load(url)
		except Exception as e:
			logging.error("cannot download %s reason %s", (url, str(e)))
			return False
		ret = True
		if not self.playlist:
			logging.error("no playlist")
			return False
		if self.playlist.is_variant:
			for sub in self.playlist.playlists:
				newuri = sub.uri
				if not isAbsoluteUrl(sub.uri):
					base = urlBase(url)
					newuri = base + sub.uri
				logging.info("download %s with bandwidth %3.1f " % (newuri, sub.stream_info.bandwidth))
				rc = await self.downloadPlaylist(newuri)
				ret &= rc
			return ret
		
		for segment in self.playlist.segments.by_key(None):
			segmenturl = followUri(url, segment.uri)
			u = urlparse(segmenturl)
			
			p = "./%d_pid%d_%s" % (mstime(), os.getpid(), os.path.basename(u.path))
			logging.info(" download %s to %s" % (segmenturl, p))
			dlrc = await downloadFile(segmenturl, p)
			logging.info(str(dlrc))
			ret &= dlrc.ok

		print(self.playlist.target_duration)
		return ret