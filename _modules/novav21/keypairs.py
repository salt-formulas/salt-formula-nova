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


@common.function_descriptor('create', 'Keypair', 'keypair')
@common.send('post')
def create(name, public_key, **kwargs):
    """Create a keypair"""
    url = '/os-keypairs'
    body = {'name': name, 'public_key': public_key}
    body.update(kwargs)
    return url, {'json': {'keypair': body}}


@common.function_descriptor('delete', 'Keypair')
@common.send('delete')
def delete(name, **kwargs):
    """Delete keypair"""
    url = '/os-keypairs/{}?{}'.format(name, urllib_parse.urlencode(kwargs))
    return url, {}


@common.function_descriptor('find', 'Keypair', 'keypair')
@common.send('get')
def get(name, **kwargs):
    """Get a keypair of a project (and user)"""
    url = '/os-keypairs/{}?{}'.format(name, urllib_parse.urlencode(kwargs))
    return url, {}


@common.function_descriptor('find', 'Keypair', 'keypairs')
@common.send('get')
def list_(**kwargs):
    """List keypairs of a project (and user)"""
    url = '/os-keypairs?{}'.format(urllib_parse.urlencode(kwargs))
    return url, {}
