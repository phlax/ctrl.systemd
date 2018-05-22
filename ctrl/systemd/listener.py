
import asyncio

from systemd import journal


class SystemdListener(object):

    def __init__(self, emit, filter_journal=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.journal = journal.Reader()
        self.journal.seek_tail()
        self.journal.get_previous()
        if filter_journal:
            filter_journal(self.journal)
        self.emit = emit

    def reader(self):
        while True:
            resp = self.journal.get_next()
            if not resp:
                break
            asyncio.ensure_future(self.emit(resp))
        self.journal.process()

    def listen(self):
        self.loop.add_reader(self.journal, self.reader)
