# Imports
import cv2
import time
import numpy as np

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm

# Main
if __name__ == '__main__':

    ##########################################
    wCam, hCam = 640, 480
    ##########################################

    pTime = 0

    capture = cv2.VideoCapture(0)
    capture.set(3, wCam)
    capture.set(4, hCam)

    window_name = "camera"
    cv2.namedWindow(window_name)

    detector = htm.handDetector()

    buttonPressed = False

    newVolume = 0

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    volumeRange = volume.GetVolumeRange()

    while cv2.waitKey(1) == -1:
        success, frame = capture.read()

        frame = detector.findHands(frame)
        lmList, rect = detector.findPosition(frame, draw=False)

        if len(lmList) != 0:
            tFing = np.array([lmList[4][1], lmList[4][2]])
            iFing = np.array([lmList[8][1], lmList[8][2]])
            mFing = np.array([lmList[12][1], lmList[12][2]])
            tbFing = np.array([lmList[2][1], lmList[2][2]])

            volumeDist = np.linalg.norm(iFing - tFing)
            activationDist = np.linalg.norm(mFing - tbFing)

            if activationDist < 30 and not buttonPressed:
                buttonPressed = True
            elif activationDist > 30 and buttonPressed:
                buttonPressed = False

            if buttonPressed:
                vol = np.interp(volumeDist, [20, 150], [volumeRange[0], volumeRange[1]])
                volume.SetMasterVolumeLevel(vol, None)

                print(vol)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(frame, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        cv2.imshow(window_name, frame)
