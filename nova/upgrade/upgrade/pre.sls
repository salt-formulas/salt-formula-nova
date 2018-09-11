{%- from "nova/map.jinja" import controller, compute, compute_driver_mapping with context %}

nova_upgrade_pre:
  test.show_notification:
    - name: "dump_message_upgrade_nova_pre"
    - text: "Running nova.upgrade.upgrade.pre"

{%- if compute.get('enabled') %}
{% set host_id = salt['network.get_hostname']() %}

novav21_service_disabled:
  novav21.service_disabled:
  - binary: nova-compute
  - disabled_reason: Disabled for upgrade
  - cloud_name: admin_identity
  - name: {{ host_id }}

{% endif %}
