from zope import interface

import dbussy

from .interfaces import ISysctl


@interface.implementer(ISysctl)
class SystemdSysctl(object):

    async def await_send_reply(self, method, *args):
        conn = await self.get_connection()
        message = dbussy.Message.new_method_call(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            iface='org.freedesktop.systemd1.Manager',
            method=method)
        message.append_objects(*args)
        return await conn.send_await_reply(message)

    async def get_connection(self):
        return await dbussy.Connection.bus_get_async(
            dbussy.DBUS.BUS_SYSTEM, private=False)

    async def daemon_reload(self):
        print("Reloading daemons")
        # busctl call org.freedesktop.systemd1 /org/freedesktop/systemd1
        # org.freedesktop.systemd1.Manager Reload
        return await self.send_await_reply('Reload')

    async def start(self, service):
        pass

    async def stop(self, service):
        # whod have thought itd be so damn difficult
        # to stop a systemd unit
        print("Sysctl stopping %s" % service)
        # busctl call org.freedesktop.systemd1 /org/freedesktop/systemd1
        # org.freedesktop.systemd1.Manager
        # StopUnit ss "controller-translate.service" "replace"
        reply = await self.send_await_reply(
            'StopUnit',
            'ss',
            'controller-%s.service' % service,
            'replace')
        print(repr(reply.all_objects))
        return 'Service (%s) stopped' % service

    async def status(self, service):
        pass
