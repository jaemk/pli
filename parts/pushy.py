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
    def __init__(self, users, handle, queue):
        self.last_push = time.time()
        self.users = users
        self.handle = handle
        self.queue = queue
        # print(self.users, self.handle)
    
    def catch(self, event):
        # print('received: {}'.format(event))
        push_event = self.handle.get_pushes(self.last_push)
        if not push_event:
            return
        push = push_event[0]
        self.last_push = time.time()
        # print(push)
        push_items = push.keys()
        message_items = ['body', 'url', 'file_url']
        
        if push['dismissed'] == False:
            message = []
            for item in push_items:
                if item in message_items:
                    message.append(push[item])
                    # print('message {}: {}'.format(item, push[item]))
            self.queue.put(', '.join(message))
        else:
            pass
            # print('type: {} - dismissed'.format(event['type']))


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

