{%- from "keystone/map.jinja" import client as kclient with context %}

nova_upgrade_verify_api:
  test.show_notification:
    - name: "dump_message_verify_api_nova"
    - text: "Running nova.upgrade.verify.api"

{%- if kclient.enabled and kclient.get('os_client_config', {}).get('enabled', False)  %}
  {%- set Nova_Test_Flavor_ID = 'random' | uuid %}

novav21_flavor_create:
  module.run:
    - name: novav21.flavor_create
    - kwargs:
        cloud_name: admin_identity
        id: {{ Nova_Test_Flavor_ID }}
        name: {{ Nova_Test_Flavor_ID }}
        vcpus: 2
        ram: 1
        disk: 2

novav21_flavor_list:
  module.run:
    - name: novav21.flavor_list
    - kwargs:
        cloud_name: admin_identity

novav21_quota_list:
  module.run:
    - name: novav21.quota_list
    - kwargs:
        cloud_name: admin_identity
        project_id: default

novav21_flavor_absent:
  novav21.flavor_absent:
  - cloud_name: admin_identity
  - name: {{ Nova_Test_Flavor_ID }}
  - require:
    - novav21_flavor_create

novav21_server_list:
  module.run:
    - name: novav21.server_list
    - kwargs:
        cloud_name: admin_identity

{%- endif %}
