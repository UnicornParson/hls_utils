import enum 
import sqlite3
import sys
import os
import asyncio
import time
from .PlaylistStat import *

"""
			CREATE TABLE "segments" (
				"id"	INTEGER NOT NULL UNIQUE,
				"parent"	INTEGER NOT NULL,
				"url"	TEXT,
				"seq"	INTEGER NOT NULL DEFAULT 0,
				"hash"	TEXT NOT NULL,
				"size"	INTEGER NOT NULL DEFAULT 0,
				"meta"	TEXT,
				"ex"	TEXT,
				PRIMARY KEY("id" AUTOINCREMENT)
				);
		"""

class SegmentRecord:
	def __init__(self) -> None:
		self.parent = ""
		self.url = ""
		self.seq = 0
		self.hash = ""
		self.size = 0
		self.meta = ""
		self.ex = ""

	def toTuple(self) -> tuple:
		return (self.parent,
				self.url,
				self.seq,
				self.hash,
				self.size,
				self.meta,
				self.ex)

class DBEngine:
	def __init__(self) -> None:
		self.connection = None
		self.cursor = None
		self.path = ""

	async def open(self, path:str):
		self.path = path
		self.connection = sqlite3.connect(path)
		self.cursor = self.connection.cursor()
		await self.makeDb()

	def checkDb(self):
		if not self.cursor or not self.connection:
			raise Exception('dbEngine', 'not opened')
		

	async def exec(self, q : str, params : tuple):
		self.checkDb()
		self.cursor.execute(q, params)
		self.connection.commit()
			
	async def makeDb(self):
		self.checkDb()
		self.cursor.execute("""
			CREATE TABLE "playlists" (
				"id"	INTEGER NOT NULL UNIQUE,
				"time"  timestamp NOT NULL,
				"url"	TEXT NOT NULL,
				"variant"	INTEGER NOT NULL DEFAULT 0,
				"bandwidth"	INTEGER NOT NULL DEFAULT 0,
				"invalid"	INTEGER NOT NULL DEFAULT 0,
				"invalidReason"	TEXT,
				"loadDuration" REAL NOT NULL DEFAULT 0.0,
				"seq"	INTEGER NOT NULL,
				"duration"	REAL NOT NULL DEFAULT 0.0,
				"lastplaylist"	TEXT, 
				PRIMARY KEY("id" AUTOINCREMENT)
		);
		""")

		self.cursor.execute("""
			CREATE TABLE "segments" (
				"id"	INTEGER NOT NULL UNIQUE,
				"parent"	INTEGER NOT NULL,
				"url"	TEXT,
				"seq"	INTEGER NOT NULL DEFAULT 0,
				"hash"	TEXT NOT NULL,
				"size"	INTEGER NOT NULL DEFAULT 0,
				"meta"	TEXT,
				"ex"	TEXT,
				PRIMARY KEY("id" AUTOINCREMENT)
				);
		""")
		self.cursor.execute("PRAGMA auto_vacuum = '2'")
		self.cursor.execute("VACUUM")
		self.cursor.execute("PRAGMA journal_mode = 'MEMORY'")
		self.connection.commit()

	def close(self):
		self.cursor = None
		if self.connection:
			self.connection.close()
		self.connection = None

class StatSqliteWriter(StatWriter):
	def __init__(self) -> None:
		self.engine = None
	
	async def setup(self) -> bool:
		await self.close()
		self.engine = DBEngine()
		name = "./%s.db" % self.fname()
		try:
			await self.engine.open(name)
		except Exception as e:
			print("cannot open db in %s reason %s" % (name, str(e)))
			self.engine.close()
			return False
		return True
	
	async def close(self):
		if self.engine:
			self.engine.close()
			self.engine = None

	def fname(self) -> str:
		return "%d_p%d" % (round(time.time() * 1000), os.getpid())

	async def writeSegment(self, segment: SegmentRecord) -> bool:
		if not self.engine:
			print("no engine")
			return False
		try:
			data = segment.toTuple()
			q = """INSERT INTO 'segments'('parent', 'url', 'seq', 'hash', 'size','meta', 'ex')VALUES (?,?,?,?,?,?,?);"""
			await self.engine.exec(q, data)
		except Exception as e:
			print("cannot exec query ", str(e))
			return False
		return True

	async def write(self, stat: PlaylistStat) -> bool:
		if not self.engine:
			print("no engine")
			return False
		try:
			data = stat.toTuple()
			q = """INSERT INTO 'playlists'('time', 'url', 'variant', 'bandwidth', 'invalid', 'invalidReason', 'seq', 'duration', 'lastplaylist', 'loadDuration')
			 		VALUES (?,?,?,?,?,?,?,?,?,?);"""
			await self.engine.exec(q, data)
		except Exception as e:
			print("cannot exec query ", str(e))
			return False
		return True
		