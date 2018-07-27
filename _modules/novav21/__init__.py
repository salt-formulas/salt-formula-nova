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

try:
    import os_client_config
    REQUIREMENTS_MET = True
except ImportError:
    REQUIREMENTS_MET = False

__virtualname__ = 'novav21'

import aggregates
import flavors
import keypairs
import quotas
import servers

aggregate_add_host = aggregates.add_host
aggregate_create = aggregates.create
aggregate_delete = aggregates.delete
aggregate_get = aggregates.get
aggregate_list = aggregates.list_
aggregate_remove_host = aggregates.remove_host
aggregate_set_metadata = aggregates.set_metadata
flavor_add_extra_specs = flavors.add_extra_specs
flavor_create = flavors.create
flavor_delete = flavors.delete
flavor_delete_extra_spec = flavors.delete_extra_spec
flavor_get = flavors.get
flavor_get_extra_specs = flavors.get_extra_specs
flavor_list = flavors.list_
keypair_create = keypairs.create
keypair_delete = keypairs.delete
keypair_get = keypairs.get
keypair_list = keypairs.list_
quota_delete = quotas.delete
quota_list = quotas.list_
quota_update = quotas.update
server_create = servers.create
server_delete = servers.delete
server_get = servers.get
server_list = servers.list_
server_lock = servers.lock
server_resume = servers.resume
server_suspend = servers.suspend
server_unlock = servers.unlock


__all__ = (
    'aggregate_add_host', 'aggregate_create', 'aggregate_delete',
    'aggregate_get', 'aggregate_list', 'aggregate_remove_host',
    'aggregate_set_metadata', 'flavor_add_extra_specs', 'flavor_create',
    'flavor_delete', 'flavor_delete_extra_spec', 'flavor_get',
    'flavor_get_extra_specs', 'flavor_list', 'keypair_create',
    'keypair_delete', 'keypair_get', 'keypair_list', 'quota_delete',
    'quota_list', 'quota_update', 'server_create', 'server_delete',
    'server_get', 'server_list', 'server_lock', 'server_resume',
    'server_suspend', 'server_unlock')


def __virtual__():
    if REQUIREMENTS_MET:
        return __virtualname__
    else:
        return False, ("The novav21 execution module cannot be loaded: "
                       "os_client_config package not found.")
