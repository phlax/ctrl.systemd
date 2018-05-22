
from zope import component

from ctrl.core.interfaces import ICtrlExtension
from .extension import CtrlSystemdExtension


# register the extension
component.provideUtility(
    CtrlSystemdExtension(),
    ICtrlExtension,
    'systemd')
