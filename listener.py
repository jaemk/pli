#!/home/james/projects/pli/pbenv/bin/python

from pushbullet import Listener
from pushbullet import Pushbullet
from pusher import SettingsError
from pusher import PushHandler
import settings
import time


class Pushy(object):
    HPH = None
    HPP = None
    key = settings.API_KEY
    users = settings.USERS
    ear = None

    @classmethod
    def _connect(cls, queue):
        if cls.key and cls.users:
            cls.pb = Pushbullet(cls.key)
            cls.handler = PushHandler(cls.users, cls.pb, queue)
            cls.ear = Listener(account=cls.pb,
                               on_push=cls.handler.catch,
                               http_proxy_host=cls.HPH,
                               http_proxy_port=cls.HPP)
        else:
            raise SettingsError('Please check info in your settings.py file')

    @classmethod
    def _run(cls):
        cls.ear.run_forever()

    @classmethod
    def _stop(cls):
        if cls.ear:
            cls.ear.close()


def run_as_process(queue):
    try:
        Pushy._connect(queue)
        Pushy._run()
    except:
        Pushy._stop()


def main():
    try:
        Pushy._connect()
        Pushy._run()
    except (SettingsError, KeyboardInterrupt):
        Pushy._stop()


if __name__ == '__main__':
    main()

