cleanup log files:
  local.cmd.run:
    - tgt: 'minion1'
    - arg:
      - rm /tmp/log.txt
