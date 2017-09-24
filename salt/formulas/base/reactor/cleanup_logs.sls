restart_ssh_service:
  local.cmd.run:
    - args:
      - service ssh restart