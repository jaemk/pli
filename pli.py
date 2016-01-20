import os
import sys
import time
import signal
from blessed import Terminal

from multiprocessing import Process, Queue

import listener
import pusher


term = Terminal()
queue = Queue()


def _clear():
    ''' clear screen wrapper '''
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def input_section():
    ''' return section of user input '''
    return 0


def sent_section():
    ''' return section of sent messages '''
    return term.height//4


def push_section():
    ''' return section of pushes '''
    return term.height//2


def clear_line(section=None, length=None, location=None):
    ''' clear lines in specified section 
        section={input | sent |pushes }
        optional, location=int 
                  length=int '''
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
            section = int(location)
        except ValueError:
            pass

    if not length:
        length = term.width

    print('{}{}'.format(term.move_y(section),
                        ' '*length))


def write_line(section=None, words=None, location=None):
    ''' write lines in specified section 
        section={input | sent |pushes }
        optional, location=int
                  words=str '''
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
            section = int(location)
        except ValueError:
            pass
    
    if not words:
        words = ''

    print('{}{}'.format(term.move_y(section),
                        words))


def _start_listener(target, arg):
    ''' start push listener as a process '''
    def _wrapper():
        target(arg)

    proc = Process(target=_wrapper,
                   name='Listener')
    proc.start()
    print('{} started'.format(proc.name))
    time.sleep(1)
    return proc


def _get(q):
    ''' pull latest push from proc queue '''
    if not q.empty():
        return q.get()
    return None


def _check_pushes(pushes):
    ''' check for new pushes,
        redraw the pushes section '''
    qval = _get(queue)
    if qval != None:
        pushes.append(qval)
        clear_line(section='pushes', length=len('\n'.join(pushes)))
        write_line(section='pushes', words='\n'.join(pushes))

       
def write_headers(words, last_sent, pushes, *args):
    ''' helper to clear screen and redraw section 
        headers after a screen resize event (SIGWINCH)'''
    _clear()

    # draw title
    write_line(location=input_section() + 0,
               words=term.center('Welcome to PLI! -- (input \'Q\' to exit)'))
    
    # draw input section
    write_line(location=input_section() + 2,
               words='_'*term.width)
    write_line(location=input_section() + 3, 
               words=term.bold_underline('<<< User Input >>>'))
    write_line(section='input', words=''.join(words))
    
    # draw last message section
    write_line(location=sent_section() + 0,
               words='_'*term.width)
    write_line(location=sent_section() + 1, 
               words=term.bold_underline('<<< Last sent message >>>'))
    write_line(section='sent', words=''.join(last_sent))   
    
    # draw pushes section
    write_line(location=push_section() + 0,
               words='_'*term.width)
    write_line(location=push_section() + 1,
               words=term.bold_underline('<<< Recent Pushes >>>'))
    write_line(section='pushes', words = '\n'.join(pushes))


def main():
    handle = pusher.get_handle()
    val = ''
    last_sent = []
    words = []
    longest_word = []
    pushes = []

    # draw initial sections
    write_headers(words, last_sent, pushes)
 
    while True:
        # attach a signal window resize event, redraw sections
        signal.signal(signal.SIGWINCH, write_headers)
    
        _check_pushes(pushes)
        
        val = term.inkey(timeout=2)
        if not val: 
            # input timeout
            pass    
        elif val.is_sequence: 
            # key sequence e.g. enter or delete
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
            # exit keystroke
            _clear()
            write_line(section='sent', words=term.center('goodbye!'))
            time.sleep(1)
            return
        else: 
            # regular keystroke 
            words.append(val)
            longest_word = words[:]
       
        # update input section
        write_line(section='input', words =''.join(words))

    print('bye!')
    

def start():
    with term.fullscreen():
        with term.cbreak():
            try:
                proc = _start_listener(listener.run_as_process, queue)
                main()
            except (Exception, KeyboardInterrupt) as exc:
                print('Error: {}'.format(exc))
            else:
                print('Wrapping up...')
                if proc.is_alive():
                    proc.terminate()
    
if __name__ == '__main__':
    start()


