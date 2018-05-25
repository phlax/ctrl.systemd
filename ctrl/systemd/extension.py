
from zope import component

from ctrl.core.interfaces import IConfiguration, ISystemctl

from .config import SystemdConfiguration
from .systemctl import SystemdSystemctl


class CtrlSystemdExtension(object):

    async def register(self, app):
        component.provideUtility(
            SystemdConfiguration(),
            provides=IConfiguration,
            name='systemd')

        component.provideUtility(
            SystemdSystemctl(),
            provides=ISystemctl)
