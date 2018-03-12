import subprocess

import win32pipe
import win32api
import win32file

import log


def show_help():
    print('TODO: help')


def run_prompt(speechv_pipe):
    while True:
        try:
            command = input('-> ')
            print('received command: ', command)
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
                win32file.WriteFile(speechv_pipe, (command + '\n').encode())
        except KeyboardInterrupt:
            print()


def main():
    try:
        subprocess.check_call(['del', 'named_pipe'])
    except FileNotFoundError:
        pass # allow for no pre-existing named pipe

    pipe = win32pipe.CreateNamedPipe(
            r'\\.\pipe\named_pipe',
            win32pipe.PIPE_ACCESS_DUPLEX, 
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            2, 65536, 65536, 300, None)

    # Run speechv by starting up web-ext. We sever all input/output to the 
    # web-ext process so that the debug prompt remains clean. Using a bat
    # script must be done because web-ext couldn't be run from here (?)
    speechv = subprocess.Popen(['debug_helper.bat'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)

    log.info('waiting for speechv to start and connect with us...')

    print('Waiting to connect with SpeechV... ', end='')
    win32pipe.ConnectNamedPipe(pipe, None)
    print('connected')

    win32file.WriteFile(pipe, 'hello world\n'.encode())

    run_prompt(pipe)

    for subprogram in ['firefox.exe', 'python.exe']:
        try:
            subprocess.check_call(['taskkill', '/T', '/F', '/IM', subprogram])
        except Exception as e:
            log.error(e)

    # TODO: quick start documentation printed at beginning of each session

def suggest_help(bad_command):
    print("error: command '{}' is incomplete. Use 'debug help'"
            " for correct usage", bad_command)

if __name__ == '__main__':
    main()
