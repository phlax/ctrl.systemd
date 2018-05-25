from zope import interface

import dbussy

from ctrl.core.interfaces import ISystemctl


@interface.implementer(ISystemctl)
class SystemdSystemctl(object):

    async def get_connection(self):
        return await dbussy.Connection.bus_get_async(
            dbussy.DBUS.BUS_SYSTEM, private=False)

    async def send_await_reply(self, method, *args):
        conn = await self.get_connection()
        message = dbussy.Message.new_method_call(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            iface='org.freedesktop.systemd1.Manager',
            method=method)
        message.append_objects(*args)
        return await conn.send_await_reply(message)

    async def daemon_reload(self):
        print("Reloading daemons")
        # busctl call org.freedesktop.systemd1 /org/freedesktop/systemd1
        # org.freedesktop.systemd1.Manager Reload
        return await self.send_await_reply('Reload', '')

    async def start(self, service):
        reply = await self.send_await_reply(
            'StartUnit',
            'ss',
            service,
            'replace')
        print(repr(reply.all_objects))
        return 'Service (%s) started' % service

    async def stop(self, service):
        # whod have thought itd be so damn difficult
        # to stop a systemd unit
        print("Systemctl stopping %s" % service)
        # busctl call org.freedesktop.systemd1 /org/freedesktop/systemd1
        # org.freedesktop.systemd1.Manager
        # StopUnit ss "controller-translate.service" "replace"
        reply = await self.send_await_reply(
            'StopUnit',
            'ss',
            service,
            'replace')
        print(repr(reply.all_objects))
        return 'Service (%s) stopped' % service

    async def status(self, service):
        pass
