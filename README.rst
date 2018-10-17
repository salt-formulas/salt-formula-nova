
============
Usage
============

OpenStack Nova provides a cloud computing fabric controller, supporting a wide
variety of virtualization technologies, including KVM, Xen, LXC, VMware, and
more. In addition to its native API, it includes compatibility with the
commonly encountered Amazon EC2 and S3 APIs.

Sample Pillars
==============

Controller nodes
----------------

Nova services on the controller node:

.. code-block:: yaml

    nova:
      controller:
        version: juno
        enabled: true
        security_group: true
        cpu_allocation_ratio: 8.0
        ram_allocation_ratio: 1.0
        disk_allocation_ratio: 1.0
        cross_az_attach: false
        workers: 8
        report_interval: 60
        dhcp_domain: novalocal
        consoleauth_token_ttl: 600
        bind:
          public_address: 10.0.0.122
          public_name: openstack.domain.com
          novncproxy_port: 6080
        database:
          engine: mysql
          host: 127.0.0.1
          port: 3306
          name: nova
          user: nova
          password: pwd
        identity:
          engine: keystone
          host: 127.0.0.1
          port: 35357
          user: nova
          password: pwd
          tenant: service
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        pci:
          alias:
            alias1:
              device_type: "type-PF"
              name: "a1"
              product_id: "154d"
              vendor_id: "8086"
        network:
          engine: neutron
          host: 127.0.0.1
          port: 9696
          extension_sync_interval: 600
          identity:
            engine: keystone
            host: 127.0.0.1
            port: 35357
            user: neutron
            password: pwd
            tenant: service
        metadata:
          password: password
        audit:
          enabled: false
        osapi_max_limit: 500
        barbican:
          enabled: true

Nova services from custom package repository:

.. code-block:: yaml

    nova:
      controller:
        version: juno
        source:
          engine: pkg
          address: http://...
      ....

Client-side RabbitMQ HA setup:

.. code-block:: yaml

   nova:
     controller:
       ....
       message_queue:
         engine: rabbitmq
         members:
           - host: 10.0.16.1
           - host: 10.0.16.2
           - host: 10.0.16.3
         user: openstack
         password: pwd
         virtual_host: '/openstack'
      ....

Enable auditing filter, i.e: CADF:

.. code-block:: yaml

    nova:
      controller:
        audit:
          enabled: true
      ....
          filter_factory: 'keystonemiddleware.audit:filter_factory'
          map_file: '/etc/pycadf/nova_api_audit_map.conf'
      ....

Enable CORS parameters:

.. code-block:: yaml

    nova:
      controller:
        cors:
          allowed_origin: https:localhost.local,http:localhost.local
          expose_headers: X-Auth-Token,X-Openstack-Request-Id,X-Subject-Token
          allow_methods: GET,PUT,POST,DELETE,PATCH
          allow_headers: X-Auth-Token,X-Openstack-Request-Id,X-Subject-Token
          allow_credentials: True
          max_age: 86400

Configuration of the ``policy.json`` file:

.. code-block:: yaml

    nova:
      controller:
        ....
        policy:
          context_is_admin: 'role:admin or role:administrator'
          'compute:create': 'rule:admin_or_owner'
          # Add key without value to remove line from policy.json
          'compute:create:attach_network':

Enable Barbican integration:

.. code-block:: yaml

    nova:
      controller:
        ....
        barbican:
          enabled: true

Define aliases for PCI devices:
.. code-block:: yaml

    nova:
      controller:
        ...
        pci:
          alias:
            alias1:
              device_type: "type-PF"
              name: "a1"
              product_id: "154d"
              vendor_id: "8086"

Enable cells update:

.. note:: Useful when upgrading Openstack. To update cells to test
   sync db agains duplicated production database.

.. code-block:: yaml

    nova:
      controller:
        update_cells: true


Configuring TLS communications
------------------------------

.. note:: By default system wide installed CA certs are used,
   so ``cacert_file`` param is optional, as well as ``cacert``.

