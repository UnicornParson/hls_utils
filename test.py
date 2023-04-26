from common import *
from hls_internal import *
from hls_internal.HLSDownloader import *
from hls_internal.common import *
import asyncio
import pprint


async def main() -> int:
	#url = "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.2.6.tar.xz"
	url = "https://kernel.org/theme/images/logos/tux.png"
	rc = await downloadFile(url)
	print(str(rc))
	assert rc
	assert rc.url
	assert rc.target
	assert rc.ok

if __name__ == '__main__':
	result = 0
	try:
		result = asyncio.run(main())
	except KeyboardInterrupt:
		print(" KeyboardInterrupt...")
	exit(result)