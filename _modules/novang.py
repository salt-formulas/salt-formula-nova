# -*- coding: utf-8 -*-
from __future__ import absolute_import
from pprint import pprint

# Import python libs
import logging

# Import salt libs
import salt.utils.openstack.nova as suon
from salt.utils.decorators import depends

# Get logging started
log = logging.getLogger(__name__)

# Function alias to not shadow built-ins
__func_alias__ = {
    'list_': 'list'
}

# Define the module's virtual name
__virtualname__ = 'novang'

try:
    import novaclient
    HAS_NOVA = True
except:
    HAS_NOVA = False

try:
    import keystoneauth1
    HAS_KEYSTONE = True
except:
    HAS_KEYSTONE = False

HAS_SALTNOVA = suon.check_nova()


def __virtual__():
    '''
    Only load this module if nova
    is installed on this minion.
    '''
    if HAS_SALTNOVA or HAS_NOVA:
        return __virtualname__
    return (False, 'The nova execution module failed to load: '
            'only available if nova is installed.')


__opts__ = {}


def _auth(profile=None, tenant_name=None):
    '''
    Set up nova credentials
    '''
    if profile:
        credentials = __salt__['config.option'](profile)
        user = credentials['keystone.user']
        password = credentials['keystone.password']
        if tenant_name:
            tenant = tenant_name
        else:
            tenant = credentials['keystone.tenant']
        auth_url = credentials['keystone.auth_url']
        region_name = credentials.get('keystone.region_name', None)
        api_key = credentials.get('keystone.api_key', None)
        os_auth_system = credentials.get('keystone.os_auth_system', None)
    else:
        user = __salt__['config.option']('keystone.user')
        password = __salt__['config.option']('keystone.password')
        tenant = __salt__['config.option']('keystone.tenant')
        auth_url = __salt__['config.option']('keystone.auth_url')
        region_name = __salt__['config.option']('keystone.region_name')
        api_key = __salt__['config.option']('keystone.api_key')
        os_auth_system = __salt__['config.option']('keystone.os_auth_system')
    kwargs = {
        'username': user,
        'password': password,
        'api_key': api_key,
        'project_id': tenant,
        'auth_url': auth_url,
        'region_name': region_name,
        'os_auth_plugin': os_auth_system
    }
    return suon.SaltNova(**kwargs)


def _get_novaclient(profile=None, tenant_name=None):
    if HAS_SALTNOVA:
        conn = _auth(profile=None, tenant_name=None)
        return conn.compute_conn
    elif HAS_NOVA and HAS_KEYSTONE:
        conn_args = get_connection_args()
        auth = keystoneauth1.identity.v2.Password(auth_url=conn_args.get('auth_url', None),
                                                  username=conn_args.get('username', None),
                                                  password=conn_args.get('password', None),
                                                  tenant_name=conn_args.get('tenant_name', None))
        sess = keystoneauth1.session.Session(auth=auth)
        nova = novaclient.client.Client("2.1", session=sess)
        try:
            nova.flavors.list()
        except:
            raise Exception('novaclient: Could not authenticate with given credentials.')
        return nova
    else:
        raise Exception('novaclient: could not instantiate.')


@depends(HAS_SALTNOVA)
def server_list(profile=None, tenant_name=None):
    '''
    Return list of active servers
    CLI Example:
    .. code-block:: bash
        salt '*' nova.server_list
    '''
    conn = _auth(profile, tenant_name)
    return conn.server_list()


@depends(HAS_SALTNOVA)
def server_get(name, tenant_name=None, profile=None):
    '''
    Return information about a server
    '''
    items = server_list(profile, tenant_name)
    instance_id = None
    for key, value in items.iteritems():
        if key == name:
            instance_id = value['id']
    return instance_id


def get_connection_args(profile=None):
    '''
    Set up profile credentials
    '''
    if profile:
        credentials = __salt__['config.option'](profile)
        user = credentials['keystone.user']
        password = credentials['keystone.password']
        tenant = credentials['keystone.tenant']
        auth_url = credentials['keystone.auth_url']
    else:
        user = __salt__['config.option']('keystone.user')
        password = __salt__['config.option']('keystone.password')
        tenant = __salt__['config.option']('keystone.tenant')
        auth_url = __salt__['config.option']('keystone.auth_url')

    kwargs = {
        'username': user,
        'password': password,
        'tenant': tenant,
        'auth_url': auth_url
    }
    return kwargs


def quota_list(tenant_name, profile=None):
    '''
    list quotas of a tenant
    '''
    connection_args = get_connection_args(profile)
    tenant = __salt__['keystone.tenant_get'](name=tenant_name, profile=profile, **connection_args)
    tenant_id = tenant[tenant_name]['id']
    nt_ks = _get_novaclient(profile)
    item = nt_ks.quotas.get(tenant_id).__dict__
    return item


def quota_get(name, tenant_name, profile=None, quota_value=None):
    '''
    get specific quota value of a tenant
    '''
    item = quota_list(tenant_name, profile)
    quota_value = item[name]
    return quota_value


def quota_update(tenant_name, profile=None, **quota_argument):
    '''
    update quota of specified tenant
    '''
    connection_args = get_connection_args(profile)
    tenant = __salt__['keystone.tenant_get'](name=tenant_name, profile=profile, **connection_args)
    tenant_id = tenant[tenant_name]['id']
    nt_ks = _get_novaclient(profile)
    item = nt_ks.quotas.update(tenant_id, **quota_argument)
    return item


