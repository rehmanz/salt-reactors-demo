# Salt Stack Reactors 
Salt Stack's Reactor system provides the ability to trigger actions in response to events. This tutorial sets up a vagrant box and gives you a brief overview on reactors.

## Setup
1. Download & install [Vagrant](https://www.vagrantup.com/downloads.html) `2.0.0` and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) `5.0.0` or above.
2. Ensure vagrant-salt plugin is not installed as it may cause issues.
   ```shell
   vagrant plugin uninstall vagrant-salt
   ```

3. Create a workspace and clone `salt-reactors-demo` repository.
   ```shell
   mkdir ~/saltspace && cd ~/saltspace
   git clone git@github.com:rehmanz/salt-reactors-demo.git
   export WORKSPACE=~/saltspace/salt-reactors-demo/
   ```

4. Use Vagrant to create and provision Salt master and two minions.
   ```shell
   cd ${WORKSPACE}
   vagrant up --provider virtualbox
   ```

5. Validate provisioning via the ping test from Salt master
   ```shell
   vagrant ssh master
   sudo salt '*' test.ping
   ```
   
   You should see the following output.
   ```yml
   minion2:
    True
   minion1:
    True
   ```
   

## Salt Reactors

Salt Stack has internal and external reactors.
 
### Internal Reactors

Internal reactors are automatically triggered by Salt. Let's explore the structure.

1. Login into Salt master to explore.
    ```shell
    cd ${WORKSPACE}
    vagrant ssh master
    ```

2. Salt reactors allow you to define specific event tags and associate them with one or more reactions. This can be seen in Salt master `/etc/salt/master` config file under `reactor` section.
    ```yml
    reactor:
      - 'salt/demo/minion1/full_logs':
        - salt://reactor/cleanup_logs.sls
      - 'salt/demo/minion1/restart/ssh':
        - salt://reactor/restart_ssh_service.sls
    ```
    The above example shows `salt/demo/minion/full_logs` tag, which triggers the `cleanup_logs.sls` formula.
    
    The `cleanup_logs.sls` formula simply removes the log file.
    ```yml
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
   ```shell
   cd ${WORKSPACE}
   vagrant ssh minion1
   ```
   
3. Create a log file on `minion1` and manually trigger the event.
   ```shell
   echo "This is a test" > /tmp/log.txt
   sudo salt-call event.send 'salt/demo/minion1/full_logs'
   ```
   You will notice `/tmp/log.txt` file was removed due to `salt/demo/minion/full_logs` event sent to Salt master by `minion1`.

4. You can go back to the Salt master window and view the event output and reaction.
   ```yml
    # This is the event triggered by minion1
    salt/demo/minion1/full_logs	{
        "_stamp": "2017-09-24T23:30:37.659325", 
        "cmd": "_minion_event", 
        "data": {
            "__pub_fun": "event.send", 
            "__pub_jid": "20170924233038250552", 
            "__pub_pid": 16518, 
            "__pub_tgt": "salt-call"
        }, 
        "id": "minion1", 
        "tag": "salt/demo/minion1/full_logs"
    }
    
    
    # Salt Reactor ran this formula due to the event above    
    salt/job/20170924233037754615/ret/minion1	{
        "_stamp": "2017-09-24T23:30:37.794277", 
        "cmd": "_return", 
        "fun": "cmd.run", 
        "fun_args": [
            "rm /tmp/log.txt"
        ], 
        "id": "minion1", 
        "jid": "20170924233037754615", 
        "retcode": 0, 
        "return": "", 
        "success": true
    }
   ```




### External Reactors

External reactors are custom scripts (i.e. Bash, Python, Golang) that listen for specific tags from Salt event bus.

1. Let's view an external reactor by logging into the Salt master first.
    ```shell
    cd ${WORKSPACE}
    vagrant ssh master
    ```

2. `ui_reactor.py` script in `/srv/salt/formulas/base/reactor` directory provides a basic structure.
   ```python
    #!/usr/bin/env python
    
    import os
    import time
    import logging
    import argparse
    
    from Queue import Queue
    from threading import Thread
    from salt.utils.event import LocalClientEvent
    
    LOGGER = logging.getLogger()
    MAX_TIMEOUT_VALUE=60*5
    
    def __parse_record(event):
        payload = event.get('data', {})
        return payload.get('record', {})
    
    def get_event_payload(tag_id):
        for event in client.iter_events(tag=tag_id):
            payload = __parse_record(event)
            return payload
    
    def process_events():
        while True:
            if not q.empty():
                LOGGER.debug("#TODO: Implement correlation logic")
                LOGGER.debug("Waiting 20 seconds for all events to be registered")
                time.sleep(20)
    
                LOGGER.debug("Fetching all events from the event queue")
                while not q.empty():
                    msg_payload = q.get()
                    LOGGER.debug("msg_payload=%s" %msg_payload)
    
                timeout = time.time() + MAX_TIMEOUT_VALUE
                while time.time() < timeout:
                    try:
                        LOGGER.debug("#TODO: Implement complex reaction")
    
                    except Exception as e:
                        LOGGER.error("Failed to complete the reaction: %s" %(e))
                        # Send failure notification
                    break
    
                LOGGER.debug("#TODO: Implement validation & notification")
    
    if __name__ == '__main__':
        logging.basicConfig(level=logging.DEBUG)
        parser = argparse.ArgumentParser()
    
        """ Required Parameters Definition """
        parser.add_argument("environment", help="demo")
        args = parser.parse_args()
    
        target_env = args.environment
        tag_id = 'salt/%s/ui/slave/dead' %(target_env)
        client = LocalClientEvent("/var/run/salt/master")
    
        # Setup file handler
        fh= logging.FileHandler("/var/log/%s.log" %target_env)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        LOGGER.addHandler(fh)
    
        LOGGER.debug("##")
        LOGGER.debug("# Setting up UI Reactor for %s" %target_env)
        LOGGER.debug("##")
        q = Queue()
        worker = Thread(target=process_events)
        worker.setDaemon(True)
        worker.start()
        while True:
            event_payload = get_event_payload(tag_id)
            q.put(event_payload)
            LOGGER.info("Received an event=%s" %event_payload)
   ```

3. Now start the reactor process and monitor the log file for activity.
   ```shell
   sudo /srv/salt/formulas/base/reactor/ui_reactor.py demo &
   sudo tail -f /var/log/demo.log
   ```
   
4. In new shells, login to `minion1` and `minion2`.
    ```shell
    cd ${WORKSPACE}
    vagrant ssh minion1
    ```
    
    ```shell
    cd ${WORKSPACE}
    vagrant ssh minion2
    ```
    
5. Now trigger the dead event from both minions while monitoring log file activity on Salt Master.

   On `minion1` execute.
   ```shell
   sudo salt-call event.send 'salt/demo/ui/slave/dead' '{ 'record': { 'environment' : 'demo', 'node_type' : 'ui',  'node_id' : 'minion1' } }'
   ```
   
   On `minion2` execute.
   ```shell
   sudo salt-call event.send 'salt/demo/ui/slave/dead' '{ 'record': { 'environment' : 'demo', 'node_type' : 'ui',  'node_id' : 'minion2' } }'
   ```
   
   You will notice our reactor waited for both the events to be registered, before invoking the recovery logic.
   To learn more about reactors, Salt Stack [Reactor System](https://docs.saltstack.com/en/latest/topics/reactor/) is a great resource!
   