- **RabbitMQ TLS**

  .. code-block:: yaml

   nova:
     compute:
        message_queue:
          port: 5671
          ssl:
            enabled: True
            (optional) cacert: cert body if the cacert_file does not exists
            (optional) cacert_file: /etc/openstack/rabbitmq-ca.pem
            (optional) version: TLSv1_2

- **MySQL TLS**

  .. code-block:: yaml

   nova:
     controller:
        database:
          ssl:
            enabled: True
            (optional) cacert: cert body if the cacert_file does not exists
            (optional) cacert_file: /etc/openstack/mysql-ca.pem

- **Openstack HTTPS API**

  Set the ``https`` as protocol at ``nova:compute`` and
  ``nova:controller`` sections :

  .. code-block:: yaml

   nova:
     controller :
        identity:
           protocol: https
           (optional) cacert_file: /etc/openstack/proxy.pem
         network:
           protocol: https
           (optional) cacert_file: /etc/openstack/proxy.pem
        glance:
           protocol: https
           (optional) cacert_file: /etc/openstack/proxy.pem

  .. code-block:: yaml

   nova:
     compute:
        identity:
           protocol: https
           (optional) cacert_file: /etc/openstack/proxy.pem
        network:
           protocol: https
           (optional) cacert_file: /etc/openstack/proxy.pem
        image:
           protocol: https
           (optional) cacert_file: /etc/openstack/proxy.pem
        ironic:
           protocol: https
           (optional) cacert_file: /etc/openstack/proxy.pem

.. note:: Barbican, Cinder, and placement url endpoints are discovering
   using service catalog.

Compute nodes
-------------

Nova controller services on compute node:

.. code-block:: yaml

    nova:
      compute:
        version: juno
        enabled: true
        cross_az_attach: false
        disk_cachemodes: network=writeback,block=none
        availability_zone: availability_zone_01
        aggregates:
        - hosts_with_fc
        - hosts_with_ssd
        security_group: true
        resume_guests_state_on_host_boot: False
        preallocate_images: space  # Default is 'none'
        my_ip: 10.1.0.16
        bind:
          vnc_address: 172.20.0.100
          vnc_port: 6080
          vnc_name: openstack.domain.com
          vnc_protocol: http
        database:
          engine: mysql
          host: 127.0.0.1
          port: 3306
          name: nova
          user: nova
          password: pwd
        identity:
          engine: keystone
          host: 127.0.0.1
          port: 35357
          user: nova
          password: pwd
          tenant: service
        message_queue:
          engine: rabbitmq
          host: 127.0.0.1
          port: 5672
          user: openstack
          password: pwd
          virtual_host: '/openstack'
        image:
          engine: glance
          host: 127.0.0.1
          port: 9292
        pci:
          alias:
            alias1:
              device_type: "type-PF"
              name: "a1"
              product_id: "154d"
              vendor_id: "8086"
        network:
          engine: neutron
          host: 127.0.0.1
          port: 9696
          identity:
            engine: keystone
            host: 127.0.0.1
            port: 35357
            user: neutron
            password: pwd
            tenant: service
        qemu:
          max_files: 4096
          max_processes: 4096
        host: node-12.domain.tld

Compute with vmware driver. Each vmware cluster requires a separate process of nova-compute.
Each process should have uniq host identifier. However multiple computes might be running on
single host. It is not recommended to have multiple computes running on different hosts that
manage the same vmware cluster. To achive this pacemaker/corosync or keepalived might be used.

.. code-block:: yaml

    nova:
      compute:
        compute_driver: vmwareapi.VMwareVCDriver
        vmware:
          host_username: vmware
          host_password: vmware
          cluster_name: vmware_cluster01
          host_ip: 1.2.3.4

Group and user to be used for QEMU processes run by the system instance:

.. code-block:: yaml

    nova:
      compute:
        enabled: true
        ...
        qemu:
          user: nova
          group: cinder
          dynamic_ownership: 1

Group membership for user nova (upgrade related):

.. code-block:: yaml

    nova:
      compute:
        enabled: true
        ...
        user:
          groups:
          - libvirt

