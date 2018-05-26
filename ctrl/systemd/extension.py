
from zope import component

from ctrl.core.extension import CtrlExtension
from ctrl.core.interfaces import (
    IConfiguration, ICtrlExtension, ISystemctl)

from .config import SystemdConfiguration
from .systemctl import SystemdSystemctl


class CtrlSystemdExtension(CtrlExtension):

    async def register_utilities(self):
        component.provideUtility(
            SystemdConfiguration(),
            provides=IConfiguration,
            name='systemd')

        component.provideUtility(
            SystemdSystemctl(),
            provides=ISystemctl)


# register the extension
component.provideUtility(
    CtrlSystemdExtension(),
    ICtrlExtension,
    'systemd')
