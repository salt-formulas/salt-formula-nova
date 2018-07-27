#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import six
from six.moves import zip_longest

import salt

LOG = logging.getLogger(__name__)

KEYSTONE_LOADED = False


def __virtual__():
    """Only load if the nova module is in __salt__"""
    if 'keystonev3.project_get_details' in __salt__:
        global KEYSTONE_LOADED
        KEYSTONE_LOADED = True
    return 'novav21'


class SaltModuleCallException(Exception):

    def __init__(self, result_dict, *args, **kwargs):
        super(SaltModuleCallException, self).__init__(*args, **kwargs)
        self.result_dict = result_dict


def _get_failure_function_mapping():
    return {
        'create': _create_failed,
        'update': _update_failed,
        'find': _find_failed,
        'delete': _delete_failed,
    }


def _call_nova_salt_module(call_string, name, module_name='novav21'):
    def inner(*args, **kwargs):
        func = __salt__['%s.%s' % (module_name, call_string)]
        result = func(*args, **kwargs)
        if not result['result']:
            ret = _get_failure_function_mapping()[func._action_type](
                name, func._resource_human_readable_name)
            ret['comment'] += '\nStatus code: %s\n%s' % (result['status_code'],
                                                         result['comment'])
            raise SaltModuleCallException(ret)
        return result['body'].get(func._body_response_key)
    return inner