Nova services on compute node with OpenContrail:

.. code-block:: yaml

    nova:
      compute:
        enabled: true
        ...
        networking: contrail

Nova services on compute node with memcached caching:

.. code-block:: yaml

    nova:
      compute:
        enabled: true
        ...
        cache:
          engine: memcached
          members:
          - host: 127.0.0.1
            port: 11211
          - host: 127.0.0.1
            port: 11211

Client-side RabbitMQ HA setup:

.. code-block:: yaml

   nova:
     compute:
       ....
       message_queue:
         engine: rabbitmq
         members:
           - host: 10.0.16.1
           - host: 10.0.16.2
           - host: 10.0.16.3
         user: openstack
         password: pwd
         virtual_host: '/openstack'
      ....

Nova with ephemeral configured with Ceph:

.. code-block:: yaml

    nova:
      compute:
        enabled: true
        ...
        ceph:
          ephemeral: yes
          rbd_pool: nova
          rbd_user: nova
          secret_uuid: 03006edd-d957-40a3-ac4c-26cd254b3731
      ....

Nova with ephemeral configured with LVM:

.. code-block:: yaml

    nova:
      compute:
        enabled: true
        ...
        lvm:
          ephemeral: yes
          images_volume_group: nova_vg

    linux:
      storage:
        lvm:
          nova_vg:
            name: nova_vg
            devices:
              - /dev/sdf
              - /dev/sdd
              - /dev/sdg
              - /dev/sde
              - /dev/sdc
              - /dev/sdj
              - /dev/sdh

Enable Barbican integration:

.. code-block:: yaml

    nova:
      compute:
        ....
        barbican:
          enabled: true

Define aliases for PCI devices:
.. code-block:: yaml

    nova:
      compute:
        ...
        pci:
          alias:
            alias1:
              device_type: "type-PF"
              name: "a1"
              product_id: "154d"
              vendor_id: "8086"

Nova metadata custom bindings:

.. code-block:: yaml

    nova:
      controller:
        enabled: true
        ...
        metadata:
          bind:
            address: 1.2.3.4
            port: 8776

Client role
-----------

Nova configured with NFS:

.. code-block:: yaml

    nova:
      compute:
        instances_path: /mnt/nova/instances

    linux:
      storage:
        enabled: true
        mount:
          nfs_nova:
            enabled: true
            path: ${nova:compute:instances_path}
            device: 172.31.35.145:/data
            file_system: nfs
            opts: rw,vers=3

Nova flavors:

.. code-block:: yaml

  nova:
    client:
      enabled: true
      server:
        identity:
          flavor:
            flavor1:
              flavor_id: 10
              ram: 4096
              disk: 10
              vcpus: 1
            flavor2:
              flavor_id: auto
              ram: 4096
              disk: 20
              vcpus: 2
        identity1:
          flavor:
            ...

Availability zones:

.. code-block:: yaml

    nova:
      client:
        enabled: true
        server:
          identity:
            availability_zones:
            - availability_zone_01
            - availability_zone_02

Aggregates:

.. code-block:: yaml

    nova:
      client:
        enabled: true
        server:
          identity:
            aggregates:
            - aggregate1
            - aggregate2

Upgrade levels:

.. code-block:: yaml

    nova:
      controller:
        upgrade_levels:
          compute: juno

    nova:
      compute:
        upgrade_levels:
          compute: juno

SR-IOV
------

Add ``PciPassthroughFilter`` into scheduler filters and NICs on
specific compute nodes:

.. code-block:: yaml

  nova:
    controller:
      sriov: true
      scheduler_default_filters: "DifferentHostFilter,SameHostFilter,RetryFilter,AvailabilityZoneFilter,RamFilter,CoreFilter,DiskFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,PciPassthroughFilter"

  nova:
    compute:
      sriov:
        nic_one:
          devname: eth1
          physical_network: physnet1

.. note:: Parameters located under nova:compute:sriov:<nic_name> are copied to passthrough_whitelist parameter into
          nova.conf file in appropriate format.

