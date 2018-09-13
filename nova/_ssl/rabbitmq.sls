{% from "nova/map.jinja" import controller, compute with context %}

nova_ssl_rabbitmq:
  test.show_notification:
    - text: "Running nova._ssl.rabbitmq"

{%- if controller.message_queue.get('x509',{}).get('enabled',False) %}

  {%- set ca_file=controller.message_queue.x509.ca_file %}
  {%- set key_file=controller.message_queue.x509.key_file %}
  {%- set cert_file=controller.message_queue.x509.cert_file %}

rabbitmq_nova_ssl_x509_ca:
  {%- if controller.message_queue.x509.cacert is defined %}
  file.managed:
    - name: {{ ca_file }}
    - contents_pillar: nova:controller:message_queue:x509:cacert
    - mode: 444
    - user: nova
    - group: nova
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ ca_file }}
  {%- endif %}

rabbitmq_nova_client_ssl_cert:
  {%- if controller.message_queue.x509.cert is defined %}
  file.managed:
    - name: {{ cert_file }}
    - contents_pillar: nova:controller:message_queue:x509:cert
    - mode: 440
    - user: nova
    - group: nova
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ cert_file }}
  {%- endif %}

rabbitmq_nova_client_ssl_private_key:
  {%- if controller.message_queue.x509.key is defined %}
  file.managed:
    - name: {{ key_file }}
    - contents_pillar: nova:controller:message_queue:x509:key
    - mode: 400
    - user: nova
    - group: nova
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ key_file }}
  {%- endif %}

rabbitmq_nova_ssl_x509_set_user_and_group:
  file.managed:
    - names:
      - {{ ca_file }}
      - {{ cert_file }}
      - {{ key_file }}
    - user: nova
    - group: nova

  {% elif controller.message_queue.get('ssl',{}).get('enabled',False) %}
rabbitmq_ca_nova_client_controller:
  {%- if controller.message_queue.ssl.cacert is defined %}
  file.managed:
    - name: {{ controller.message_queue.ssl.cacert_file }}
    - contents_pillar: nova:controller:message_queue:ssl:cacert
    - mode: 0444
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ controller.message_queue.ssl.get('cacert_file', controller.cacert_file) }}
  {%- endif %}

{%- endif %}
