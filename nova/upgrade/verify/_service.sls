{%- from "nova/map.jinja" import controller, compute, compute_driver_mapping with context %}

nova_task_uprade_verify_service:
  test.show_notification:
    - text: "Running nova.upgrade.verify.service"

{%- if compute.get('enabled') or controller.get('enabled') %}
{% set host_id = salt['network.get_hostname']() %}

wait_for_service:
  module.run:
    - name: novav21.services_wait
    - cloud_name: admin_identity
    - admin_up_only: False
    - host: {{ host_id }}
    - retries: 30
    - timeout: 10

{% endif %}
