{%- from "nova/map.jinja" import controller, compute, upgrade with context %}

nova_pre:
  test.show_notification:
    - name: "dump_message_pre-upgrade_nova"
    - text: "Running nova.upgrade.pre"

{%- if controller.get('enabled', false) %}
  {%- set _data = controller %}
  {%- set type = 'controller' %}
{%- elif compute.get('enabled', false) %}
  {%- set _data = compute %}
  {%- set type = 'compute' %}
{%- endif %}

/etc/nova/nova.conf:
  file.managed:
  - name: /etc/nova/nova.conf
  - source: salt://nova/files/{{ _data.version }}/nova-{{ type }}.conf.{{ grains.os_family }}
  - template: jinja

{%- if controller.get('enabled') %}

include:
 - nova.db.online_sync

nova_status:
  cmd.run:
    - name: nova-status upgrade check
  {%- if grains.get('noservices') or controller.get('role', 'primary') == 'secondary' %}
    - onlyif: /bin/false
  {%- endif %}
{%- endif %}

{%- set os_content = salt['mine.get']('I@keystone:client:os_client_config:enabled:true', 'keystone_os_client_config', 'compound').values()[0] %}
keystone_os_client_config:
  file.managed:
    - name: /etc/openstack/clouds.yml
    - contents: |
        {{ os_content |yaml(False)|indent(8) }}
    - user: 'root'
    - group: 'root'
    - makedirs: True
    - unless: test -f /etc/openstack/clouds.yml
