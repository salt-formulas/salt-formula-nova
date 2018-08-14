{%- from "nova/map.jinja" import controller, compute, compute_driver_mapping with context %}

nova_upgrade_post:
  test.show_notification:
    - name: "dump_message_upgrade_nova_post"
    - text: "Running nova.upgrade.upgrade.post"

