# Salt Stack Reactors 
Salt Stack reactors demo

## Installing Vagrant & Virtual Box 
1. Download & install [Vagrant](https://www.vagrantup.com/downloads.html) `2.0.0` and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) `5.0.0` or above
2. Ensure vagrant-salt plugin is not installed
   ```
   $ vagrant plugin uninstall vagrant-salt
   ```


## Project Setup
1. Create a workspace & clone salt-reactors-demo repo
   ```
   $ mkdir ~/saltspace && cd ~/saltspace
   $ git clone git@github.com:rehmanz/salt-reactors-demo.git
   $ export WORKSPACE="~/saltspace/salt-reactors-demo"
   ```

2. Use vagrant to create and provision Salt master and two minions
   ```
   $ cd ${WORKSPACE}
   $ vagrant up --provider virtualbox
   ```

3. Validate provisioning via the ping test from Salt master
   ```
   $ vagrant ssh master
   $ sudo salt '*' test.ping
   
   minion2:
    True
   minion1:
    True
   ```
   

## Salt Reactors

Salt Stack has internal and external reactors.
 
#### Internal Reactors

Salt Reactors allows you to define a specific tag and associate to a specific set of action. 

1. Let's login into salt master to explore.
    ```
    $ cd ${WORKSPACE}
    $ vagrant ssh master
    ```

2. Reactor configuration files can be view via `sudo vi /etc/salt/master` command.
    ```
    ...
    
    reactor:
      - 'salt/demo/minion1/full_logs':
        - salt://reactor/cleanup_logs.sls
      - 'salt/demo/minion1/restart/ssh':
        - salt://reactor/restart_ssh_service.sls  
    ```
    Salt Reactors allows you to define a specific event tag and associated reaction(s). For example, when `salt/demo/minion/full_logs` event is received, we trigger the `cleanup_logs.sls` formula.
    
    The cleanup formula looks simply removed the log file.
    ```
    cleanup log files:
      local.cmd.run:
        - tgt: 'minion1'
        - arg:
          - rm /tmp/log.txt
    ```
3. 