import os
import time
import signal
from blessed import Terminal

from multiprocessing import Process, Queue

import listener
import pusher


term = Terminal()
queue = Queue()


def _clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def clear_line(section=None, length=None, location=None):
    if section == None:
       section, col = term.get_location()
    elif section.lower() == 'input':
        section = input_section()  + 4
    elif section.lower() == 'sent':
        section = sent_section() + 2
    elif section.lower() == 'pushes':
        section = push_section() + 2

    if location != None:
        try:
            assert int(location)
            section = location
        except AssertionError:
            pass

    if not length:
        length = term.width

    print('{}{}'.format(term.move_y(section),
                        ' '*length))


def write_line(section=None, words=None, location=None):
    if section == None:
        section, col = term.get_location()
    elif section.lower() == 'input':
        section = input_section() + 4
    elif section.lower() == 'sent':
        section = sent_section() + 2
    elif section.lower() == 'pushes':
        section = push_section() + 2

    if location != None:
        try:
            assert int(location)
            section = location
        except AssertionError:
            pass
    
    if not words:
        words = ''

    print('{}{}'.format(term.move_y(section),
                        words))


def input_section():
    return 0


def sent_section():
    return term.height//4


def push_section():
    return term.height//2


def _get(q):
    if not q.empty():
        return q.get()
    return None


def _start_listener(target, arg):
    def _wrapper():
        target(arg)

    proc = Process(target=_wrapper,
                   name='Listener')
    proc.start()
    print('{} started'.format(proc.name))

    return proc


def _check_pushes(pushes):
    qval = _get(queue)
    # update = False
    if qval != None:
        pushes.append(qval)
        # update = True
        clear_line(section='pushes', length=len('\n'.join(pushes)))
        write_line(section='pushes', words='\n'.join(pushes))
        

def main():
    handle = pusher.get_handle()
    val = ''
    last_sent = []
    words = []
    longest_word = []
    pushes = []
       
    def write_headers(*args):
        ''' helped function to clear screen and redraw 
            section headers after a screen resize event'''
        _clear()

        # title
        write_line(location=input_section() + 0,
                   words=term.center('Welcome to PLI!'))

        # input section
        write_line(location=input_section() + 2,
                   words='_'*term.width)
        write_line(location=input_section() + 3, 
                   words=term.bold_underline('<<< User Input >>>'))
        write_line(section='input', words=''.join(words))

        # last message section
        write_line(location=sent_section() + 0,
                   words='_'*term.width)
        write_line(location=sent_section() + 1, 
                   words=term.bold_underline('<<< Last sent message >>>'))
        write_line(section='sent', words=''.join(last_sent))   

        # pushes section
        write_line(location=push_section() + 0,
                   words='_'*term.width)
        write_line(location=push_section() + 1,
                   words=term.bold_underline('<<< Recent Pushes >>>'))
        write_line(section='pushes', words = '\n'.join(pushes))
 
    #signal.signal(signal.SIGWINCH, write_headers)
    write_headers()
 
    while True:
        signal.signal(signal.SIGWINCH, write_headers)
        _check_pushes(pushes)
        
        val = term.inkey(timeout=2)
        if not val: # timeout
            pass    
        elif val.is_sequence:
            if val.name == 'KEY_ENTER':
                clear_line(section='input', length=len(longest_word))
                clear_line(section='sent', length=len(last_sent))
                write_line(section='sent', words=''.join(words))
                handle.push_note('', ''.join(words))
                last_sent = words[:]
                words = []
                longest_word = []
            elif val.name == 'KEY_DELETE':
                if len(words) > 0:
                    words.pop()
                    clear_line(section='input', length=len(longest_word))
                    longest_word = words[:]
        elif val == 'Q':
            _clear()
            write_line(section='sent', words=term.center('goodbye!'))
            time.sleep(1)
            return
        else:
            words.append(val)
            longest_word = words[:]
       
        write_line(section='input', words =''.join(words))


    print('bye!')
    

def start():
    with term.fullscreen():
        with term.cbreak():
            # try:
            proc = _start_listener(listener.run_as_process, queue)
            main()
            print('Wrapping up...')
            proc.terminate()
            # except:
            #     print('Wrapping up...')
            #     if proc.is_alive():
            #         proc.terminate()
    
if __name__ == '__main__':
    start()


