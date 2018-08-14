{%- from "nova/map.jinja" import controller, compute, compute_driver_mapping with context %}

nova_upgrade_pre:
  test.show_notification:
    - name: "dump_message_upgrade_nova_pre"
    - text: "Running nova.upgrade.upgrade.pre"

