import cv2
from win32api import GetSystemMetrics
import time
import os
import math
from tkinter import filedialog, messagebox
from cvzone.HandTrackingModule import HandDetector

filepath = filedialog.askopenfilename(initialdir=os.getcwd(), title='Browse Image File', filetypes=(('JPEG Image File', '*.jpg'),('PNG Image File','*.png')))
if not filepath.endswith('.jpg') or filepath.endswith('.jpeg'):
    messagebox.showerror('Error Occured','The image type is not supported.\nWe only support .jpg and .jpeg files.')
    quit()

imagefile = cv2.imread(filepath)
image_aspect_ratio = (imagefile.shape[1]/imagefile.shape[0])
w = imagefile.shape[1]
h = imagefile.shape[0]
if w > h:
    w = 400
    h = int((1/image_aspect_ratio) * w)
elif w < h:
    h = 400
    w = int(image_aspect_ratio * h)
else:
    w = 400
    h = 400
finalimage = cv2.resize(imagefile, (w,h), cv2.INTER_AREA)
trueimage = finalimage

def isDark(image):
    blur = cv2.blur(image, (5, 5))
    if cv2.mean(blur) > (127,127,127):  # The range for a pixel's value in grayscale is (0-255), 127 lies midway
        return False # (127 - 255) denotes light image
    else:
        return True # (0 - 127) denotes dark image

window_name = '2D Graphics Manipulation Software'
camera_width = GetSystemMetrics(0)
camera_height = GetSystemMetrics(1)

willQuit = False
quitCounter = 10

distance_hands = None

capture = cv2.VideoCapture(0)
capture.set(3, camera_width)
capture.set(4, camera_height)
pTime = 0

success, tempcam = capture.read()
image_x = int((tempcam.shape[1]-finalimage.shape[1])/2)
image_y = int((tempcam.shape[0]-finalimage.shape[0])/2)
image_width = finalimage.shape[1]
image_height = finalimage.shape[0]

detector = HandDetector(detectionCon=0.8)

messagebox.showinfo('Before we start!','''Before Proceeding, please read the following instructions:

> To exit the program, make sure your index finger is positioned at the close button on the top right side of the screen. (Make sure only one hand is being detected, and you need not be necessarily pointing your index finger)

> To move a picture around, open only your index finger and/or your middle finger. (Make sure only one hand is being detected)

> To zoom in or zoom out of a picture, use both of your hands' index finger and/or your middle finger. The farther the position of the two index finger tips are, the bigger the image.

That's it, have fun!
''')

while True:
    # Capture webcam and mirror it
    success, src = capture.read()
    img = cv2.flip(src, 1)
    img_shape = img.shape

    # Detect hands
    hands, img = detector.findHands(img)
    if len(hands) == 1:
        distance_hands = None
        # Single handed functions
        for i in range(len(hands)):
            lmList = hands[i]["lmList"]
            #print('Index finger X:' + str(lmList[8][0]) + '  Y: ' + str(lmList[8][1]))
            if (lmList[8][0] >= img_shape[1]-70) and (lmList[8][1] <= 70):
                willQuit = True
                quitCounter -= 1
                if quitCounter == 0:
                    cv2.destroyAllWindows()
                    quit()
            else:
                willQuit = False
                quitCounter = 10
        if detector.fingersUp(hands[0]) == [0,1,0,0,0] or detector.fingersUp(hands[0]) == [0,1,1,0,0]:
            lmList = hands[0]['lmList']
            x = lmList[8][0]
            y = lmList[8][1]
            if (x >= (image_width/2)) or (x <= img_shape[1]-(image_width/2)) or (y >= (image_height/2)) or (y <= img_shape[0]-(image_height/2)):
                image_x = int(x-(image_width/2))
                if image_x < 0:
                    image_x = 0
                elif image_x > img_shape[1]-image_width:
                    image_x = img_shape[1]-image_width
                image_y = int(y-(image_height/2))
                if image_y < 0:
                    image_y = 0
                elif image_y > img_shape[0]-image_height:
                    image_y = img_shape[0]-image_height
        if willQuit:
            image_x = int((img_shape[1]-image_width)/2)
            image_y = int((img_shape[0]-image_height)/2)
    elif len(hands) == 2:
        #Double handed functions
        if (detector.fingersUp(hands[0]) == [0,1,0,0,0] or detector.fingersUp(hands[0]) == [0,1,1,0,0]) and (detector.fingersUp(hands[1]) == [0,1,0,0,0] or detector.fingersUp(hands[1]) == [0,1,1,0,0]):
            image_x = int((img_shape[1]-image_width)/2)
            image_y = int((img_shape[0]-image_height)/2)
            lmList1 = hands[0]['lmList']
            lmList2 = hands[1]['lmList']
            x1 = lmList1[8][0]
            x2 = lmList2[8][0]
            y1 = lmList1[8][1]
            y2 = lmList2[8][1]
            if distance_hands == None:
                distance_hands = math.sqrt(math.pow(abs(x2-x1),2)+math.pow(abs(y2-y1),2))
            else:
                prev_distance_hands = distance_hands
                distance_hands = abs(math.sqrt(math.pow(abs(x2-x1),2)+math.pow(abs(y2-y1),2)))
                diff = int((distance_hands - prev_distance_hands)/2.5)
                image_height += diff
                image_width += image_aspect_ratio * diff                
                if image_width > img_shape[1]:
                    image_width = img_shape[1]
                    image_height = int((1/image_aspect_ratio)*image_width)
                elif image_width < 50:
                    image_width = 50
                    image_height = int((1/image_aspect_ratio)*image_width)
                elif image_height > img_shape[0]:
                    image_height = img_shape[0]
                    image_width = int(image_aspect_ratio*image_height)
                elif image_height < 100:
                    image_height = 100
                    image_width =  int(image_aspect_ratio*image_height)
                image_x = (img_shape[1]-int(image_width))/2
                image_y = (img_shape[0]-int(image_height))/2
                finalimage = cv2.resize(imagefile, (int(image_width), int(image_height)), interpolation=cv2.INTER_AREA)
        else:
            distance_hands = None

    # Window Properties
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    # Calculate FPS
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    # Show elements on screen
    fpscolor = None
    titlecolor = None

    if isDark(img[0:100,0:100]):
        fpscolor = (255,255,255)
    else:
        fpscolor = (0,0,0)
    
    if isDark(img[img_shape[0]-50:img_shape[0],0:400]):
        titlecolor = (255,255,255)
    else:
        titlecolor = (0,0,0)
    cv2.putText(img, f'{int(fps)} FPS', (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, fpscolor, 3)
    cv2.putText(img, '2D Augmented Graphics Manipulation Software', (10,img_shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, titlecolor, 3)

    #Format image and show it
    try:
        exit_button = cv2.imread('images/exit-button-image.png')
        img[int(image_y):int(image_y)+int(image_height),int(image_x):int(image_x)+int(image_width)] = finalimage
        img[10:60, img_shape[1]-60:img_shape[1]-10] = exit_button
    except:
        pass
    cv2.imshow(window_name, img)
    cv2.waitKey(1)