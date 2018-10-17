nova:
  compute:
    version: pike
    enabled: true
    bind:
      vnc_address: 127.0.0.1
      vnc_port: 6080
      vnc_name: 0.0.0.0
    database:
      engine: mysql
      host: 127.0.0.1
      port: 3306
      name: nova
      user: nova
      password: password
    identity:
      engine: keystone
      region: RegionOne
      host: 127.0.0.1
      port: 35357
      user: nova
      password: password
      tenant: service
    logging:
      log_appender: false
      log_handlers:
        watchedfile:
          enabled: true
        fluentd:
          enabled: false
        ossyslog:
          enabled: false
    message_queue:
      engine: rabbitmq
      members:
      - host: 127.0.0.1
      - host: 127.0.1.1
      - host: 127.0.2.1
      user: openstack
      password: password
      virtual_host: '/openstack'
    image:
      engine: glance
      host: 127.0.0.1
      port: 9292
    network:
      engine: neutron
      region: RegionOne
      host: 127.0.0.1
      port: 9696
      extension_sync_interval: 600
      user: nova
      password: password
      tenant: service
    metadata:
      password: metadata
    cache:
      engine: memcached
      members:
      - host: 127.0.0.1
        port: 11211
      - host: 127.0.1.1
        port: 11211
      - host: 127.0.2.1
        port: 11211
      security:
        enabled: true
        strategy: ENCRYPT
        secret_key: secret
    compute_driver: vmwareapi.VMwareVCDriver
    vmware:
      host_username: vmware
      host_password: vmware
      cluster_name: vmware_cluster01
    upgrade_levels:
      compute: liberty
    libvirt_service_group: libvirtd
    lvm:
      ephemeral: yes
      images_volume_group: nova_vg
      volume_clear: zero
      volume_clear_size: 0
