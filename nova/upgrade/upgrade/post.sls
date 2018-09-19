{%- from "nova/map.jinja" import controller, compute, compute_driver_mapping with context %}

nova_upgrade_post:
  test.show_notification:
    - name: "dump_message_upgrade_nova_post"
    - text: "Running nova.upgrade.upgrade.post"

{%- if compute.get('enabled') %}
{% set host_id = salt['network.get_hostname']() %}

novav21_service_enabled:
  novav21.service_enabled:
  - binary: nova-compute
  - cloud_name: admin_identity
  - name: {{ host_id }}

{% endif %}
