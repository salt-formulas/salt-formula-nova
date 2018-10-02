{%- from "nova/map.jinja" import client with context %}
{%- if client.enabled %}

{%- for identity_name, identity in client.get('resources', {}).get('v21', {}).iteritems() %}

  {%- if identity.flavor is defined %}
  {%- for flavor_name, flavor in identity.flavor.iteritems() %}

novav21_openstack_flavor_{{ flavor_name }}:
  novav21.flavor_present:
    - name: {{ flavor_name }}
    - cloud_name: {{ identity_name }}
    {%- if flavor.flavor_id is defined %}
    - flavor_id: {{ flavor.flavor_id }}
    {%- endif %}
    {%- if flavor.ram is defined %}
    - ram: {{ flavor.ram }}
    {%- endif %}
    {%- if flavor.disk is defined %}
    - disk: {{ flavor.disk }}
    {%- endif %}
    {%- if flavor.vcpus is defined %}
    - vcpus: {{ flavor.vcpus }}
    {%- endif %}
    {%- if flavor.extra_specs is defined %}
    - extra_specs: {{ flavor.extra_specs }}
    {%- endif %}

  {%- endfor %}
  {%- endif %}

{%- endfor %}
{%- endif %}
