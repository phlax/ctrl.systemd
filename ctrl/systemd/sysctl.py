from zope import interface

import dbussy

from .interfaces import ISysctl


@interface.implementer(ISysctl)
class SystemdSysctl(object):

    async def start(self, service):
        pass

    async def stop(self, service):
        # whod have thought itd be so damn difficult
        # to stop a systemd unit
        print("Sysctl stopping %s" % service)
        # busctl call org.freedesktop.systemd1 /org/freedesktop/systemd1
        # org.freedesktop.systemd1.Manager
        # StopUnit ss "controller-translate.service" "replace"
        conn = await dbussy.Connection.bus_get_async(
            dbussy.DBUS.BUS_SYSTEM, private=False)
        message = dbussy.Message.new_method_call(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            iface='org.freedesktop.systemd1.Manager',
            method='StopUnit')
        message.append_objects(
            'ss',
            'controller-%s.service' % service,
            'replace')
        reply = await conn.send_await_reply(message)
        print(repr(reply.all_objects))
        return 'Service (%s) stopped' % service

    async def status(self, service):
        pass
