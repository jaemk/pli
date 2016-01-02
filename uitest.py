import signal
from blessed import Terminal
import time
import os

term = Terminal()

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
    return term.height//3


def main():
    val = ''
    last_sent = []
    words = []
    longest_word = []
       
    def write_headers(*args):
        _clear()
        write_line(location=input_section() + 0,
                   words=term.center('Welcome to PLI!'))
        write_line(location=input_section() + 2, 
                   words=term.bold_underline('<<< User Input >>>'))
        write_line(section='input', words=''.join(words))

        write_line(location=sent_section() + 0, 
                   words=term.bold_underline('<<< Last sent message >>>'))
        write_line(section='sent', words=''.join(last_sent))   
 
    signal.signal(signal.SIGWINCH, write_headers)
    write_headers()
 
    while True:
        val = term.inkey(timeout=10)
        if not val: # timeout
            pass
        elif val.is_sequence:
            if val.name == 'KEY_ENTER':
                clear_line(section='input', length=len(longest_word))
                clear_line(section='sent', length=len(last_sent))
                write_line(section='sent', words=''.join(words))
                last_sent = words[:]
                words = []
                longest_word = []
            elif val.name == 'KEY_DELETE':
                if len(words) > 0:
                    words.pop()
                    clear_line(section='input', length=len(longest_word))
                    longest_word = words[:]
        elif val.upper() == 'Q':
            write_line(section='sent', words=term.center('goodbye!'))
            time.sleep(1)
            return
        else:
            words.append(val)
            longest_word = words[:]
       
        write_line(section='input', words =''.join(words))

    print('bye!')
    

    
if __name__ == '__main__':
    with term.fullscreen():
        with term.cbreak():
            main()
