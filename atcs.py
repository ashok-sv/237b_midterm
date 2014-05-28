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
currentTracks = []
numTracks = 0

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
    updateTracks()
    updateCount += 1
    if updateCount == 5:
        updateCount = 0
        #print('Display Tracks')
        displayTracks()

    renewTimer = threading.Timer(1.0, updateATCS)
    renewTimer.daemon = True
    renewTimer.start()

def displayTracks():
    if currentTracks:
        print('Tracking ' + str(len(currentTracks)) + ' planes')
        for track in currentTracks:
            print('Track: ' + str(track['Track']) + '  X: ' + str(track['X']) + '  Y: ' + str(track['Y']))
    else:
        print('No current tracks')

def correlateTrack(trackOne, trackTwo):
    diffX = trackOne['X'] - trackTwo['X']
    diffY = trackOne['Y'] - trackTwo['Y']
    dist = ((diffX ** 2) + (diffY ** 2)) ** (0.5)
    if (dist<=PROXIMITY):
        return True
    else:
        return False

def updateTracks():
    if currentTracks:
        print('Updating tracks')
        for track in currentTracks:
            track['X'] += SPEED
            track['Y'] += SPEED

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
        else:
            newPlane = s.strip('\t\n\r')
            newXY = [int(s) for s in newPlane.split(' ') if s.isdigit()]
            if (len(newXY) != 2):
                print('Invalid entry')
            else:
                #print('New plane is at: ' + str(newXY[0]) + ',' + str(newXY[1]))
                if (numTracks < MAX_TRACKS):
                    newTrack = {'Track':numTracks, 'X':newXY[0], 'Y':newXY[1]}
                    currentTracks.append(newTrack)
                    numTracks += 1
                else:
                    print('Track limit reached')


print('Exiting ATCS')
