from common import *
from hls_internal import *
from hls_internal.HLSDownloader import *
from hls_internal.common import *
from hls_internal.ListScanner import *
from hls_internal.ListParser import Parser
import asyncio
import pprint

async def downloaderTest():
	url = "https://kernel.org/theme/images/logos/tux.png"
	rc = await downloadFile(url)
	#print(str(rc))
	assert rc
	assert rc.url
	assert rc.target
	assert rc.ok

async def scanTest():
	playlistUrl = "https://iptv-org.github.io/iptv/index.nsfw.m3u"
	p = Parser()
	s = ListScanner()
	rc = await p.load(playlistUrl)
	assert rc

	await s.loadUrl(playlistUrl)
	l = await s.scan()
	assert l

async def main() -> int:
	await downloaderTest()
	await scanTest()

if __name__ == '__main__':
	result = 0
	try:
		result = asyncio.run(main())
	except KeyboardInterrupt:
		print(" KeyboardInterrupt...")
	exit(result)