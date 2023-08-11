import asyncio
import base64
import json
import datetime
import logging
import json

from .common import *

class PlaylistStat:
	def __init__(self) -> None:
		self.variant = False
		self.url = ""
		self.bandwidth = 0
		self.invalid = False
		self.invalidReason = ""
		self.seq = 0
		self.duration = 0
		self.lastPlaylist = ""
		self.time = datetime.datetime.now()
		self.loadDuaration = 0.0
	
	def toDict(self, scramble: bool = False) -> dict:
		d = {}
		d["time"] = self.time
		d["variant"] = self.variant
		if scramble:
			d["url"] = base64.b64encode(bytes(self.url, 'utf-8')).decode("utf-8")
		else:
			d["url"] = self.url
		d["bandwidth"] = self.bandwidth
		d["invalid"] = self.invalid
		d["invalidReason"] = self.invalidReason
		d["seq"] = self.seq
		d["duration"] = self.duration

		if scramble:
			d["lastPlaylist"] = base64.b64encode(bytes(self.lastPlaylist, 'utf-8')).decode("utf-8")
		else:
			d["lastPlaylist"] = self.lastPlaylist
		d["loadDuaration"] = self.loadDuaration
		return d
	
	def toTuple(self) -> tuple:
		return 	(
			self.time,
			self.url,
			self.variant,
			self.bandwidth,
			self.invalid,
			self.invalidReason,
			self.seq,
			self.duration,
			base64.b64encode(bytes(self.lastPlaylist, 'utf-8')).decode("utf-8"),
			self.loadDuaration)

class StatWriter:
	def __init__(self) -> None:
		pass
	
	async def write(self, stat: PlaylistStat) -> bool:
		return True

	async def setup(self) -> bool:
		return True
	async def close(self):
		pass

class NopPrinter(StatWriter):
	async def write(self, stat: PlaylistStat) -> bool:
		return True
class NopWriter(StatWriter):
	async def setup(self) -> bool:
		return True
	async def write(self, stat: PlaylistStat) -> bool:
		return True
class StatPrinter(StatWriter):
	async def write(self, stat: PlaylistStat) -> bool:
		d = stat.toDict()
		logging.debug(json.dumps(d, default=default_serialize))
		if d["lastPlaylist"]:
			s = len(d["lastPlaylist"])
			d["lastPlaylist"] = "<truncated data> size %d" % s
		objprint("statprinter.dict", d)
		return True

class StatVerbosePrinter(StatWriter):
	async def write(self, stat: PlaylistStat) -> bool:
		objprint("StatVerbosePrinter.doct", stat.toDict())
		logging.debug(str(stat.toDict()))
		return True