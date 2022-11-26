from flask import Flask,render_template,request,redirect,url_for
import cv2
import subprocess
smoothening = 5
import numpy as np
import handtracking as htm
import time
import autopy
import cv2
import mouse
import threading
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard
import screen_brightness_control as sbc

app = Flask(__name__)

@app.route('/home',methods=['POST'])
def func():
        print("here")
        print(request.form['subject'])
        if request.form['subject'] == 'fav_HTML':
            wCam, hCam = 640, 480
            frameR = 100

            pTime = 0
            plocX, plocY = 0, 0
            clocX, clocY = 0, 0

            cap = cv2.VideoCapture(0)
            cap.set(3, 640)
            cap.set(4, 480)

            detector = htm.handDetector(maxHands=1)
            wSrc, hSrc = autopy.screen.size()

            while True:
                # 1. Find hand landmarks
                success, img = cap.read()
                img = detector.findHands(img)
                lmList, bbox = detector.findPosition(img)

                if len(lmList) != 0:
                    x1, y1 = lmList[8][1:]
                    x2, y2 = lmList[12][1:]

                    # print(x1, y1, x2, y2)

                    # 2. Get tip of the index and middle finger
                    # 3. Chaeck which fingers are up
                    fingers = detector.fingersUp()
                    # print(fingers)
                    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
                    # 4. Only Inder fingers : Moving mode
                    if fingers[1] == 1 and fingers[2] == 0:
                        # 5. convert coordinates
                        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wSrc))
                        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hSrc))
                        # 6. Smoothen Values
                        clocX = plocX + (x3 - plocX) / smoothening
                        clocY = plocY + (y3 - plocY) / smoothening

                        # 7. Move Mouse
                        autopy.mouse.move(wSrc - clocX, clocY)
                        cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
                        plocX, plocY = clocX, clocY

                    # 8. Both index and middle fingers are up : clicking mode
                    if fingers[1] == 1 and fingers[2] == 1:
                        # 9. find distance between fingers
                        length, img, lineInfo = detector.findDistance(8, 12, img)
                        print(length)
                        # 10. Click mouse if distance are short
                        if length < 40:
                            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                            autopy.mouse.click()

                # 11. Frame rate
                cTime = time.time()
                fps = 1 / (cTime - pTime)
                pTime = cTime
                cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
                # 12. Display
                cv2.imshow("Image", img)

                cv2.waitKey(1)
          # used try so that if user pressed other than the given key error will not be shown
                if keyboard.is_pressed('q'):  # if key 'q' is pressed
                            keyboard.release('q')

                            print('You Pressed A Key!')
                            break  # finishing the loop
            cap.release()
            cv2.destroyAllWindows()
            return redirect('/')

                        #volume_started
        if request.form['subject'] == 'fav_CSS':

            cap = cv2.VideoCapture(0)

            mpHands = mp.solutions.hands
            hands = mpHands.Hands()
            mpDraw = mp.solutions.drawing_utils

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volbar = 400
            volper = 0

            volMin, volMax = volume.GetVolumeRange()[:2]

            while True:
                success, img = cap.read()
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                results = hands.process(imgRGB)

                lmList = []
                if results.multi_hand_landmarks:
                    for handlandmark in results.multi_hand_landmarks:
                        for id, lm in enumerate(handlandmark.landmark):
                            h, w, _ = img.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            lmList.append([id, cx, cy])  # adding to the empty list 'lmList'
                        mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

                if lmList != []:
                    # getting the value at a point
                    # x      #y
                    x1, y1 = lmList[4][1], lmList[4][2]  # thumb
                    x2, y2 = lmList[8][1], lmList[8][2]  # index finger
                    # creating circle at the tips of thumb and index finger
                    cv2.circle(img, (x1, y1), 13, (255, 0, 0), cv2.FILLED)  # image #fingers #radius #rgb
                    cv2.circle(img, (x2, y2), 13, (255, 0, 0), cv2.FILLED)  # image #fingers #radius #rgb
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0),
                             3)  # create a line b/w tips of index finger and thumb

                    length = hypot(x2 - x1, y2 - y1)  # distance b/w tips using hypotenuse
                    # from numpy we find our length,by converting hand range in terms of volume range ie b/w -63.5 to 0
                    vol = np.interp(length, [30, 250], [volMin, volMax])
                    volbar = np.interp(length, [30, 250], [400, 150])
                    volper = np.interp(length, [30, 250], [0, 100])

                    print(vol, int(length))
                    volume.SetMasterVolumeLevel(vol, None)

                    # Hand range 30 - 350
                    # Volume range -63.5 - 0.0
                    # creating volume bar for volume level
                    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255),
                                  4)  # vid ,initial position ,ending position ,rgb ,thickness
                    cv2.rectangle(img, (50, int(volbar)), (85, 400), (0, 0, 255), cv2.FILLED)
                    cv2.putText(img, f"{int(volper)}%", (10, 40), cv2.FONT_ITALIC, 1, (0, 255, 98), 3)
                    # tell the volume percentage ,location,font of text,length,rgb color,thickness
                cv2.imshow('Image', img)
                cv2.waitKey(1)
                if keyboard.is_pressed('q'):  # if key 'q' is pressed
                    keyboard.release('q')

                    print('You Pressed A Key!')
                    break  # finishing the loop
            cap.release()
            cv2.destroyAllWindows()
            return redirect('/')




        # GESTUREBRIGHTNESS
        if request.form['subject'] == 'fav_SQL':
            cap = cv2.VideoCapture(0)

            mpHands = mp.solutions.hands
            hands = mpHands.Hands()
            mpDraw = mp.solutions.drawing_utils

            while True:
                success, img = cap.read()
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(imgRGB)

                lmList = []
                if results.multi_hand_landmarks:
                    for handlandmark in results.multi_hand_landmarks:
                        for id, lm in enumerate(handlandmark.landmark):
                            h, w, _ = img.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            lmList.append([id, cx, cy])
                        mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

                if lmList != []:
                    x1, y1 = lmList[4][1], lmList[4][2]
                    x2, y2 = lmList[8][1], lmList[8][2]

                    cv2.circle(img, (x1, y1), 4, (255, 0, 0), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 4, (255, 0, 0), cv2.FILLED)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

                    length = hypot(x2 - x1, y2 - y1)

                    bright = np.interp(length, [15, 220], [0, 100])
                    print(bright, length)
                    sbc.set_brightness(int(bright))

                    # Hand range 15 - 220
                    # Brightness range 0 - 100

                cv2.imshow('Image', img)
                cv2.waitKey(1)
                if keyboard.is_pressed('q'):  # if key 'q' is pressed
                    keyboard.release('q')

                    print('You Pressed A Key!')
                    break  # finishing the loop
            cap.release()
            cv2.destroyAllWindows()
            return redirect('/')

        if request.form['subject'] == 'fav_boot':


            wcam, hcam = 640, 480
            frameR = 100
            smoothening = 7

            pTime = 0
            plocX, plocY = 0, 0
            clocX, clocY = 0, 0
            cap = cv2.VideoCapture(0)
            cap.set(3, wcam)
            cap.set(4, hcam)
            detector = htm.handDetector(maxHands=1)
            wScr, hScr = autopy.screen.size()
            # print(wScr,hScr)

            while True:
                success, img = cap.read()
                img = detector.findHands(img)
                lmList, bbox = detector.findPosition(img)

                if len(lmList) != 0:
                    x1, y1 = lmList[8][1:]
                    x2, y2 = lmList[12][1:]
                    # print(x1,y1,x2,y2)

                    fingers = detector.fingersUp()
                    # print(fingers)
                    cv2.rectangle(img, (frameR, frameR), (wcam - frameR, hcam - frameR), (255, 0, 255), 2)

                    if fingers[1] == 1 and fingers[2] == 0:
                        # fingers[0]==1

                        x3 = np.interp(x1, (frameR, wcam - frameR), (0, wScr))
                        y3 = np.interp(y1, (frameR, hcam - frameR), (0, hScr))

                        clocX = plocX + (x3 - plocX) / smoothening
                        clocY = plocY + (y3 - plocY) / smoothening

                        autopy.mouse.move(wScr - clocX, clocY)
                        cv2.circle(img, (x1, y1), 13, (255, 250, 0), cv2.FILLED)  # Pink color
                        plocX, plocY = clocX, clocY

                    if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:
                        length, img, lineInfo = detector.findDistance(8, 12, img)
                        # print(length)
                        if length < 50:
                            # Left Click
                            if fingers[4] == 0:
                                cv2.circle(img, (lineInfo[4], lineInfo[5]), 13, (0, 255, 0), cv2.FILLED)  # Green color
                                mouse.click(button="left")
                            # autopy.mouse.click()

                            # Right Click
                            if fingers[4] == 1:
                                cv2.circle(img, (lineInfo[4], lineInfo[5]), 13, (0, 0, 0), cv2.FILLED)  # Black Color
                                mouse.click(button="right")

                    ##Scroll Up and Down
                    if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0:
                        length, img, lineInfo = detector.findDistance(8, 12, img)
                        if length < 50:
                            if fingers[4] == 0:
                                mouse.wheel(delta=-1)
                                cv2.circle(img, (lineInfo[4], lineInfo[5]), 13, (255, 0, 0), cv2.FILLED)  # Yellow color

                            if fingers[4] == 1:
                                mouse.wheel(delta=1)
                                cv2.circle(img, (lineInfo[4], lineInfo[5]), 13, (0, 0, 128), cv2.FILLED)  # Blue color

                    # if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 1:
                    #     if length < 50:
                    #         mouse.wheel(delta=1)

                cTime = time.time()
                fps = 1 / (cTime - pTime)
                pTime = cTime
                cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

                cv2.imshow("Image", img)
                cv2.waitKey(1)


@app.route('/',methods=['GET'])
def high():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug = True , use_reloader = True)