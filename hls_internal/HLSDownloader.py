import aiofiles
import aiohttp
from aiohttp import ClientSession
import m3u8
from urllib.parse import urlparse
from .common import *

class Downloader:
	def __init__(self) -> None:
		self.playlist = None

	async def downloadSegment(self, url: str, target:str)-> bool:
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as resp:
				if resp.status == 200:
					f = await aiofiles.open(target, mode='wb')
					await f.write(await resp.read())
					await f.close()
					print(url, " done")
					return True
				print(url, " returns status ", resp.status)

	async def downloadPlaylist(self, url: str) -> bool:
		try:
			self.playlist = m3u8.load(url)
		except Exception as e:
			print("cannot download ", url, " reason ", str(e))
			return False
		ret = True
		if not self.playlist:
			print("no playlist")
			return False
		if self.playlist.is_variant:
			for sub in self.playlist.playlists:
				newuri = sub.uri
				if not isAbsoluteUrl(sub.uri):
					base = urlBase(url)
					newuri = base + sub.uri
				print("download ", newuri, " with bandwidth ", sub.stream_info.bandwidth)
				rc = await self.downloadPlaylist(newuri)
				ret &= rc
			return ret
		
		for segment in self.playlist.segments.by_key(None):
			u = urlparse(segment.uri)
			p = "./%d_pid%d_%s" % (mstime(), os.getpid(), os.path.basename(u.path))
			print(" download ", segment.uri, " to ", p)
			rc = await self.downloadSegment(segment.uri, p)

		print(self.playlist.target_duration)
		return ret