
from zope import component

from ctrl.core.extension import CtrlExtension
from ctrl.core.interfaces import (
    ICommandRunner, IConfiguration, ICtrlExtension,
    ISubcommand, ISystemctl)

from .command import SystemdSubcommand
from .config import SystemdConfiguration
from .systemctl import SystemdSystemctl


class CtrlSystemdExtension(CtrlExtension):

    def register_adapters(self):
        component.provideAdapter(
            factory=SystemdSubcommand,
            adapts=[ICommandRunner],
            provides=ISubcommand,
            name='systemd')

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
