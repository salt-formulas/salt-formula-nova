{%- from "nova/map.jinja" import controller, compute, client, upgrade with context %}

nova_task_pkgs_latest:
  test.show_notification:
    - name: "dump_message_pkgs_latest"
    - text: "Running nova.upgrade.pkg_latest"

policy-rc.d_present:
  file.managed:
    - name: /usr/sbin/policy-rc.d
    - mode: 755
    - contents: |
        #!/bin/sh
        exit 101

{%- set pkgs = [] %}
{%- if compute.get('enabled', false) %}
  {%- do pkgs.extend(compute.pkgs) %}
{%- endif %}

{%- if client.get('enabled', false) %}
  {%- do pkgs.extend(client.pkgs) %}
{%- endif %}

{%- if controller.get('enabled', false) %}
  {%- do pkgs.extend(controller.pkgs) %}

{%- if controller.get('version',{}) not in ["juno", "kilo", "liberty", "mitaka", "newton"] %}
  {%- do pkgs.append('nova-placement-api') %}
{%- endif %}

{%- endif %}

nova_packages:
  pkg.latest:
  - names: {{ pkgs|unique }}
  - require:
    - file: policy-rc.d_present
  - require_in:
    - file: policy-rc.d_absent

policy-rc.d_absent:
  file.absent:
    - name: /usr/sbin/policy-rc.d
