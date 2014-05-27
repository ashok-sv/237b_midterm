__author__ = 'Sean Hamilton'
__author__ = 'Ashok Vydyanathan'

import sys
import select
import threading
import Queue

PROXIMITY = 1000
SPEED = 200
MAX_TRACKS = 200

radarQ = Queue.Queue()
running = True
updateCount = 0

def radarCallback():
    count = 0
    while(running):
        count = count + 1
        if count == 100000000:
            radarQ.put('Radar Update Received')
            count = 0

def updateATCS():
    if not radarQ.empty():
        print(radarQ.get())

    global updateCount
    updateCount += 1
    if updateCount == 5:
        updateCount = 0
        print('Display Tracks')

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
