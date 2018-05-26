
import os

from zope import component

import yaml

from ctrl.core.interfaces import ICtrlConfig, ISettings

from .service import (
    SystemdProxyServiceConfiguration,
    SystemdServiceConfiguration)


class SystemdConfiguration(object):

    def configure(self):
        self.clear_service_files()
        self.update_systemd()

    @property
    def clients(self):
        sections = [
            s for s
            in self.config
            if s.startswith('client:')]
        for section in sections:
            yield section[7:]

    @property
    def config(self):
        return component.getUtility(ISettings)

    @property
    def services(self):
        sections = [
            s for s
            in self.config
            if s.startswith('service:')]
        for section in sections:
            yield section[8:]

    @property
    def var_path(self):
        var_path = self.config['controller']['var_path']
        if not os.path.exists(var_path):
            os.makedirs(var_path)
        return var_path

    def append_touch_files(self, name):
        idle_files = self.config['service:%s' % name].getlist('idle-files')
        with open(os.path.join(self.var_path, 'idle-files'), 'a') as f:
            f.write('%s %s' % (name, ' '.join(idle_files)))

    def clear_service_files(self):
        files = [
            x for x
            in os.listdir('/etc/systemd/system')
            if x.startswith('controller-')]
        for f in files:
            os.unlink('/etc/systemd/system/%s' % f)

    def generate_compose_file(self, name):
        var_path = os.path.join(self.var_path, name)
        if not os.path.exists(var_path):
            os.makedirs(var_path)
        config = component.getUtility(ICtrlConfig, 'compose').config

        new_config = dict(services={}, volumes={}, networks={})
        extra_services = []
        for service in self.get_services(name):
            if not config['services'].get(service):
                continue
            new_config['services'][service] = dict(config['services'][service])
            for volume in new_config['services'][service].get('volumes', []):
                if volume.startswith('/'):
                    continue
                new_config['volumes'][volume.split(':')[0]] = {}
            has_extra_services = config['services'][service].get(
                'network_mode', '').startswith('service:')
            if has_extra_services:
                extra_services.append(
                    config['services'][service]['network_mode'][8:])
            networks = new_config['services'][service].get(
                'networks', [])
            for network in networks:
                if network.startswith('/'):
                    continue
                new_config['networks'][network.split(':')[0]] = {}
        for service in extra_services:
            new_config['services'][service] = dict(
                config['services'][service])
        new_config['version'] = config['version']
        yaml.dump(
            new_config,
            open(os.path.join(var_path, 'docker-compose.yml'), 'w'),
            default_flow_style=False)

    def generate_daemon_compose_file(self, config, startup_config):
        daemons = [
            d for d
            in self.config['controller'].getlist('daemons')
            if d]
        if not daemons:
            return
        extra_services = []
        for daemon in daemons:
            if not config['services'][daemon]:
                print('No config for daemon: %s' % daemon)
                continue
            startup_config['services'][daemon] = dict(
                config['services'][daemon])
            has_extra_services = config['services'][daemon].get(
                'network_mode', '').startswith('service:')
            if has_extra_services:
                extra_services.append(
                    config['services'][daemon]['network_mode'][8:])
        for service in extra_services:
            startup_config['services'][service] = dict(
                config['services'][service])

        startup_config['volumes'] = dict(config.get('volumes', {}))
        startup_config['networks'] = dict(config.get('networks', {}))
        if startup_config['networks'].get('default'):
            subnet = startup_config[
                'networks']['default'][
                    'ipam']['config'][0]['subnet'].split('.')
            subnet[2] = '100'
            startup_config[
                'networks']['default'][
                    'ipam']['config'][0]['subnet'] = '.'.join(subnet)

    def generate_client_compose_file(self, config, startup_config):
        for client in self.clients:
            startup_config['services'][client] = dict(
                config['services'].get(client, {}))

    def generate_system_compose_file(self):
        var_path = self.var_path
        compose_config = component.getUtility(
            ICtrlConfig, 'compose').config
        startup_config = dict(
            services={}, volumes={}, networks={})
        self.generate_daemon_compose_file(
            compose_config, startup_config)
        self.generate_client_compose_file(
            compose_config, startup_config)
        startup_config['version'] = compose_config['version']
        yaml.dump(
            startup_config,
            open(os.path.join(var_path, 'docker-compose.yml'), 'w'),
            default_flow_style=False)

    def generate_service_files(self, name):
        context = self.config['controller']['context']
        project = (
            self.config['controller'].get('name')
            or os.path.basename(context))
        listen_socket = self.config['service:%s' % name]['listen']
        description = self.config['service:%s' % name]['description']
        upstream_socket = (
            self.config['service:%s' % name].get('socket')
            or '/sockets/%s.sock' % name)
        service = self.get_service(name)
        services = self.get_services(name)
        SystemdProxyServiceConfiguration(
            name,
            listen_socket,
            upstream_socket,
            service=service,
            services=services,
            description=description,
            project=project).update_config()

    def get_services(self, name):
        return [
            ('%s-%s' % (s, name))
            for s
            in self.config['service:%s' % name]['services'].split(" ")
            if s] or [self.get_service(name)]

    def get_service(self, name):
        service = self.config['service:%s' % name]['service']
        return (
            "%s-%s" % (service, name)
            if service
            else name)

    def set_timeout_file(self):
        with open(os.path.join(self.var_path, 'idle-timeout'), 'w') as f:
            f.write(self.config['controller']['idle-timeout'])

    def setup_zmq_pipes(self):
        if 'zmq-listen' in self.config['controller']:
            listen_socket = self.config['controller']['zmq-listen']
            upstream_socket = '/sockets/zmq-rpc.sock'
            if listen_socket.startswith('ipc:///'):
                listen_socket = listen_socket[6:]
            print('Configuring zmq rpc listener on: %s'
                  % listen_socket)
            SystemdProxyServiceConfiguration(
                'rpc',
                listen_socket,
                upstream_socket,
                service='zmq-rpc',
                start_command='/usr/local/bin/start-zmq',
                wait_command='/usr/local/bin/wait-for-zmq',
                stop_command='/usr/local/bin/stop-zmq',
                env_vars=(
                    ('CTRL_MODULES', 'ctrl.zmq'),
                    ('PYTHONPATH', '/controller/src')),
                prefix='zmq').update_config()
        if 'zmq-publish' in self.config['controller']:
            socket, subscription = (
                self.config['controller']['zmq-publish'].split(' '))
            print('Publishing events to zmq subscriber: %s'
                  % socket)
            SystemdServiceConfiguration(
                'publish',
                service=subscription,
                upstream_socket=socket,
                start_command='/usr/local/bin/start-zmq',
                wait_command='/usr/local/bin/wait-for-zmq',
                stop_command='/usr/local/bin/stop-zmq',
                env_vars=(
                    ('CTRL_MODULES', 'ctrl.zmq'),
                    ('PYTHONPATH', '/controller/src')),
                prefix='zmq').update_config()

    def create_env_file(self):
        if 'controller' not in self.config:
            return
        print('Creating env file')
        env = (
            'COMPOSE_CONTEXT=%s\nDOCKER_HOST=%s'
            % (self.config['controller']['context'],
               'unix:///fat/docker.sock'))
        open('/etc/controller.env', 'w').write(env)

    def update_systemd(self):
        self.create_env_file()
        self.generate_system_compose_file()
        self.set_timeout_file()
        self.setup_zmq_pipes()
        for name in self.services:
            self.generate_service_files(name)
            self.generate_compose_file(name)
            self.append_touch_files(name)
