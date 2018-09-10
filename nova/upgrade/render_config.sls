{%- from "nova/map.jinja" import controller, compute, client, upgrade with context %}

nova_render_config:
  test.show_notification:
    - name: "dump_message_render_config_nova"
    - text: "Running nova.upgrade.render_config"

{%- if controller.get('enabled', false) %}
  {%- set _data = controller %}
  {%- set type = 'controller' %}
{%- elif compute.get('enabled', false) %}
  {%- set _data = compute %}
  {%- set type = 'compute' %}
{%- endif %}

/etc/nova/nova.conf:
  file.managed:
  - source: salt://nova/files/{{ _data.version }}/nova-{{ type }}.conf.{{ grains.os_family }}
  - template: jinja

/etc/nova/api-paste.ini:
  file.managed:
  - source: salt://nova/files/{{ _data.version }}/api-paste.ini.{{ grains.os_family }}
  - template: jinja

{%- if controller.get('enabled', False) %}

  {% for service_name in controller.services %}
{{ service_name }}_default:
  file.managed:
    - name: /etc/default/{{ service_name }}
    - source: salt://nova/files/default
    - template: jinja
    - defaults:
        service_name: {{ service_name }}
        values: {{ controller }}
  {% endfor %}

  {% if controller.get('policy', {}) and controller.version not in ['liberty', 'mitaka', 'newton'] %}
{# nova no longer ships with a default policy.json #}

/etc/nova/policy.json:
  file.managed:
    - contents: '{}'
    - replace: False
    - user: nova
    - group: nova

  {% endif %}

{%- endif %}