@depends(HAS_SALTNOVA)
def server_list(profile=None, tenant_name=None):
    '''
    Return list of active servers
    CLI Example:
    .. code-block:: bash
        salt '*' nova.server_list
    '''
    conn = _auth(profile, tenant_name)
    return conn.server_list()


@depends(HAS_SALTNOVA)
def secgroup_list(profile=None, tenant_name=None):
    '''
    Return a list of available security groups (nova items-list)
    CLI Example:
    .. code-block:: bash
        salt '*' nova.secgroup_list
    '''
    conn = _auth(profile, tenant_name)
    return conn.secgroup_list()


@depends(HAS_SALTNOVA)
def boot(name, flavor_id=0, image_id=0, profile=None, tenant_name=None, timeout=300, **kwargs):
    '''
    Boot (create) a new instance
    name
        Name of the new instance (must be first)
    flavor_id
        Unique integer ID for the flavor
    image_id
        Unique integer ID for the image
    timeout
        How long to wait, after creating the instance, for the provider to
        return information about it (default 300 seconds).
        .. versionadded:: 2014.1.0
    CLI Example:
    .. code-block:: bash
        salt '*' nova.boot myinstance flavor_id=4596 image_id=2
    The flavor_id and image_id are obtained from nova.flavor_list and
    nova.image_list
    .. code-block:: bash
        salt '*' nova.flavor_list
        salt '*' nova.image_list
    '''
    #kwargs = {'nics': nics}
    conn = _auth(profile, tenant_name)
    return conn.boot(name, flavor_id, image_id, timeout, **kwargs)


@depends(HAS_SALTNOVA)
def network_show(name, profile=None):
    conn = _auth(profile)
    return conn.network_show(name)


def availability_zone_list(profile=None):
    '''
    list existing availability zones
    '''
    connection_args = get_connection_args(profile)
    nt_ks = _get_novaclient(profile)
    ret = nt_ks.aggregates.list()
    return ret


def availability_zone_get(name, profile=None):
    '''
    list existing availability zones
    '''
    connection_args = get_connection_args(profile)
    nt_ks = _get_novaclient(profile)
    zone_exists=False
    items = availability_zone_list(profile)
    for p in items:
        item = nt_ks.aggregates.get(p).__getattr__('name')
        if item == name:
            zone_exists = True
    return zone_exists


def availability_zone_create(name, availability_zone, profile=None):
    '''
    create availability zone
    '''
    connection_args = get_connection_args(profile)
    nt_ks = _get_novaclient(profile)
    item = nt_ks.aggregates.create(name, availability_zone)
    ret = {
        'Id': item.__getattr__('id'),
        'Aggregate Name': item.__getattr__('name'),
        'Availability Zone': item.__getattr__('availability_zone'),
    }
    return ret

def aggregate_list(profile=None):
    '''
    list existing aggregates
    '''
    connection_args = get_connection_args(profile)
    nt_ks = _get_novaclient(profile)
    ret = nt_ks.aggregates.list()
    return ret


def aggregate_get(name, profile=None):
    '''
    list existing aggregates
    '''
    connection_args = get_connection_args(profile)
    nt_ks = _get_novaclient(profile)
    aggregate_exists=False
    items = aggregate_list(profile)
    for p in items:
        item = nt_ks.aggregates.get(p).__getattr__('name')
        if item == name:
            aggregate_exists = True
    return aggregate_exists


def aggregate_create(name, aggregate, profile=None):
    '''
    create aggregate
    '''
    connection_args = get_connection_args(profile)
    nt_ks = _get_novaclient(profile)
    item = nt_ks.aggregates.create(name, aggregate)
    ret = {
        'Id': item.__getattr__('id'),
        'Aggregate Name': item.__getattr__('name'),
    }
    return ret

def flavor_list(profile=None):
    '''
    Return a list of available flavors (nova flavor-list)
    '''
    nt_ks = _get_novaclient(profile)
    ret = {}
    for flavor in nt_ks.flavors.list():
        links = {}
        for link in flavor.links:
            links[link['rel']] = link['href']
        ret[flavor.name] = {
            'disk': flavor.disk,
            'id': flavor.id,
            'name': flavor.name,
            'ram': flavor.ram,
            'swap': flavor.swap,
            'vcpus': flavor.vcpus,
            'links': links,
        }
        if hasattr(flavor, 'rxtx_factor'):
            ret[flavor.name]['rxtx_factor'] = flavor.rxtx_factor
    return ret


def flavor_create(name,             # pylint: disable=C0103
                  flavor_id=0,      # pylint: disable=C0103
                  ram=0,
                  disk=0,
                  vcpus=1,
                  profile=None):
    '''
    Create a flavor
    '''
    nt_ks = _get_novaclient(profile)
    nt_ks.flavors.create(
        name=name, flavorid=flavor_id, ram=ram, disk=disk, vcpus=vcpus
    )
    return {'name': name,
            'id': flavor_id,
            'ram': ram,
            'disk': disk,
            'vcpus': vcpus}


def flavor_delete(flavor_id, profile=None):  # pylint: disable=C0103
    '''
    Delete a flavor
    '''
    nt_ks = _get_novaclient(profile)
    nt_ks.flavors.delete(flavor_id)
    return 'Flavor deleted: {0}'.format(flavor_id)

