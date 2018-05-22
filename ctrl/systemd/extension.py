
from zope import component

from ctrl.config.interfaces import IConfiguration

from .config import SystemdConfiguration


class CtrlSystemdExtension(object):

    async def register(self, app):
        component.provideUtility(
            SystemdConfiguration(),
            provides=IConfiguration,
            name='systemd')
