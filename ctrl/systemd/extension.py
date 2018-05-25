
from zope import component

from ctrl.config.interfaces import IConfiguration

from .config import SystemdConfiguration
from .interfaces import ISysctl
from .sysctl import SystemdSysctl


class CtrlSystemdExtension(object):

    async def register(self, app):
        component.provideUtility(
            SystemdConfiguration(),
            provides=IConfiguration,
            name='systemd')

        component.provideUtility(
            SystemdSysctl(),
            provides=ISysctl)
