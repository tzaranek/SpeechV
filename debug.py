import subprocess

import win32pipe
import win32api

import log

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
    speechv = subprocess.Popen(['debug_helper.bat'], 
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # TODO: quick start documentation printed at beginning of each session

    # FIXME: proof of concept
    for i in range(30):
        # TODO: add debug only commands, prefixed with 'debug'
        #  - quit, batch, help
        # TODO: create batch input file examples
        try:
            print('-> ', end='')
            what = input()
            print(what)
            if what.strip() == 'quit':
                break
        except KeyboardInterrupt:
            print()

    # TODO: this currently kills nothing. Figure out why. The current workaround
    # is to restart the command prompt after each use, but that sucks
    speechv.kill()
    

    log.info('waiting for speechv to start and connect with us...')
    print('Waiting to connect with SpeechV...')
    win32pipe.ConnectNamedPipe(pipe, None)

    # TODO: connect from speechv's side with the named pipe

if __name__ == '__main__':
    main()
