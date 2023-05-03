import asyncio
import pprint
from .PlaylistStat import *
from .StatCollector import *
from .DbWriter import *
from .ListParser import *
from .common import *

class ListScanner:
	def __init__(self):
		self.urls = []
		self.nop = NopPrinter()

	def loadList(self, urls):
		self.urls.clear()
		for u in urls:
			us = u.strip()
			if us and us[0] == "#":
				continue
			if isUrl(us):
				self.urls.append(us)

	async def loadUrl(self, baseUrl) :
		p = Parser()
		data:ListData = await p.load(baseUrl)
		if not data.ok:
			eprint("cannot load base url %s reason %s" % (baseUrl, baseUrl))
			return False, data.reason
		if not data.items:
			return True, "no items"
		self.loadList(data.items)
		return True, "ok"

	async def scan(self) -> list:
		rc = []
		for u in self.urls:
			collector = StatCollector()
			collector.setup([self.nop])
			stat = await collector.getPlaylistStat(u)
			pprint.pprint(stat)