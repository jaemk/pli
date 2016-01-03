#!/home/james/projects/pli/pbenv/bin/python


from pushbullet import Listener
from pushbullet import Pushbullet
import settings
import time


class SettingsError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ', '.join([str(arg) for arg in self.args])


class PushHandler(object):
    def __init__(self, users, handle):
        self.last_push = time.time()
        self.users = users
        self.handle = handle
        # print(self.users, self.handle)


    def read_push(self):
        while True:
            val = input('to push >> ').strip().lower()
            if val:
                self.handle.push_note('', val)


class Pushy(object):
    HPH = None
    HPP = None

    key = settings.API_KEY
    users = settings.USERS

    @classmethod
    def _connect(cls):
        if cls.key and cls.users:
            cls.pb = Pushbullet(cls.key)
            cls.handler = PushHandler(cls.users, cls.pb)
        else:
            raise SettingsError('Please check info in your settings.py file')

    @classmethod
    def _run(cls):
        cls.handler.read_push()

    @classmethod
    def _stop(cls):
        return


def get_handle():
    try:
        Pushy._connect()
        return Pushy.handler.handle
    except SettingsError as err:
        print('Error: ', err)
        


def main():
    try:
        Pushy._connect()
        Pushy._run()
    except (SettingsError, KeyboardInterrupt):
        Pushy._stop()


if __name__ == '__main__':
    main()

