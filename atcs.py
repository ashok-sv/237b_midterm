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
    count = 0
    while(running):
        count = count + 1
	# roughly 4 seconds on ieng6
        if count == 100000000:
            radarQ.put('4000 4500')
            count = 0

# main update function for all tracks
# either updates track by default (x,y+=200) or checks correlation with radar queue, if any
def updateATCS():
    while (not radarQ.empty()):
        #print(radarQ.get())
	print("Radar input received")
        newPlane = radarQ.get()
        newPlane = newPlane.strip('/r/n/t')
        newXY = [int(s) for s in newPlane.split(' ') if s.isdigit()]
        if (len(newXY) != 2):
                print('Invalid radar data')
        else:
            corrTrack = {'Track':2001, 'X':newXY[0], 'Y':newXY[1]}
            for track in currentTracks:
                if (correlateTrack(track, corrTrack)):
                    track['X'] = corrTrack['X']
                    track['Y'] = corrTrack['Y']
                    break

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
            if (len(newXY) != 3):
                print('Invalid entry')
            else:
                #print('New plane is at: ' + str(newXY[0]) + ',' + str(newXY[1]))
                if (numTracks < MAX_TRACKS):
                    newTrack = {'Track':newXY[0], 'X':newXY[1], 'Y':newXY[2]}
                    currentTracks.append(newTrack)
                    numTracks += 1
                else:
                    print('Track limit reached')


print('Exiting ATCS')
