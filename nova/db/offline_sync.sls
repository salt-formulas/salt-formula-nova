{% from "nova/map.jinja" import controller with context %}

nova_controller_syncdb:
  cmd.run:
  - name: nova-manage db sync
  {%- if grains.get('noservices') or controller.get('role', 'primary') == 'secondary' %}
  - onlyif: /bin/false
  {%- endif %}

{%- if controller.version not in ["juno", "kilo", "liberty"] %}
nova_controller_sync_apidb:
  cmd.run:
  - name: nova-manage api_db sync
  {%- if grains.get('noservices') or controller.get('role', 'primary') == 'secondary' %}
  - onlyif: /bin/false
  {%- endif %}

{%- endif %}
