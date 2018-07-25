linux:
  system:
    enabled: true
    repo:
      mirantis_openstack_repo:
        source: "deb http://mirror.fuel-infra.org/mcp-repos/pike/{{ grains.get('oscodename') }} pike main"
        architectures: amd64
        key_url: "http://mirror.fuel-infra.org/mcp-repos/pike/{{ grains.get('oscodename') }}/archive-mcppike.key"
        pin:
        - pin: 'release a=pike'
          priority: 1050
          package: '*'