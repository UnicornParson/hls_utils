from .common import *
import json
import base64
class OutputFormat:
	Json = "json"
	SqLite = "sqlite"
	PrettyPrint = "pretty"

	@staticmethod
	def all():
		return [OutputFormat.Json, OutputFormat.SqLite, OutputFormat.PrettyPrint]

class ReservedTargets:
	stdout = "stdout"

class ResultPkg:
	FilterRc = "FilterRc"
	Original = "Original"
	Empty = "empty"

	@staticmethod
	def getEmpty():
		o = ResultPkg(None)
		o.what = ResultPkg.Empty
		o.subtype = ""
		return

	def isEmpty(self):
		return self.what == ResultPkg.Empty or not self.content

	def __init__(self, obj):
		self.content = obj
		self.what = ResultPkg.Original
		self.subtype = ""

class ResultPrinter():
	def __init__(self, format: str, target: str):
		self.target = target
		self.format = format

	def print(self, obj: ResultPkg):
		mprint("print to %s[%s]" % (self.target, self.format))
		if self.format == OutputFormat.Json:
			self.json_print(obj)
		elif self.format == OutputFormat.PrettyPrint:
			self.prettyPrint(obj)
		else:
			eprint("format %s is not implemented" % self.format)

	def prettyPrint(self, obj: ResultPkg):
		msg = ""
		if not obj or obj.isEmpty():
			eprint("no results")
			return
		if obj.what == ResultPkg.Original:
			msg = pprint.pformat(obj.content, indent=4)
		elif obj.what == ResultPkg.FilterRc:
			if obj.subtype == ResultFilter.FilterAvailable:
				for record in obj.content:
					msg += str(base64.b64decode(record).decode('utf-8')) + "\n"
			elif obj.subtype == ResultFilter.FilterOnOff:
				for url, stat in obj.content.items():
					sym = " ⚫ "
					if stat:
						sym = " ⚪ "
					msg += "{0}{1}\n".format(sym, str(base64.b64decode(url).decode('utf-8')))
			else:
				msg = pprint.pformat(obj.content, indent=4)
		else:
			msg = "[ NO DATA ]"
		self.write(msg)

	def write(self, msg: str):
		t = self.target.strip()
		if t.lower() == ReservedTargets.stdout:
			print(msg)
			return
		mprint("write results to %s" % self.target)
		with open(t, "w") as f:
			f.write(msg)
			f.flush()
			fssync()

	def json_print(self, obj: ResultPkg):
		msg = json.dumps(obj.content, default=default_serialize)
		self.write(msg)

class ResultFilter:
	FilterAvailable = "available"
	FilterOnOff = "onoff"
	FilterAsIs = "asis"

	@staticmethod
	def statfilter(f: str, statResults: ResultPkg) -> ResultPkg:
		mprint("apply stat filter %s" % f)
		if f == ResultFilter.FilterAsIs:
			return statResults
		if f == ResultFilter.FilterAvailable:
			return ResultFilter.availableOnly(statResults)
		if f == ResultFilter.FilterOnOff:
			return ResultFilter.onOffStats(statResults)
		mprint("unknown filter %s" % f)
		return ResultPkg.getEmpty()

	@staticmethod
	def availableOnly(statResults: ResultPkg) -> ResultPkg:
		if statResults.what != ResultPkg.Original and not statResults.isEmpty():
			eprint("input should be an original and not empty")
			return
		out = ResultPkg([])
		out.what = ResultPkg.FilterRc
		out.subtype = ResultFilter.FilterAvailable
		for rc in statResults.content:
			if rc["available"]:
				out.content.append(rc['url'])
		return out

	@staticmethod
	def onOffStats(statResults: ResultPkg) -> ResultPkg:
		if statResults.what != ResultPkg.Original and not statResults.isEmpty():
			eprint("input should be an original and not empty")
			return
		out = ResultPkg({})
		out.what = ResultPkg.FilterRc
		out.subtype = ResultFilter.FilterOnOff
		for rc in statResults.content:
			out.content[rc['url']] = rc["available"]
		return out