CPU pinning & Hugepages
-----------------------

CPU pinning of virtual machine instances to dedicated physical
CPU cores. Hugepages mount point for libvirt.

.. code-block:: yaml

  nova:
    controller:
      scheduler_default_filters: "DifferentHostFilter,SameHostFilter,RetryFilter,AvailabilityZoneFilter,RamFilter,CoreFilter,DiskFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,NUMATopologyFilter,AggregateInstanceExtraSpecsFilter"

  nova:
    compute:
      vcpu_pin_set: 2,3,4,5
      hugepages:
        mount_points:
        - path: /mnt/hugepages_1GB
        - path: /mnt/hugepages_2MB

Custom Scheduler filters
------------------------

If you have a custom filter, that needs to be included in the
scheduler, then you can include it like so:

.. code-block:: yaml

  nova:
    controller:
      scheduler_custom_filters:
      - my_custom_driver.nova.scheduler.filters.my_custom_filter.MyCustomFilter

      # Then add your custom filter on the end (make sure to include all other ones that you need as well)
      scheduler_default_filters: "DifferentHostFilter,SameHostFilter,RetryFilter,AvailabilityZoneFilter,RamFilter,CoreFilter,DiskFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,PciPassthroughFilter,MyCustomFilter"

Hardware Trip/Unmap Support
---------------------------

To enable TRIM support for ephemeral images (thru nova managed
images), libvirt has this option:

.. code-block:: yaml

  nova:
    compute:
      libvirt:
        hw_disk_discard: unmap

To actually utilize this feature, the following metadata must be
set on the image as well, so the SCSI unmap is supported:

.. code-block:: bash

  glance image-update --property hw_scsi_model=virtio-scsi <image>
  glance image-update --property hw_disk_bus=scsi <image>

Scheduler Host Manager
----------------------

Specify a custom host manager.

libvirt CPU mode
----------------

Allow setting the model of CPU that is exposed to a VM. This
allows for better support live migration between hypervisors with
different hardware, among other things. Defaults to host-passthrough.

.. code-block:: yaml

  nova:
    controller:
      scheduler_host_manager: ironic_host_manager

    compute:
      cpu_mode: host-model

Nova compute cpu model
----------------------

.. code-block:: yaml

  nova:
    compute:
      cpu_mode: custom
      libvirt:
        cpu_model: IvyBridge


Nova compute workarounds
------------------------

Live snapshotting is disabled by default in nova. To enable
this, it needs a manual switch.

From manual:

.. code-block:: yaml

  When using libvirt 1.2.2 live snapshots fail intermittently under load
  (likely related to concurrent libvirt/qemu operations). This config
  option provides a mechanism to disable live snapshot, in favor of cold
  snapshot, while this is resolved. Cold snapshot causes an instance
  outage while the guest is going through the snapshotting process.

  For more information, refer to the bug report:

  https://bugs.launchpad.net/nova/+bug/1334398

Configurable pillar data:

.. code-block:: yaml

  nova:
    compute:
      workaround:
        disable_libvirt_livesnapshot: False

Config drive options
--------------------

See example below on how to configure the options for the
config drive:

.. code-block:: yaml

  nova:
    compute:
      config_drive:
        forced: True  # Default: True
        cdrom: True  # Default: False
        format: iso9660  # Default: vfat
        inject_password: False  # Default: False

Number of concurrent live migrates
----------------------------------

Default is to have no concurrent live migrations (so 1
live-migration at a time).

Excerpt from config options page
https://docs.openstack.org/ocata/config-reference/compute/config-options.html:

Maximum number of live migrations to run concurrently. This limit is
enforced to avoid outbound live migrations overwhelming the host/network
and causing failures. It is not recommended that you change this unless
you are very sure that doing so is safe and stable in your environment.

Possible values:

- 0 : treated as unlimited.
- Negative value defaults to 0.
- Any positive integer representing maximum number of live migrations
  to run concurrently.

To configure this option:

.. code-block:: yaml

  nova:
    compute:
      max_concurrent_live_migrations: 1  # (1 is the default)

