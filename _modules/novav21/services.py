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
import six.moves.urllib.parse as urllib_parse
import time
from salt.exceptions import CommandExecutionError

# Function alias to not shadow built-ins
__func_alias__ = {
    'list_': 'list'
}


@common.function_descriptor('find', 'Compute services', 'services')
@common.send('get')
def list_(*args, **kwargs):
    """Return list of nova services."""
    url = '/os-services?{}'.format(urllib_parse.urlencode(kwargs))
    return url, {}


@common.function_descriptor('update', 'Compute service', 'service')
@common.send('put')
def update(host, service, action, **kwargs):
    """Enable/Disable nova service"""
    if kwargs.get('disabled_reason') and action == 'disable':
      url = '/os-services/disable-log-reason'
      req = {"host": host, "binary": service, "disabled_reason": kwargs['disabled_reason']}
    else:
      url = '/os-services/%s' % action
      req = {"host": host, "binary": service}
    return url, {"json": req}


def wait_for_services(cloud_name, host=None, service=None, admin_up_only=True, retries=18, timeout=10, **kwargs):
    """Ensure the service is up and running on specified host.

    :param host:           name of a host where service is running
    :param admin_up_only:  do not check status for admin disabled service
    :param service:        name of the service (by default nova-compute)
    :param timeout:        number of seconds to wait before retries
    :param retries:        number of retries
    """
    kwargs = {}
    if host is not None:
        kwargs['host'] = host
    if service is not None:
        kwargs['service'] = service

    for i in range(retries):
        services = list_(cloud_name=cloud_name, **kwargs)['body'].get('services')

        if admin_up_only:
            down_services = [s for s in services if (not service or s['binary'] == service) and s['status'] == 'enabled' and s['state'] == 'down']
        else:
            down_services = [s for s in services if (not service or s['binary'] == service) and s['state'] == 'down']

        if len(down_services) == 0:
            return 'Compute services with admin_up_only=%s are up or disabled administratively' % (admin_up_only)
        time.sleep(timeout)

    raise CommandExecutionError("Compute services {} are still down or disabled".format(down_services))
