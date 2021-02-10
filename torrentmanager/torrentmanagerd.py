import argparse
import os
import sys
from pathlib import Path

from . import torrentmanager


PID = None
BASE_PATH = "%s/.torrentmanager" % Path.home()
PID_FILE = "%s/daemon.pid" % BASE_PATH
LOG_FILE = "%s/torrenmanager.log" % BASE_PATH

is_running = False


def _start():
    try:
        n = os.fork()
        if n > 0:
            sys.exit(0)
    except OSError as e:
        print("Error while forking process: %s" % e)
    os.chdir("/")
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork()
        if pid > 0:
            exit(0)
    except OSError as e:
        print("Error on second fork: %s" % e)
    sys.stdout = open(LOG_FILE, "w", buffering=1)
    print("started child process")
    PID = os.getpid()
    with open(PID_FILE, "w") as f:
        f.write(str(PID))
    try:
        torrentmanager.main({'watch': True})
    except Exception as e:
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print("Unexpected exit: %s" % e)


def _stop(pid):
    try:
        os.kill(int(pid), 9)
    except ProcessLookupError as e:
        print("Process stoped")
    os.remove(PID_FILE)


def run_in_background():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        metavar="(start|stop|status|restart)"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose mode"
    )
    args = vars(parser.parse_args())
    command = args["command"]
    is_running = os.path.isfile(PID_FILE)
    if is_running:
        with open(PID_FILE, "r") as f:
            PID = f.read()
    if command == "start":
        if is_running:
            print("Daemon is already running; PID: %s" % PID)
            sys.exit(1)
        _start()
    elif command == "stop":
        if not is_running:
            print("Daemon is not running")
            sys.exit(1)
        _stop(PID)
        sys.exit(0)
    elif command == "restart":
        if not is_running:
            print("Daemon is not running")
            sys.exit(1)
        _stop(PID)
        _start()
    elif command == "status":
        if is_running:
            print("Daemon is running on PID %s" % PID)
        else:
            print("Daemon is not running")


if __name__ == "__main__":
    run_in_background()