Live migration with auto converge
----------------------------------

Auto converge throttles down CPU if a progress of on-going live
migration is slow
https://docs.openstack.org/ocata/config-reference/compute/config-options.html:

.. code-block:: yaml

  nova:
    compute:
      libvirt:
        live_migration_permit_auto_converge: False  # (False is the default)

.. code-block:: yaml

  nova:
    controller:
      libvirt:
        live_migration_permit_auto_converge: False  # (False is the default)

Enhanced logging with logging.conf
----------------------------------

By default ``logging.conf`` is disabled.

That is possible to enable per-binary logging.conf with new variables:

* ``openstack_log_appender``
   Set to true to enable log_config_append for all OpenStack services

* ``openstack_fluentd_handler_enabled``
   Set to true to enable FluentHandler for all Openstack services

* ``openstack_ossyslog_handler_enabled``
   Set to true to enable OSSysLogHandler for all Openstack services

Only ``WatchedFileHandler``, ``OSSysLogHandler``, and ``FluentHandler``
are available.

Also it is possible to configure this with pillar:

.. code-block:: yaml

  nova:
    controller:
        logging:
          log_appender: true
          log_handlers:
            watchedfile:
              enabled: true
            fluentd:
              enabled: true
            ossyslog:
              enabled: true

    compute:
        logging:
          log_appender: true
          log_handlers:
            watchedfile:
              enabled: true
            fluentd:
              enabled: true
            ossyslog:
              enabled: true

The log level might be configured per logger by using the
following pillar structure:

.. code-block:: yaml

  nova:
    compute:
      logging:
        loggers:
          <logger_name>:
            level: WARNING

  nova:
    compute:
      logging:
        loggers:
          <logger_name>:
            level: WARNING

Configure syslog parameters for libvirtd
----------------------------------------

To configure syslog parameters for libvirtd the below pillar
structure should be used with values which are supported
by libvirtd. These values might be known from the documentation.

.. code-block:: yaml

 nova:
   compute:
     libvirt:
       logging:
         level: 3
         filters: '3:remote 4:event'
         outputs: '3:syslog:libvirtd'
         buffer_size: 64

Logging controls:

Logging level: 4 errors, 3 warnings, 2 information, 1 debug
basically 1 will log everything possible ``log_level = 3``

Logging filters:

A filter allows to select a different logging level for a given category
of logs.

The format for a filter is one of:

* ``x:name``
* ``x:+name``
   where name is a string which is matched against source file name,
   e.g., ``remote``, ``qemu``, or ``util/json``, the optional ``+`` prefix
   tells libvirt to log stack trace for each message matching name,
   and x is the minimal level where matching messages should be logged:

* ``1: DEBUG``
* ``2: INFO``
* ``3: WARNING``
* ``4: ERROR``

Multiple filter can be defined in a single @filters, they just
need to be separated by spaces.

For example, to only get warning or errors from the remote layer
and only errors from the event layer: ``log_filters="3:remote 4:event``

Logging outputs:

An output is one of the places to save logging information
The format for an output can be:

* ``x:stderr``
   Output goes to stderr

* ``x:syslog:name``
   Use syslog for the output and use the given name as the ident

* ``x:file:file_path``
   output to a file, with the given filepath

   In all case the x prefix is the minimal level, acting as a filter

* ``1: DEBUG``
* ``2: INFO``
* ``3: WARNING``
* ``4: ERROR``

Multiple output can be defined, they just need to be separated by spaces.
For example, to log all warnings and errors to syslog under the libvirt
dident: ``log_outputs="3:syslog:libvirtd``

Log debug buffer size: default 64
The daemon keeps an internal debug log buffer which will be dumped
in case of crash or upon receiving a ``SIGUSR2`` signal. This setting
allows to override the default buffer size in kilobytes.
If value is ``0`` or less the debug log buffer is deactivated
``log_buffer_size = 64``

To configure the logging parameters for QEMU, the below pillar
structure and logging parameters should be used:

