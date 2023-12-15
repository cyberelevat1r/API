import binascii
import hashlib
import json
import logging
import random
import socket
import threading
import time
import traceback
from datetime import datetime
from signal import SIGINT, signal
from multiprocessing import cpu_count

import requests
from colorama import Back, Fore, Style

import context as ctx

sock = None

def timer():
    tcx = datetime.now().time()
    return tcx

# ... (unchanged code)

class CoinMinerThread(ExitedThread):
    def __init__(self, arg=None):
        super(CoinMinerThread, self).__init__(arg, n=0)

    def thread_handler2(self, arg):
        self.thread_bitcoin_miner(arg)

    def thread_bitcoin_miner(self, arg):
        ctx.listfThreadRunning[self.n] = True
        check_for_shutdown(self)
        try:
            ret = bitcoin_miner(self)
            logg(Fore.MAGENTA, "[", timer(), "] [*] Miner returned %s\n\n" % "true" if ret else "false")
            print(Fore.LIGHTCYAN_EX, "[*] Miner returned %s\n\n" % "true" if ret else "false")
        except Exception as e:
            logg("[*] Miner()")
            print(Back.WHITE, Fore.MAGENTA, "[", timer(), "]", Fore.BLUE, "[*] Miner()")
            logg(e)
            traceback.print_exc()
        ctx.listfThreadRunning[self.n] = False

    pass

def StartMining():
    # Get the number of CPU cores available
    num_threads = cpu_count()

    subscribe_t = NewSubscribeThread(None)
    subscribe_t.start()
    logg("[*] Subscribe thread started.")
    print(Fore.MAGENTA, "[", timer(), "]", Fore.GREEN, "[*] Subscribe thread started.")

    time.sleep(4)

    # Create multiple mining threads
    miner_threads = [CoinMinerThread(None) for _ in range(num_threads)]

    # Start all mining threads
    for t in miner_threads:
        t.start()

    logg("[*] Bitcoin Miner Threads Started")
    print(Fore.MAGENTA, "[", timer(), "]", Fore.GREEN, "[*] Bitcoin Miner Threads Started")
    print(Fore.BLUE, '--------------~~( ', Fore.YELLOW, 'M M D R Z A . C o M', Fore.BLUE, ' )~~--------------')

    # Wait for all threads to finish
    for t in miner_threads:
        t.join()

if __name__ == '__main__':
    signal(SIGINT, handler)
    StartMining()
