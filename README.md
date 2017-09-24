# Salt Stack Reactors 
Salt Stack reactors demo

## Installing Vagrant & Virtual Box 
1. Download & install [Vagrant](https://www.vagrantup.com/downloads.html) `2.0.0` and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) `5.0.0` or above
2. Ensure vagrant-salt plugin is not installed
   ```
   vagrant plugin uninstall vagrant-salt
   ```


## Project Setup
1. Create a workspace & clone salt-reactors-demo repo
   ```shell
   mkdir ~/saltspace && cd ~/saltspace
   git clone git@github.com:rehmanz/salt-reactors-demo.git
   export WORKSPACE=~/saltspace/salt-reactors-demo/
   ```

2. Use vagrant to create and provision Salt master and two minions
   ```
   cd ${WORKSPACE}
   vagrant up --provider virtualbox
   ```

3. Validate provisioning via the ping test from Salt master
   ```
   vagrant ssh master
   sudo salt '*' test.ping
   ```
   
   You should see the following output.
   ```
   minion2:
    True
   minion1:
    True
   ```
   

## Salt Reactors

Salt Stack has internal and external reactors.
 
#### Internal Reactors

Internal reactors are automatically triggered by Salt. Let's explore the structure.

1. Login into salt master to explore.
    ```
    cd ${WORKSPACE}
    vagrant ssh master
    ```

2. Salt Reactors allows you to define a specific event tag and associated reaction(s). This can be seen in Salt master `/etc/salt/master` config file.
    ```yml
    ...
    
    reactor:
      - 'salt/demo/minion1/full_logs':
        - salt://reactor/cleanup_logs.sls
      - 'salt/demo/minion1/restart/ssh':
        - salt://reactor/restart_ssh_service.sls  
    ```
    The above example shows `salt/demo/minion/full_logs` tag. It automatically triggers the `cleanup_logs.sls` formula.
    
    The cleanup formula looks simply removed the log file.
    ```
    cleanup log files:
      local.cmd.run:
        - tgt: 'minion1'
        - arg:
          - rm /tmp/log.txt
    ```


Let's see the internal reactors in action.
1. Start monitoring events on Salt master
   ```
   sudo salt-run state.event pretty=True
   ```
2. In a new shell, login to `minion1`
   ```
   cd ${WORKSPACE}
   vagrant ssh minion1
   ```
   
3. Create a log file on `minion1` and manually trigger the event.
   ```
   echo "This is a test" > /tmp/log.txt
   sudo salt-call event.send 'salt/demo/minion1/full_logs'
   ```
   You will notice `/tmp/log.txt` file was removed due to `salt/demo/minion/full_logs` event sent to Salt master by `minion1`.

4. You can go back to the Salt master window and view the event output and reaction.

