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

import six.moves.urllib.parse as urllib_parse

import common

# Function alias to not shadow built-ins
__func_alias__ = {
    'list_': 'list'
}


@common.send('get')
def list_(**kwargs):
    """Return list of servers."""
    url = '/servers?{}'.format(urllib_parse.urlencode(kwargs))
    return url, {}


@common.send('post')
def create(name, flavor, **kwargs):
    """Create server(s)."""
    # TODO: add something useful :)
    url = '/servers'
    req = {'server': {'name': name, 'flavor': flavor}}
    req['server'].update(kwargs)
    return url, {'json': req}


@common.get_by_name_or_uuid(list_, 'servers')
@common.send('delete')
def delete(server_id, **kwargs):
    """Delete server."""
    url = '/servers/{server_id}'.format(server_id=server_id)
    return url, {}


@common.get_by_name_or_uuid(list_, 'servers')
@common.send('get')
def get(server_id, **kwargs):
    """Return one server."""
    url = '/servers/{server_id}'.format(server_id=server_id)
    return url, {}


@common.get_by_name_or_uuid(list_, 'servers')
@common.send('post')
def lock(server_id, **kwargs):
    """Lock server."""
    url = '/servers/{server_id}/action'.format(server_id=server_id)
    req = {"lock": None}
    return url, {"json": req}


@common.get_by_name_or_uuid(list_, 'servers')
@common.send('post')
def resume(server_id, **kwargs):
    """Resume server after suspend."""
    url = '/servers/{server_id}/action'.format(server_id=server_id)
    req = {"resume": None}
    return url, {"json": req}


@common.get_by_name_or_uuid(list_, 'servers')
@common.send('post')
def suspend(server_id, **kwargs):
    """Suspend server."""
    url = '/servers/{server_id}/action'.format(server_id=server_id)
    req = {"suspend": None}
    return url, {"json": req}


@common.get_by_name_or_uuid(list_, 'servers')
@common.send('post')
def unlock(server_id, **kwargs):
    """Unlock server."""
    url = '/servers/{server_id}/action'.format(server_id=server_id)
    req = {"unlock": None}
    return url, {"json": req}
