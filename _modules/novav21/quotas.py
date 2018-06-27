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


@common.function_descriptor('delete', 'Project quota')
@common.send('get')
def delete(project_id, user_id=None, **kwargs):
    """List quotas of a project (and user)"""
    url = '/os-quota-sets/%s' % project_id
    if user_id:
        url = '%s?user_id=%s' % (url, user_id)
    return url, {}


@common.function_descriptor('find', 'Project quota', 'quota_set')
@common.send('get')
def list_(project_id, user_id=None, **kwargs):
    """List quotas of a project (and user)"""
    url = '/os-quota-sets/%s' % project_id
    if user_id:
        url = '%s?user_id=%s' % (url, user_id)
    return url, {}


@common.function_descriptor('update', 'Project quota', 'quota_set')
@common.send('put')
def update(project_id, user_id=None, **kwargs):
    """Update quota of the specified project (and user)"""
    url = '/os-quota-sets/%s' % project_id
    if user_id:
        url = '%s?user_id=%s' % (url, user_id)
    return url, {'json': {'quota_set': kwargs}}
