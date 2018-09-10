{%- from "nova/map.jinja" import controller, compute, upgrade with context %}

nova_task_service_running:
  test.show_notification:
    - name: "dump_message_service_running_nova"
    - text: "Running nova.upgrade.service_running"

{%- if controller.get('enabled', false) %}
  {%- set _data = controller %}
{%- elif compute.get('enabled', false) %}
  {%- set _data = compute %}
{%- endif %}

{%- set nservices = [] %}
{%- do nservices.extend(_data.services) %}

{%- if controller.get('enabled') %}
  {%- if controller.version not in ["juno", "kilo", "liberty", "mitaka", "newton"] %}
    {%- do nservices.append('apache2') %}
  {%- endif %}
{%- endif %}

{%- if nservices|unique|length > 0 %}
  {%- for service in nservices|unique %}
nova_service_running_{{ service }}:
  service.running:
  - enable: true
  - name: {{ service }}
  {%- if grains.get('noservices') %}
  - onlyif: /bin/false
  {%- endif %}
  {%- endfor %}
{%- endif %}
