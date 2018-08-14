{%- from "nova/map.jinja" import controller, compute, client, upgrade with context %}

nova_post:
  test.show_notification:
    - name: "dump_message_post-upgrade"
    - text: "Running nova.upgrade.post"

{%- if controller.get('enabled') %}

nova_status:
  cmd.run:
    - name: nova-status upgrade check
  {%- if grains.get('noservices') or controller.get('role', 'primary') == 'secondary' %}
    - onlyif: /bin/false
  {%- endif %}

{%- endif %}

keystone_os_client_config_absent:
  file.absent:
    - name: /etc/openstack/clouds.yml
