import asyncio
import base64
import json
import pprint
import datetime
import logging
import json

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
	
	def toDict(self) -> dict:
		d = {}
		d["time"] = self.time
		d["variant"] = self.variant
		d["url"] = self.url
		d["bandwidth"] = self.bandwidth
		d["invalid"] = self.invalid
		d["invalidReason"] = self.invalidReason
		d["seq"] = self.seq
		d["duration"] = self.duration
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

	async def close(self):
		pass

class StatPrinter(StatWriter):
	async def write(self, stat: PlaylistStat) -> bool:
		d = stat.toDict()
		logging.debug(json.dumps(d))
		if d["lastPlaylist"]:
			s = len(d["lastPlaylist"])
			d["lastPlaylist"] = "<truncated data> size %d" % s
		pprint.pprint(d)
		return True

class StatVerbosePrinter(StatWriter):
	async def write(self, stat: PlaylistStat) -> bool:
		pprint.pprint(stat.toDict())
		logging.debug(str(stat.toDict()))
		return True