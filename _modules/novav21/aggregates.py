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


@common.function_descriptor('find', 'Host aggregate', 'aggregates')
@common.send('get')
def list_(**kwargs):
    """List host aggregates"""
    url = '/os-aggregates'
    return url, {}


@common.function_descriptor('update', 'Host aggregate', 'aggregate')
@common.get_by_name_or_uuid(list_, 'aggregates')
@common.send('post')
def add_host(aggregate_id, host, **kwargs):
    """Add host to a host aggregate"""
    url = '/os-aggregates/%s/action' % aggregate_id
    return url, {'json': {'add_host': {'host': host}}}


@common.function_descriptor('create', 'Host aggregate', 'aggregate')
@common.send('post')
def create(name, availability_zone, **kwargs):
    """Create a host aggregate"""
    url = '/os-aggregates'
    req = {'name': name, 'availability_zone': availability_zone}
    return url, {'json': {'aggregate': req}}


@common.function_descriptor('delete', 'Host aggregate')
@common.get_by_name_or_uuid(list_, 'aggregates')
@common.send('delete')
def delete(aggregate_id, **kwargs):
    """Delete a host aggregate"""
    url = '/os-aggregates/%s' % aggregate_id
    return url, {}


@common.function_descriptor('find', 'Host aggregate', 'aggregate')
@common.get_by_name_or_uuid(list_, 'aggregates')
@common.send('get')
def get(aggregate_id, **kwargs):
    """Get a host aggregate"""
    url = '/os-aggregates/%s' % aggregate_id
    return url, {}


@common.function_descriptor('update', 'Host aggregate', 'aggregate')
@common.get_by_name_or_uuid(list_, 'aggregates')
@common.send('post')
def remove_host(aggregate_id, host, **kwargs):
    """Remove host from a host aggregate"""
    url = '/os-aggregates/%s/action' % aggregate_id
    return url, {'json': {'remove_host': {'host': host}}}


@common.function_descriptor('update', 'Host aggregate', 'aggregate')
@common.get_by_name_or_uuid(list_, 'aggregates')
@common.send('post')
def set_metadata(aggregate_id, **kwargs):
    """Set host aggregate metadata"""
    url = '/os-aggregates/%s/action' % aggregate_id
    return url, {'json': {'set_metadata': {'metadata': kwargs}}}
