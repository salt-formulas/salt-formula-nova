nova_upgrade_verify:
  test.show_notification:
    - name: "dump_message_upgrade_nova_verify"
    - text: "Running nova.upgrade.verify"

include:
 - nova.upgrade.verify._api
