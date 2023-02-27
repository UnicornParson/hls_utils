import time
import sys

class CTimingUtil:
  timingLoggerWrapper = None

  @staticmethod
  def timing_impl(f):
      def wrap(*args, **kwargs):
          time1 = time.time()
          sarg = str(args)
          skwarg = str(kwargs)
          ret = f(*args, **kwargs)
          time2 = time.time()
          msg = '{:s} function took {:.3f} ms. args({:s},k: {:s})'.format(f.__name__, ((time2 - time1) * 1000.0), sarg, skwarg)
          if CTimingUtil.timingLoggerWrapper:
            CTimingUtil.timingLoggerWrapper.verboseLog(msg)
          else:
            print("no logger")
            sys.exit(-1)
          return ret
      return wrap

