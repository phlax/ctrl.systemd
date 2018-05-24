
from configparser import RawConfigParser

from zope import component

from ctrl.config.interfaces import ICtrlConfig


class M(dict):

    def __setitem__(self, key, value):
        if key in self:
            items = self[key]
            if isinstance(items, str):
                items = [items]
            items.append(value)
            value = items
        super(M, self).__setitem__(key, value)

    def items(self):
        items = super(M, self).items()
        _items = []
        for k, v in items:
            if isinstance(v, list):
                for _v in v:
                    _items.append((k, _v))
            else:
                _items.append((k, v))
        return tuple(_items)


class SystemdServiceConfiguration(object):
    start_command = None
    stop_command = None
    wait_command = None

    def __init__(self, name, **kwargs):
        self.name = name
        self.upstream_socket = kwargs.get('upstream_socket')
        self.prefix = kwargs.get('prefix', 'controller')
        self.project = kwargs.get('project', 'apps')
        self.description = kwargs.get('description', '')
        self.service = kwargs.get('service', '')
        self.services = kwargs.get('services', [self.service])
        self.remain_after_exit = kwargs.get('remain_after_exit', True)
        self.private_tmp = kwargs.get('private_tmp', True)
        self.start_command = kwargs.get('start_command', self.start_command)
        self.stop_command = kwargs.get('stop_command', self.stop_command)
        self.wait_command = kwargs.get('wait_command', self.wait_command)

    @property
    def config(self):
        return component.getUtility(ICtrlConfig).config

    @property
    def ctrl_name(self):
        return (
            '%s-%s' % (self.prefix, self.name)
            if self.prefix
            else self.name)

    @property
    def env_vars(self):
        with open('/var/lib/controller/env') as f:
            for line in f.readlines():
                if line.strip():
                    yield line.strip()

    def generate_service_config(self):
        upstream_config = RawConfigParser(dict_type=M)
        upstream_config.optionxform = str
        upstream_config.add_section('Unit')
        upstream_config.set('Unit', 'Description', self.description)
        setup_timer = (
            self.config.has_option('controller', 'idle-timeout')
            and not (
                self.config.get('controller', 'idle-timeout')
                == 'infinity'))
        if setup_timer:
            upstream_config.set('Unit', 'Requires', 'idle.timer')
            upstream_config.set('Unit', 'After', 'idle.timer')
        upstream_config.add_section('Service')
        upstream_config.set(
            'Service',
            'ExecStart',
            '%s %s %s %s %s %s'
            % (self.start_command,
               self.project,
               self.name,
               self.upstream_socket,
               self.service,
               " ".join(self.services)))
        if self.wait_command:
            upstream_config.set(
                'Service',
                'ExecStartPost',
                "%s %s %s %s %s"
                % (self.wait_command,
                   self.project,
                   self.name,
                   self.upstream_socket,
                   self.service))
        if self.stop_command:
            upstream_config.set(
                'Service',
                'ExecStop',
                '%s %s %s %s %s'
                % (self.stop_command,
                   self.project,
                   self.name,
                   self.upstream_socket,
                   self.service))
        if self.private_tmp:
            upstream_config.set('Service', 'PrivateTmp', 'true')
        for env_var in self.env_vars:
            upstream_config.set('Service', 'Environment', env_var)
        if self.remain_after_exit:
            upstream_config.set('Service', 'RemainAfterExit', 'true')

        upstream_config.write(
            open('/etc/systemd/system/%s.service' % self.ctrl_name, 'w'))

    def update_config(self):
        self.generate_service_config()


class SystemdProxyServiceConfiguration(SystemdServiceConfiguration):
    start_command = '/usr/local/bin/start-service'
    stop_command = '/usr/local/bin/stop-service'
    wait_command = '/usr/local/bin/wait-for-service'

    def __init__(self, name, listen_socket, upstream_socket, **kwargs):
        super(SystemdProxyServiceConfiguration, self).__init__(
            name, upstream_socket=upstream_socket, **kwargs)
        self.listen_socket = listen_socket

    def generate_socket_config(self):
        socket_config = RawConfigParser(dict_type=M)
        socket_config.optionxform = str
        socket_config.add_section('Socket')
        socket_config.set('Socket', 'ListenStream', self.listen_socket)
        socket_config.add_section('Install')
        socket_config.set('Install', 'WantedBy', 'sockets.target')
        socket_path = '%s--proxy.socket' % self.ctrl_name
        socket_config.write(
            open('/etc/systemd/system/%s' % socket_path, 'w'))

    def generate_proxy_config(self):
        service_config = RawConfigParser(dict_type=M)
        service_config.optionxform = str
        service_config.add_section('Unit')
        service_config.set(
            'Unit',
            'Requires',
            '%s.service' % self.ctrl_name)
        service_config.set(
            'Unit',
            'After',
            '%s.service' % self.ctrl_name)
        service_config.add_section('Service')
        service_config.set(
            'Service',
            'ExecStart',
            '/usr/local/bin/start-proxy %s' % self.upstream_socket)
        service_config.set('Service', 'PrivateTmp', 'yes')
        service_config.set(
            'Service',
            'PrivateNetwork',
            ('yes'
             if (self.listen_socket.startswith('/')
                 and self.upstream_socket.startswith('/'))
             else 'no'))
        service_config.write(
            open('/etc/systemd/system/%s--proxy.service'
                 % self.ctrl_name,
                 'w'))

    def update_config(self):
        self.generate_socket_config()
        self.generate_proxy_config()
        if self.service:
            super(SystemdProxyServiceConfiguration, self).update_config()
