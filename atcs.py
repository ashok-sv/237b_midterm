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

# this is the main simulation thread (?) 
def radarCallback():
    while running:
        newRadar = radarQ.get()
        print('Radar input received')
        newRadar = newRadar.strip('/r/n/t')
        XY = [int(s) for s in newRadar.split(' ') if s.isdigit()]
        if (len(newXY) != 2):
                print('Invalid radar data')
        else:
            corrTrack = {'Track':2001, 'X':XY[0], 'Y':XY[1]}
            for track in currentTracks:
                if correlateTrack(track, corrTrack):
                    print('Track ' + str(track['Track']) + ' updated from radar')
                    track['X'] = corrTrack['X']
                    track['Y'] = corrTrack['Y']
                    break

# main update function for all tracks
# either updates track by default (x,y+=200) or checks correlation with radar queue, if any
def updateATCS():
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
        print('Tracking ' + str(len(currentTracks)) + ' plane(s)')
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
            if track['X'] > 100000 or track['Y'] > 100000:
                currentTracks.remove(track)
                print('Track ' + str(track['Track']) + ' removed [out of range]')
                numTracks = numTracks - 1

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
            if (len(newXY) != 3 and len(newXY) != 2):
                print('Invalid entry')
            else:
                if len(newXY) == 3:
                    #print('New plane is at: ' + str(newXY[0]) + ',' + str(newXY[1]))
                    if (numTracks < MAX_TRACKS):
                        newTrack = {'Track':newXY[0], 'X':newXY[1], 'Y':newXY[2]}
                        currentTracks.append(newTrack)
                        numTracks += 1
                    else:
                        print('Track limit reached')
                else:
                    radarQ.put(str(newXY[0]) + ' ' + str(newXY[1]))


print('Exiting ATCS')
