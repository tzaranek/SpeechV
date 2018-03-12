import subprocess

import win32pipe
import win32api
import win32file

import log


def show_help():
    print("Usage: use all speechv commands like you would with voice. Each command")
    print("       is executed after alt-tabbing once. There are also some")
    print("       additional commands exclusive to this prompt:")
    print()
    print("    'debug help'  : list this help information")
    print("    'debug quit'  : quit the interactive prompt")
    print("    'debug batch' : run commands from a file in speechv/batch_inputs")
    print()


def run_prompt(speechv_pipe):
    while True:
        try:
            command = input('-> ')
            command_words = command.split()
            if command_words[0].lower() == 'debug':
                try:
                    if command_words[1] == 'quit':
                        break
                    elif command_words[1] == 'help':
                        show_help()
                    elif command_words[1] == 'batch':
                        print('TODO')
                    else:
                        suggest_help(command)
                except IndexError:
                    suggest_help(command)
            else:
                win32file.WriteFile(speechv_pipe, command.encode())
        except KeyboardInterrupt:
            print()


def main():
    try:
        subprocess.check_call(['del', 'named_pipe'])
    except FileNotFoundError:
        pass # allow for no pre-existing named pipe

    with open('DEBUG_FLAG', 'w') as debug_flag:
        pass # create a file to let speechv.py know it should connect with us

    pipe = win32pipe.CreateNamedPipe(
            r'\\.\pipe\named_pipe',
            win32pipe.PIPE_ACCESS_DUPLEX, 
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            2, 65536, 65536, 300, None)


    print('Waiting to connect with SpeechV... ', end='')

    # Run speechv by starting up web-ext. We sever all input/output to the 
    # web-ext process so that the debug prompt remains clean. Using a bat
    # script must be done because web-ext couldn't be run from here (?)
    speechv = subprocess.Popen(['debug_helper.bat'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)

    log.info('waiting for speechv to start and connect with us...')
    win32pipe.ConnectNamedPipe(pipe, None)
    print('connected')

    show_help()
    run_prompt(pipe)

    for subprogram in ['firefox.exe', 'python.exe']:
        try:
            subprocess.check_call(['taskkill', '/T', '/F', '/IM', subprogram])
        except Exception as e:
            log.error(e)

    # clean up so that voice activated usage will work on future use
    subprocess.check_call(['del', 'DEBUG_FLAG'])

def suggest_help(bad_command):
    print("error: command '{}' is incomplete. Use 'debug help'"
            " for correct usage", bad_command)

if __name__ == '__main__':
    main()