.. code-block:: yaml

   nova:
     compute:
        qemu:
          logging:
            handler: logd
        virtlog:
          enabled: true
          level: 4
          filters: '3:remote 3:event'
          outputs: '4:syslog:virtlogd'
          max_clients: 512
          max_size: 2097100
          max_backups: 2

Inject password to VM
---------------------

By default nova blocks up any inject to VM because
``inject_partition`` param is equal to ``-2``.
If you want to inject password to VM, you will need to
define ``inject_partition`` greater or equal to ``-1`` and
define ``inject_password`` to ``True``

For example:

.. code-block:: yaml

  nova:
    compute:
      inject_partition: '-1'
      inject_password: True

Allow the injection of an admin password for instance only at
``create`` and ``rebuild`` process.

There is no agent needed within the image to do this. If *libguestfs* is
available on the host, it will be used. Otherwise *nbd* is used. The file
system of the image will be mounted and the admin password, which is provided
in the REST API call will be injected as password for the root user. If no
root user is available, the instance won't be launched and an error is thrown.
Be aware that the injection is *not* possible when the instance gets launched
from a volume.

Possible values:

* ``True``
   Allows the injection

* ``False`` (default)
   Disallows the injection. Any via the REST API provided
   admin password will be silently ignored.

Related options:

* ``inject_partition``
   Decides about the discovery and usage of the file system.
   It also can disable the injection at all.
   (boolean value)

You can read more about injecting the administrator password here:
https://docs.openstack.org/nova/queens/admin/admin-password-injection.html

Enable libvirt control channel over TLS
---------------------------------------

By default TLS is disabled.

Enable TLS transport:

.. code-block:: yaml

  compute:
    libvirt:
      tls:
        enabled: True

You able to set custom certificates in pillar:

.. code-block:: yaml

  nova:
    compute:
      libvirt:
        tls:
          key: (certificate content)
          cert: (certificate content)
          cacert: (certificate content)
          client:
            key: (certificate content)
            cert: (certificate content)

Controlling access by `tls_allowed_dn_list`.
Enable an access control list of client certificate Distinguished Names (DNs)
which can connect to the TLS port on this server. The default is that DNs are
not checked. This list may contain wildcards such as
"C=GB,ST=London,L=London,O=Libvirt Project,CN=*" See the POSIX fnmatch function
for the format of the wildcards.
Note that if this is an empty list, no client can connect.
Note also that GnuTLS returns DNs without spaces after commas between
the fields (and this is what we check against), but the openssl x509 tool
shows spaces.

.. code-block:: yaml

  nova:
    compute:
      libvirt:
        tls:
          tls_allowed_dn_list:
            host1:
              enabled: true
              value: 'C=foo,CN=cmp1'
            host2:
              enabled: true
              value: 'C=foo,CN=cmp2'


You can read more about live migration over TLS here:
https://wiki.libvirt.org/page/TLSCreateServerCerts

Enable transport + authentication for VNC over TLS
---------------------
# Only for Queens. Communication between noVNC proxy service and QEMU

By default communication between nova-novncproxy and qemu service is unsecure.

compute:
  qemu:
    vnc:
      tls:
        enabled: True

controller:
  novncproxy:
    # This section responsible for communication between noVNC proxy and client machine
    tls:
      enabled: True
    # This section responsible for communication between nova-novncproxy and qemu service
    vencrypt:
      tls:
        enabled: True

You able to set custom certificates in pillar:

nova:
  compute:
    qemu:
      vnc:
        tls:
          cacert (certificate content)
          cert (certificate content)
          key (certificate content)

nova:
  controller:
    novncproxy:
      tls:
        server:
          cert (certificate content)
          key (certificate content)
      vencrypt:
        tls:
          cacert (certificate content)
          cert (certificate content)
          key (certificate content)


You can read more about it here:
    https://docs.openstack.org/nova/queens/admin/remote-console-access.html

Enable communication between noVNC proxy and client machine over TLS
---------------------