def _error_handler(fun):
    @six.wraps(fun)
    def inner(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except SaltModuleCallException as e:
            return e.result_dict
    return inner


@_error_handler
def flavor_present(name, cloud_name, vcpus=1, ram=256, disk=0, flavor_id=None,
                   extra_specs=None):
    """Ensures that the flavor exists"""
    extra_specs = extra_specs or {}
    # There is no way to query flavors by name
    flavors = _call_nova_salt_module('flavor_list', name)(
        detail=True, cloud_name=cloud_name)
    flavor = [flavor for flavor in flavors if flavor['name'] == name]
    # Flavor names are unique, there is either 1 or 0 with requested name
    if flavor:
        flavor = flavor[0]
        current_extra_specs = _call_nova_salt_module(
            'flavor_get_extra_specs', name)(
                flavor['id'], cloud_name=cloud_name)
        to_delete = set(current_extra_specs) - set(extra_specs)
        to_add = set(extra_specs) - set(current_extra_specs)
        for spec in to_delete:
            _call_nova_salt_module('flavor_delete_extra_spec', name)(
                flavor['id'], spec, cloud_name=cloud_name)
        _call_nova_salt_module('flavor_add_extra_specs', name)(
            flavor['id'], cloud_name=cloud_name, **extra_specs)
        if to_delete or to_add:
            ret = _updated(name, 'Flavor', extra_specs)
        else:
            ret = _no_change(name, 'Flavor')
    else:
        flavor = _call_nova_salt_module('flavor_create', name)(
            name, vcpus, ram, disk, id=flavor_id, cloud_name=cloud_name)
        _call_nova_salt_module('flavor_add_extra_specs', name)(
            flavor['id'], cloud_name=cloud_name, **extra_specs)
        flavor['extra_specs'] = extra_specs
        ret = _created(name, 'Flavor', flavor)
    return ret


@_error_handler
def flavor_absent(name, cloud_name):
    """Ensure flavor is absent"""
    # There is no way to query flavors by name
    flavors = _call_nova_salt_module('flavor_list', name)(
        detail=True, cloud_name=cloud_name)
    flavor = [flavor for flavor in flavors if flavor['name'] == name]
    # Flavor names are unique, there is either 1 or 0 with requested name
    if flavor:
        _call_nova_salt_module('flavor_delete', name)(
            flavor[0]['id'], cloud_name=cloud_name)
        return _deleted(name, 'Flavor')
    return _non_existent(name, 'Flavor')


def _get_keystone_project_id_by_name(project_name, cloud_name):
    if not KEYSTONE_LOADED:
        LOG.error("Keystone module not found, can not look up project ID "
                  "by name")
        return None
    project = __salt__['keystonev3.project_get_details'](
        project_name, cloud_name=cloud_name)
    if not project:
        return None
    return project['project']['id']


@_error_handler
def quota_present(name, cloud_name, **kwargs):
    """Ensures that the nova quota exists

    :param name: project name to ensure quota for.
    """
    project_name = name
    project_id = _get_keystone_project_id_by_name(project_name, cloud_name)
    changes = {}
    if not project_id:
        ret = _update_failed(project_name, 'Project quota')
        ret['comment'] += ('\nCould not retrieve keystone project %s' %
                           project_name)
        return ret
    quota = _call_nova_salt_module('quota_list', project_name)(
        project_id, cloud_name=cloud_name)
    for key, value in kwargs.items():
        if quota.get(key) != value:
            changes[key] = value
    if changes:
        _call_nova_salt_module('quota_update', project_name)(
            project_id, cloud_name=cloud_name, **changes)
        return _updated(project_name, 'Project quota', changes)
    else:
        return _no_change(project_name, 'Project quota')


@_error_handler
def quota_absent(name, cloud_name):
    """Ensures that the nova quota set to default

    :param name: project name to reset quota for.
    """
    project_name = name
    project_id = _get_keystone_project_id_by_name(project_name, cloud_name)
    if not project_id:
        ret = _delete_failed(project_name, 'Project quota')
        ret['comment'] += ('\nCould not retrieve keystone project %s' %
                           project_name)
        return ret
    _call_nova_salt_module('quota_delete', name)(
        project_id, cloud_name=cloud_name)
    return _deleted(name, 'Project quota')


@_error_handler
def aggregate_present(name, cloud_name, availability_zone_name=None,
                      hosts=None, metadata=None):
    """Ensures that the nova aggregate exists"""
    aggregates = _call_nova_salt_module('aggregate_list', name)(
        cloud_name=cloud_name)
    aggregate_exists = [agg for agg in aggregates
                        if agg['name'] == name]
    metadata = metadata or {}
    hosts = hosts or []
    if availability_zone_name:
        metadata.update(availability_zone=availability_zone_name)
    if not aggregate_exists:
        aggregate = _call_nova_salt_module('aggregate_create', name)(
            name, availability_zone_name, cloud_name=cloud_name)
        if metadata:
            _call_nova_salt_module('aggregate_set_metadata', name)(
                cloud_name=cloud_name, **metadata)
            aggregate['metadata'] = metadata
        for host in hosts or []:
            _call_nova_salt_module('aggregate_add_host', name)(
                name, host, cloud_name=cloud_name)
            aggregate['hosts'] = hosts
        return _created(name, 'Host aggregate', aggregate)
    else:
        aggregate = aggregate_exists[0]
        changes = {}
        existing_meta = set(aggregate['metadata'].items())
        requested_meta = set(metadata.items())
        if existing_meta - requested_meta or requested_meta - existing_meta:
            _call_nova_salt_module('aggregate_set_metadata', name)(
                name, cloud_name=cloud_name, **metadata)
            changes['metadata'] = metadata
        hosts_to_add = set(hosts) - set(aggregate['hosts'])
        hosts_to_remove = set(aggregate['hosts']) - set(hosts)
        if hosts_to_remove or hosts_to_add:
            for host in hosts_to_add:
                _call_nova_salt_module('aggregate_add_host', name)(
                    name, host, cloud_name=cloud_name)
            for host in hosts_to_remove:
                _call_nova_salt_module('aggregate_remove_host', name)(
                    name, host, cloud_name=cloud_name)
            changes['hosts'] = hosts
        if changes:
            return _updated(name, 'Host aggregate', changes)
        else:
            return _no_change(name, 'Host aggregate')


@_error_handler
def aggregate_absent(name, cloud_name):
    """Ensure aggregate is absent"""
    existing_aggregates = _call_nova_salt_module('aggregate_list', name)(
        cloud_name=cloud_name)
    matching_aggs = [agg for agg in existing_aggregates
                     if agg['name'] == name]
    if matching_aggs:
        _call_nova_salt_module('aggregate_delete', name)(
            name, cloud_name=cloud_name)
        return _deleted(name, 'Host Aggregate')
    return _non_existent(name, 'Host Aggregate')


@_error_handler
def keypair_present(name, cloud_name, public_key_file=None, public_key=None):
    """Ensures that the Nova key-pair exists"""
    existing_keypairs = _call_nova_salt_module('keypair_list', name)(
        cloud_name=cloud_name)
    matching_kps = [kp for kp in existing_keypairs
                    if kp['keypair']['name'] == name]
    if public_key_file and not public_key:
        with salt.utils.fopen(public_key_file, 'r') as f:
            public_key = f.read()
    if not public_key:
        ret = _create_failed(name, 'Keypair')
        ret['comment'] += '\nPlease specify public key for keypair creation.'
        return ret
    if matching_kps:
        # Keypair names are unique, there is either 1 or 0 with requested name
        kp = matching_kps[0]['keypair']
        if kp['public_key'] != public_key:
            _call_nova_salt_module('keypair_delete', name)(
                name, cloud_name=cloud_name)
        else:
            return _no_change(name, 'Keypair')
    res = _call_nova_salt_module('keypair_create', name)(
        name, cloud_name=cloud_name, public_key=public_key)
    return _created(name, 'Keypair', res)


@_error_handler
def keypair_absent(name, cloud_name):
    """Ensure keypair is absent"""
    existing_keypairs = _call_nova_salt_module('keypair_list', name)(
        cloud_name=cloud_name)
    matching_kps = [kp for kp in existing_keypairs
                    if kp['keypair']['name'] == name]
    if matching_kps:
        _call_nova_salt_module('keypair_delete', name)(
            name, cloud_name=cloud_name)
        return _deleted(name, 'Keypair')
    return _non_existent(name, 'Keypair')


def cell_present(name='cell1', transport_url='none:///', db_engine='mysql',
                 db_name='nova_upgrade', db_user='nova', db_password=None,
                 db_address='0.0.0.0'):
    """Ensure nova cell is present

    For newly created cells this state also runs discover_hosts and
    map_instances."""
    cell_info = __salt__['cmd.shell'](
        "nova-manage cell_v2 list_cells --verbose | "
        "awk '/%s/ {print $4,$6,$8}'" % name).split()
    db_connection = (
        '%(db_engine)s+pymysql://%(db_user)s:%(db_password)s@'
        '%(db_address)s/%(db_name)s?charset=utf8' % {
            'db_engine': db_engine, 'db_user': db_user,
            'db_password': db_password, 'db_address': db_address,
            'db_name': db_name})
    args = {'transport_url': transport_url, 'db_connection': db_connection}
    # There should be at least 1 component printed to cell_info
    if len(cell_info) >= 1:
        cell_info = dict(zip_longest(
            ('cell_uuid', 'existing_transport_url', 'existing_db_connection'),
            cell_info))
        cell_uuid, existing_transport_url, existing_db_connection = cell_info
        command_string = ''
        if existing_transport_url != transport_url:
            command_string = (
                '%s --transport-url %%(transport_url)s' % command_string)
        if existing_db_connection != db_connection:
            command_string = (
                '%s --database_connection %%(db_connection)s' % command_string)
        if not command_string:
            return _no_change(name, 'Nova cell')
        try:
            __salt__['cmd.shell'](
                ('nova-manage cell_v2 update_cell --cell_uuid %s %s' % (
                    cell_uuid, command_string)) % args)
            LOG.warning("Updating the transport_url or database_connection "
                        "fields on a running system will NOT result in all "
                        "nodes immediately using the new values. Use caution "
                        "when changing these values.")
            ret = _updated(name, 'Nova cell', args)
        except Exception as e:
            ret = _update_failed(name, 'Nova cell')
            ret['comment'] += '\nException: %s' % e
        return ret
    args.update(name=name)
    try:
        cell_uuid = __salt__['cmd.shell'](
            'nova-manage cell_v2 create_cell --name %(name)s '
            '--transport-url %(transport_url)s '
            '--database_connection %(db_connection)s --verbose' % args)
        __salt__['cmd.shell']('nova-manage cell_v2 discover_hosts '
                              '--cell_uuid %s --verbose' % cell_uuid)
        __salt__['cmd.shell']('nova-manage cell_v2 map_instances '
                              '--cell_uuid %s' % cell_uuid)
        ret = _created(name, 'Nova cell', args)
    except Exception as e:
        ret = _create_failed(name, 'Nova cell')
        ret['comment'] += '\nException: %s' % e
    return ret


def cell_absent(name, force=False):
    """Ensure cell is absent"""
    cell_uuid = __salt__['cmd.shell'](
        "nova-manage cell_v2 list_cells | awk '/%s/ {print $4}'" % name)
    if not cell_uuid:
        return _non_existent(name, 'Nova cell')
    try:
        __salt__['cmd.shell'](
            'nova-manage cell_v2 delete_cell --cell_uuid %s %s' % (
                cell_uuid, '--force' if force else ''))
        ret = _deleted(name, 'Nova cell')
    except Exception as e:
        ret = _delete_failed(name, 'Nova cell')
        ret['comment'] += '\nException: %s' % e
    return ret


def _db_version_update(db, version, human_readable_resource_name):
    existing_version = __salt__['cmd.shell'](
        'nova-manage %s version 2>/dev/null' % db)
    try:
        existing_version = int(existing_version)
        version = int(version)
    except Exception as e:
        ret = _update_failed(existing_version,
                             human_readable_resource_name)
        ret['comment'] += ('\nCan not convert existing or requested version '
                           'to integer, exception: %s' % e)
        LOG.error(ret['comment'])
        return ret
    if existing_version < version:
        try:
            __salt__['cmd.shell'](
                'nova-manage %s sync --version %s' % (db, version))
            ret = _updated(existing_version, human_readable_resource_name,
                           {db: '%s sync --version %s' % (db, version)})
        except Exception as e:
            ret = _update_failed(existing_version,
                                 human_readable_resource_name)
            ret['comment'] += '\nException: %s' % e
        return ret
    return _no_change(existing_version, human_readable_resource_name)


def api_db_version_present(name=None, version="20"):
    """Ensures that specific api_db version is present"""
    return _db_version_update('api_db', version, 'Nova API database version')


def db_version_present(name=None, version="334"):
    """Ensures that specific db version is present"""
    return _db_version_update('db', version, 'Nova database version')


def online_data_migrations_present(name=None, api_db_version="20",
                                   db_version="334"):
    """Runs online_data_migrations if databases are of specific versions"""
    ret = {'name': 'online_data_migrations', 'changes': {}, 'result': False,
           'comment': 'Current nova api_db version != {0} or nova db version '
                      '!= {1}.'.format(api_db_version, db_version)}
    cur_api_db_version = __salt__['cmd.shell'](
        'nova-manage api_db version 2>/dev/null')
    cur_db_version = __salt__['cmd.shell'](
        'nova-manage db version 2>/dev/null')
    try:
        cur_api_db_version = int(cur_api_db_version)
        cur_db_version = int(cur_db_version)
        api_db_version = int(api_db_version)
        db_version = int(db_version)
    except Exception as e:
        LOG.error(ret['comment'])
        ret['comment'] = ('\nCan not convert existing or requested database '
                          'versions to integer, exception: %s' % e)
        return ret
    if cur_api_db_version == api_db_version and cur_db_version == db_version:
        try:
            __salt__['cmd.shell']('nova-manage db online_data_migrations')
            ret['result'] = True
            ret['comment'] = ('nova-manage db online_data_migrations was '
                              'executed successfuly')
            ret['changes']['online_data_migrations'] = (
                'online_data_migrations run on nova api_db version {0} and '
                'nova db version {1}'.format(api_db_version, db_version))
        except Exception as e:
            ret['comment'] = (
                'Failed to execute online_data_migrations on nova api_db '
                'version %s and nova db version %s, exception: %s' % (
                    api_db_version, db_version, e))
    return ret


def _find_failed(name, resource):
    return {
        'name': name, 'changes': {}, 'result': False,
        'comment': 'Failed to find {0}s with name {1}'.format(resource, name)}


def _created(name, resource, changes):
    return {
        'name': name, 'changes': changes, 'result': True,
        'comment': '{0} {1} created'.format(resource, name)}


def _create_failed(name, resource):
    return {
        'name': name, 'changes': {}, 'result': False,
        'comment': '{0} {1} creation failed'.format(resource, name)}


def _no_change(name, resource):
    return {
        'name': name, 'changes': {}, 'result': True,
        'comment': '{0} {1} already is in the desired state'.format(
            resource, name)}


def _updated(name, resource, changes):
    return {
        'name': name, 'changes': changes, 'result': True,
        'comment': '{0} {1} was updated'.format(resource, name)}


def _update_failed(name, resource):
    return {
        'name': name, 'changes': {}, 'result': False,
        'comment': '{0} {1} update failed'.format(resource, name)}


def _deleted(name, resource):
    return {
        'name': name, 'changes': {}, 'result': True,
        'comment': '{0} {1} deleted'.format(resource, name)}


def _delete_failed(name, resource):
    return {
        'name': name, 'changes': {}, 'result': False,
        'comment': '{0} {1} deletion failed'.format(resource, name)}


def _non_existent(name, resource):
    return {
        'name': name, 'changes': {}, 'result': True,
        'comment': '{0} {1} does not exist'.format(resource, name)}
