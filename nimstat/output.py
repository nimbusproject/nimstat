from datetime import datetime
import sys

__author__ = 'bresnaha'


class Spinner(object):

    def __init__(self, interval=0.5):
        self._interval = interval
        self._count = 0
        self._already = 0
        self._chars = "|/-\\"
        self._last_time = datetime.now()
        self._spin_ndx = 0

    def _update(self):
        now = datetime.now()
        timedif = now - self._last_time
        span = float("%d.%d" % (timedif.seconds, timedif.microseconds))
        if span < self._interval:
            return None

        msg = "%s | new: %d | already in %d" % (self._chars[self._spin_ndx], self._count, self._already)
        self._spin_ndx = self._spin_ndx + 1
        if self._spin_ndx >= len(self._chars):
            self._spin_ndx = 0
        self._last_time = now

        sys.stdout.write("\r %s" % (msg))
        sys.stdout.flush()

        return msg

    def already(self):
        self._already = self._already + 1
        return self._update()

    def next(self):
        self._count = self._count + 1
        return self._update()

        


