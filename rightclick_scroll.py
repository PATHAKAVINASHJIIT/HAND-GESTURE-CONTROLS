import cv2
import numpy as np
import handtracking as htm
import time
import autopy
import mouse
import threading

wcam,hcam=640,480
frameR=100
smoothening=7

pTime=0
plocX,plocY= 0,0
clocX,clocY= 0,0
cap= cv2.VideoCapture(0)
cap.set(3,wcam)
cap.set(4,hcam)
detector= htm.handDetector(maxHands=1)
wScr, hScr= autopy.screen.size()
# print(wScr,hScr)

while True:
    success, img = cap.read()
    img= detector.findHands(img)
    lmList, bbox= detector.findPosition(img)


    if len(lmList)!=0:
        x1, y1= lmList[8][1:]
        x2, y2= lmList[12][1:]
        # print(x1,y1,x2,y2)

        fingers= detector.fingersUp()
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wcam - frameR, hcam - frameR), (255, 0, 255), 2)

        if fingers[1]==1 and fingers[2]==0 :
            #fingers[0]==1

            x3=np.interp(x1,(frameR,wcam-frameR),(0,wScr))
            y3=np.interp(y1,(frameR,hcam-frameR),(0,hScr))

            clocX= plocX+ (x3-plocX)/ smoothening
            clocY= plocY+ (y3-plocY)/ smoothening

            autopy.mouse.move(wScr-clocX,clocY)
            cv2.circle(img,(x1,y1), 13, (255,250,0),cv2.FILLED) #Pink color
            plocX,plocY= clocX,clocY

        if fingers[1] == 1 and fingers[2] == 1 and fingers[0]==1:
            length, img, lineInfo= detector.findDistance(8, 12, img)
            # print(length)
            if length<50:
                #Left Click
                if fingers[4]==0 :
                    cv2.circle(img, (lineInfo[4],lineInfo[5]), 13, (0,255,0), cv2.FILLED)#Green color
                    mouse.click(button="left")
                # autopy.mouse.click()

                #Right Click
                if fingers[4]==1 :
                    cv2.circle(img, (lineInfo[4],lineInfo[5]), 13, (0,0,0), cv2.FILLED)#Black Color
                    mouse.click(button="right")




        ##Scroll Up and Down
        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 :
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 50:
                if fingers[4]==0:
                    mouse.wheel(delta=-1)
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 13, (255,0,0), cv2.FILLED)#Yellow color

                if fingers[4]==1:
                    mouse.wheel(delta=1)
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 13, (0,0,128), cv2.FILLED)#Blue color


        # if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 1:
        #     if length < 50:
        #         mouse.wheel(delta=1)



    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime
    cv2.putText(img,str(int(fps)),(20,50),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)

    cv2.imshow("Image",img)
    cv2.waitKey(1)
