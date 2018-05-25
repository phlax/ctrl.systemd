
from zope.interface import Interface


class ISysctl(Interface):

    async def start(service):
        pass

    async def stop(service):
        pass

    async def status(service):
        pass
