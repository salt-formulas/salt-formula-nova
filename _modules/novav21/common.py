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

import six
import logging
import uuid

import os_client_config
from salt import exceptions


log = logging.getLogger(__name__)

SERVICE_KEY = 'compute'


def get_raw_client(cloud_name):
    config = os_client_config.OpenStackConfig()
    cloud = config.get_one_cloud(cloud_name)
    adapter = cloud.get_session_client(SERVICE_KEY)
    adapter.version = '2.1'
    endpoints = []
    try:
        access_info = adapter.session.auth.get_access(adapter.session)
        endpoints = access_info.service_catalog.get_endpoints()
    except (AttributeError, ValueError) as exc:
        six.raise_from(exc, exceptions.SaltInvocationError(
            "Cannot load keystoneauth plugin. Please check your environment "
            "configuration."))
    if SERVICE_KEY not in endpoints:
        raise exceptions.SaltInvocationError("Cannot find compute endpoint in "
                                             "environment endpoint list.")
    return adapter


def send(method):
    def wrap(func):
        @six.wraps(func)
        def wrapped_f(*args, **kwargs):
            cloud_name = kwargs.pop('cloud_name', None)
            if not cloud_name:
                raise exceptions.SaltInvocationError(
                    "No cloud_name specified. Please provide cloud_name "
                    "parameter")
            adapter = get_raw_client(cloud_name)
            kwarg_keys = list(kwargs.keys())
            for k in kwarg_keys:
                if k.startswith('__'):
                    kwargs.pop(k)
            url, request_kwargs = func(*args, **kwargs)
            try:
                response = getattr(adapter, method.lower())(url,
                                                            **request_kwargs)
            except Exception as e:
                log.exception("Error occurred when executing request")
                return {"result": False,
                        "comment": six.text_type(e),
                        "status_code": getattr(e, "http_status", 500)}
            return {"result": True,
                    "body": response.json() if response.content else {},
                    "status_code": response.status_code}
        return wrapped_f
    return wrap


def _check_uuid(val):
    try:
        return str(uuid.UUID(val)) == val
    except (TypeError, ValueError, AttributeError):
        return False


def get_by_name_or_uuid(resource_list, resp_key):
    def wrap(func):
        @six.wraps(func)
        def wrapped_f(*args, **kwargs):
            if 'name' in kwargs:
                ref = kwargs.pop('name', None)
                start_arg = 0
            else:
                start_arg = 1
                ref = args[0]
            item_id = None
            if _check_uuid(ref):
                item_id = ref
            else:
                cloud_name = kwargs['cloud_name']
                resp = resource_list(cloud_name=cloud_name)["body"][resp_key]
                for item in resp:
                    if item["name"] == ref:
                        if item_id is not None:
                            return {
                                "name": ref,
                                "changes": {},
                                "result": False,
                                "comment": "Multiple resources ({resource}) "
                                           "with requested name found ".format(
                                               resource=resp_key)}
                        item_id = item["id"]
                if not item_id:
                    return {
                        "name": ref,
                        "changes": {},
                        "result": False,
                        "comment": "Resource ({resource}) "
                                   "with requested name not found ".format(
                            resource=resp_key)}
            return func(item_id, *args[start_arg:], **kwargs)
        return wrapped_f
    return wrap


def function_descriptor(action_type, resource_human_readable_name,
                        body_response_key=None):
    def decorator(fun):
        fun._action_type = action_type
        fun._body_response_key = body_response_key or ''
        fun._resource_human_readable_name = resource_human_readable_name
        return fun
    return decorator
