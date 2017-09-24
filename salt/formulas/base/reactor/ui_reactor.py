# /srv/salt/reactor/ui_reactor.py
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
            LOGGER.debug("Waiting 60 seconds for all events to be registered")
            time.sleep(60)

            LOGGER.debug("Fetching all events from the event queue")
            while not q.empty():
                msg_payload = q.get()
                LOGGER.debug("msg_payload=%s" %msg_payload)

            timeout = time.time() + MAX_TIMEOUT_VALUE
            while time.time() < timeout:
                try:
                    LOGGER.debug("Implement complex reaction here")

                except Exception as e:
                    LOGGER.error("Failed to complete the reaction: %s" %(e))
                    # Send failure notification
                break

            LOGGER.debug("Implement notification summary")

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