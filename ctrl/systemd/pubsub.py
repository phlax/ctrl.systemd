
import asyncio

from zope import component

import zmq

from ctrl.core.interfaces import ICtrlApp
from ctrl.config.interfaces import ICtrlConfig
from ctrl.zmq.base import ZMQService
from .listener import SystemdListener


class SystemdZMQPublisher(ZMQService):
    protocol = zmq.PUB
    wait_on_start = .1
    bind = False

    @property
    def config(self):
        return component.getUtility(ICtrlConfig).config

    @property
    def services(self):
        sections = [
            s for s
            in self.config.sections()
            if s.startswith('service:')]
        for section in sections:
            yield section[8:]

    async def emit_systemd(self, message):
        # timestamp = message['__REALTIME_TIMESTAMP']
        unit = message['_SYSTEMD_UNIT'].split('-')[1].split('.')[0]
        action = message['MESSAGE']
        message = (
            "%s %s %s"
            % (self.subscription, action, unit))
        print('Sending: %s' % message)
        await self.sock.send_multipart(
            [message.encode("utf-8")])

    def filter_systemd(self, journal):
        for service in self.services:
            journal.add_match(
                _SYSTEMD_UNIT="controller-%s.service" % service)
        for k in ['starting', 'started', 'stopping', 'stopped']:
            journal.add_match(MESSAGE=k.upper())

    def listen_systemd(self, loop):
        print('Creating systemd listener')
        SystemdListener(self.emit_systemd, self.filter_systemd, loop).listen()

    async def run(self, subscribe, *args):
        app = component.getUtility(ICtrlApp)
        await app.setup(['ctrl.config'])

        self.subscription = subscribe
        self.listen_systemd(self.loop)
        asyncio.ensure_future(self.handle())
        return 'Subscribed %s (%s)' % (subscribe, self)

    async def handle(self, *args):
        recv = await self.sock.recv_multipart()
        subscription = recv[0].split()[0]
        msg = ' '.join(recv[0].decode('utf-8').split()[1:])
        print("Received (%s): %s" % (subscription, msg))
        asyncio.ensure_future(self.handle())
