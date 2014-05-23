__author__ = 'Sean Hamilton'
__author__ = 'Ashok Vydyanathan'

import sys
import select
import threading
import queue

radarQ = queue.Queue()
running = True

def radarCallback():
    count = 0
    while(running):
        count = count + 1
        if count == 100000000:
            radarQ.put('Radar Update Recieved')
            count = 0

def updateATCS():
    print('ATCS Updated')
    if not radarQ.empty():
        print(radarQ.get())
    renewTimer = threading.Timer(1.0, updateATCS)
    renewTimer.daemon = True
    renewTimer.start()

# setup and start radar thread
radarThread = threading.Thread(target=radarCallback)
radarThread.daemon = True
radarThread.start()

# setup and start first update timer
updateTimer = threading.Timer(1.0, updateATCS)
updateTimer.daemon = True
updateTimer.start()

while running:
    i, o, e = select.select([sys.stdin], [], [])
    if i:
        s = sys.stdin.readline()
        if s == 'q\n':
            running = False


print('Exiting ATCS')