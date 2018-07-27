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

import common

# Function alias to not shadow built-ins
__func_alias__ = {
    'list_': 'list'
}


@common.function_descriptor('update', 'Flavor extra specs', 'extra_specs')
@common.send('post')
def add_extra_specs(flavor_id, **kwargs):
    # NOTE: flavor_id can be any string, don't convert flavor name to uuid
    url = '/flavors/{flavor_id}/os-extra_specs'.format(flavor_id=flavor_id)
    return url, {'json': {"extra_specs": kwargs}}


@common.function_descriptor('create', 'Flavor', 'flavor')
@common.send('post')
def create(name, vcpus, ram, disk, **kwargs):
    """Create flavor(s)."""
    url = '/flavors'
    req = {'flavor': {'name': name, 'vcpus': vcpus, 'ram': ram, 'disk': disk}}
    req['flavor'].update(kwargs)
    return url, {'json': req}


@common.function_descriptor('delete', 'Flavor')
@common.send('delete')
def delete(flavor_id, **kwargs):
    """Delete flavor."""
    # NOTE: flavor_id can be any string, don't convert flavor name to uuid
    url = '/flavors/{flavor_id}'.format(flavor_id=flavor_id)
    return url, {}


@common.function_descriptor('update', 'Flavor extra specs')
@common.send('delete')
def delete_extra_spec(flavor_id, key_name, **kwargs):
    # NOTE: flavor_id can be any string, don't convert flavor name to uuid
    url = '/flavors/{flavor_id}/os-extra_specs/{key_name}'.format(
        flavor_id=flavor_id, key_name=key_name)
    return url, {}


@common.function_descriptor('find', 'Flavor', 'flavor')
@common.send('get')
def get(flavor_id, **kwargs):
    """Return one flavor."""
    # NOTE: flavor_id can be any string, don't convert flavor name to uuid
    url = '/flavors/{flavor_id}'.format(flavor_id=flavor_id)
    return url, {}


@common.function_descriptor('find', 'Flavor extra specs', 'extra_specs')
@common.send('get')
def get_extra_specs(flavor_id, **kwargs):
    # NOTE: flavor_id can be any string, don't convert flavor name to uuid
    url = '/flavors/{flavor_id}/os-extra_specs'.format(flavor_id=flavor_id)
    return url, {}


@common.function_descriptor('find', 'Flavor', 'flavors')
@common.send('get')
def list_(detail=False, **kwargs):
    """Return list of flavors."""
    url = '/flavors'
    if detail:
        url = '%s/detail' % url
    return url, {}
