
import json
import os

from zope import interface

import dbussy

from ctrl.core.interfaces import ISystemctl


@interface.implementer(ISystemctl)
class SystemdSystemctl(object):

    async def get_connection(self):
        return await dbussy.Connection.bus_get_async(
            dbussy.DBUS.BUS_SYSTEM, private=False)

    async def send_await_reply(self, method: str, *args):
        conn = await self.get_connection()
        message = dbussy.Message.new_method_call(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            iface='org.freedesktop.systemd1.Manager',
            method=method)
        message.append_objects(*args)
        return await conn.send_await_reply(message)

    async def daemon_reload(self):
        reply = await self.send_await_reply('Reload', '')
        print(repr(reply.all_objects))

    async def start(self, service: str):
        reply = await self.send_await_reply(
            'StartUnit',
            'ss',
            service,
            'replace')
        print(repr(reply.all_objects))
        return 'Service (%s) started' % service

    async def stop(self, service: str):
        # whod have thought itd be so damn difficult
        # to stop a systemd unit
        # busctl call org.freedesktop.systemd1 /org/freedesktop/systemd1
        # org.freedesktop.systemd1.Manager
        # StopUnit ss "controller-translate.service" "replace"
        reply = await self.send_await_reply(
            'StopUnit',
            'ss',
            service,
            'replace')
        print(repr(reply.all_objects))

    async def services(self):
        reply = await self.send_await_reply('ListUnits', '')
        configured = [
            x for x
            in reply.all_objects[0]
            if x[0].startswith("ctrl.")]
        if os.path.exists("/var/lib/ctrl/services"):
            with open("/var/lib/ctrl/services") as f:
                services = json.loads(f.read())
        else:
            services = {}
        print("configured", configured)
        print("services", services)

    async def configure(self):
        print("configuring SERVICES in utility")

    async def enable(self, service: str):
        print("enabling SERVICE in utility: %s" % service)

    async def disable(self, service: str):
        print("disabling SERVICE in utility: %s" % service)