By default communication between noVNC proxy and client machine is unsecure.

  controller:
    novncproxy:
      tls:
        enabled: True

  nova:
    controller:
      novncproxy:
        tls:
          server:
            cert (certificate content)
            key (certificate content)

You can read more about it here:
    https://docs.openstack.org/mitaka/config-reference/dashboard/configure.html

Enable x509 and ssl communication between Nova and Galera cluster.
---------------------
By default communication between Nova and Galera is unsecure.

nova:
  controller:
    database:
      x509:
        enabled: True

You able to set custom certificates in pillar:

nova:
  controller:
    database:
      x509:
        cacert: (certificate content)
        cert: (certificate content)
        key: (certificate content)

You can read more about it here:
    https://docs.openstack.org/security-guide/databases/database-access-control.html

Upgrades
========

Each openstack formula provide set of phases (logical bloks) that will help to
build flexible upgrade orchestration logic for particular components. The list
of phases might and theirs descriptions are listed in table below:

+-------------------------------+------------------------------------------------------+
| State                         | Description                                          |
+===============================+======================================================+
| <app>.upgrade.service_running | Ensure that all services for particular application  |
|                               | are enabled for autostart and running                |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.service_stopped | Ensure that all services for particular application  |
|                               | disabled for autostart and dead                      |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.pkgs_latest     | Ensure that packages used by particular application  |
|                               | are installed to latest available version.           |
|                               | This will not upgrade data plane packages like qemu  |
|                               | and openvswitch as usually minimal required version  |
|                               | in openstack services is really old. The data plane  |
|                               | packages should be upgraded separately by `apt-get   |
|                               | upgrade` or `apt-get dist-upgrade`                   |
|                               | Applying this state will not autostart service.      |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.render_config   | Ensure configuration is rendered actual version.     +
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.pre             | We assume this state is applied on all nodes in the  |
|                               | cloud before running upgrade.                        |
|                               | Only non destructive actions will be applied during  |
|                               | this phase. Perform service built in service check   |
|                               | like (keystone-manage doctor and nova-status upgrade)|
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.upgrade.pre     | Mostly applicable for data plane nodes. During this  |
|                               | phase resources will be gracefully removed from      |
|                               | current node if it is allowed. Services for upgraded |
|                               | application will be set to admin disabled state to   |
|                               | make sure node will not participate in resources     |
|                               | scheduling. For example on gtw nodes this will set   |
|                               | all agents to admin disable state and will move all  |
|                               | routers to other agents.                             |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.upgrade         | This state will basically upgrade application on     |
|                               | particular target. Stop services, render             |
|                               | configuration, install new packages, run offline     |
|                               | dbsync (for ctl), start services. Data plane should  |
|                               | not be affected, only OpenStack python services.     |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.upgrade.post    | Add services back to scheduling.                     |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.post            | This phase should be launched only when upgrade of   |
|                               | the cloud is completed. Cleanup temporary files,     |
|                               | perform other post upgrade tasks.                    |
+-------------------------------+------------------------------------------------------+
| <app>.upgrade.verify          | Here we will do basic health checks (API CRUD        |
|                               | operations, verify do not have dead network          |
|                               | agents/compute services)                             |
+-------------------------------+------------------------------------------------------+

Documentation and Bugs
======================

* http://salt-formulas.readthedocs.io/
   Learn how to install and update salt-formulas

* https://github.com/salt-formulas/salt-formula-nova/issues
   In the unfortunate event that bugs are discovered, report the issue to the
   appropriate issue tracker. Use the Github issue tracker for a specific salt
   formula

* https://launchpad.net/salt-formulas
   For feature requests, bug reports, or blueprints affecting the entire
   ecosystem, use the Launchpad salt-formulas project

* https://launchpad.net/~salt-formulas-users
   Join the salt-formulas-users team and subscribe to mailing list if required

* https://github.com/salt-formulas/salt-formula-nova
   Develop the salt-formulas projects in the master branch and then submit pull
   requests against a specific formula

* #salt-formulas @ irc.freenode.net
   Use this IRC channel in case of any questions or feedback which is always
   welcome
