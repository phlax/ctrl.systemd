
from zope import component, interface

from ctrl.core.interfaces import (
    ISystemctl, ISubcommand)


@interface.implementer(ISubcommand)
class SystemdSubcommand(object):

    def __init__(self, context):
        self.context = context

    @property
    def systemctl(self):
        return component.getUtility(ISystemctl)

    async def handle(self, command: str, *args, **kwargs):
        return await getattr(
            self,
            'handle_%s'
            % command.replace("-", "_"))(*args, **kwargs)

    async def handle_services(self, *args, **kwargs):
        await self.systemctl.services()

    async def handle_configure(self, *args, **kwargs):
        await self.systemctl.configure()

    async def handle_enable(self, service: str, *args, **kwargs):
        await self.systemctl.enable(service)

    async def handle_start(self, service: str, *args, **kwargs):
        await self.systemctl.start(service)

    async def handle_stop(self, service: str, *args, **kwargs):
        await self.systemctl.stop(service)

    async def handle_disable(self, service: str, *args, **kwargs):
        await self.systemctl.disable(service)

    async def handle_daemon_reload(self, *args, **kwargs):
        await self.systemctl.daemon_reload()
