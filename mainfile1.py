import cv2
import numpy as np
import time
from collections import deque



load_from_disk = True
if load_from_disk:
    penval = np.load('penval.npy')

cap = cv2.VideoCapture(0)
cap.set(3,471)
cap.set(4,636)


paintWindow = np.zeros((471,636,3)) + 255

bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

# These indexes will be used to mark the points in particular arrays of specific colour
blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0

#The kernel to be used for dilation purpose 
kernel = np.ones((5,5),np.uint8)

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0

# Here is code for Canvas setup
paintWindow = np.zeros((471,636,3)) + 255
paintWindow = cv2.rectangle(paintWindow, (40,1), (140,65), (0,0,0), 2)
paintWindow = cv2.rectangle(paintWindow, (160,1), (255,65), (255,0,0), 2)
paintWindow = cv2.rectangle(paintWindow, (275,1), (370,65), (0,255,0), 2)
paintWindow = cv2.rectangle(paintWindow, (390,1), (485,65), (0,0,255), 2)
paintWindow = cv2.rectangle(paintWindow, (505,1), (600,65), (0,255,255), 2)

cv2.putText(paintWindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)


# Load these 2 images and resize them to the same size.
pen_img = cv2.resize(cv2.imread('pen.png',1), (50, 50))
eraser_img = cv2.resize(cv2.imread('eraser.jpg',1), (50, 50))

kernel = np.ones((5,5),np.uint8)

# Making window size adjustable
cv2.namedWindow('image', cv2.WINDOW_NORMAL)

# This is the canvas on which we will draw upon
canvas = None

# Create a background subtractor Object
backgroundobject = cv2.createBackgroundSubtractorMOG2( detectShadows = False )

# This threshold determines the amount of disruption in background.
background_threshold = 600

# A variable which tells you if you're using a pen or an eraser.
switch = 'Pen'

# With this variable we will monitor the time between previous switch.
last_switch = time.time()

# Initilize x1,y1 points
x1,y1=0,0
flag = False

# Threshold for noise
noiseth = 800

# Threshold for wiper, the size of the contour must be bigger than this for us to clear the canvas
wiper_thresh = 40000
paintWindow = np.zeros((471,636,3)) + 255
# A varaible which tells when to clear canvas
clear = False

while(1):
    _, frame = cap.read()
    frame = cv2.flip(frame, 1 )
    
    # Initilize the canvas as a black image
    if canvas is None:
        canvas = np.zeros_like(frame)
        
    # Take the top left of the frame and apply the background subtractor there    
    top_left = frame[0: 50, 0: 50]
    fgmask = backgroundobject.apply(top_left)
    
    # Note the number of pixels that are white, this is the level of disruption.
    switch_thresh = np.sum(fgmask==255)
    
    # If the disruption is greater than background threshold and there has been some time after the previous switch then you 
    # can change the object type.
    if switch_thresh > background_threshold  and (time.time() - last_switch) > 1:
        
        # Save the time of the switch. 
        last_switch = time.time()
        
        if switch == 'Pen':
            switch = 'Eraser'
        else:
            switch = 'Pen'

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    



    frame = cv2.rectangle(frame, (160,1), (255,65), (255,0,0), 2)
    frame = cv2.rectangle(frame, (275,1), (370,65), (0,255,0), 2)
    frame = cv2.rectangle(frame, (390,1), (485,65), (0,0,255), 2)
    frame = cv2.rectangle(frame, (505,1), (600,65), (0,255,255), 2)
    cv2.putText(frame, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)


    # If you're reading from memory then load the upper and lower ranges from there
    if load_from_disk:
            lower_range = penval[0]
            upper_range = penval[1]
            
    # Otherwise define your own custom values for upper and lower range.
    else:             
       lower_range  = np.array([26,80,147])
       upper_range = np.array([81,255,255])
    
    mask = cv2.inRange(hsv, lower_range, upper_range)
    
    # Perform morphological operations to get rid of the noise
    mask = cv2.erode(mask,kernel,iterations = 1)
    mask = cv2.dilate(mask,kernel,iterations = 2)
    
    # Find Contours
    contours, hierarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    # Make sure there is a contour present and also its size is bigger than noise threshold.
    if contours and cv2.contourArea(max(contours, key = cv2.contourArea)) > noiseth:
                
        c = max(contours, key = cv2.contourArea)    
        x2,y2,w,h = cv2.boundingRect(c)
        
        # Get the area of the contour
        area = cv2.contourArea(c)
        
        # If there were no previous points then save the detected x2,y2 coordinates as x1,y1. 
        if x1 == 0 and y1 == 0 and flag == False:
            x1,y1= x2,y2
            flag = True       
           
        else:
            if switch == 'Eraser':
                cv2.circle(canvas, (x2, y2), 20, (0,0,0), -1)
                bpoints = [deque(maxlen=512)]
                gpoints = [deque(maxlen=512)]
                rpoints = [deque(maxlen=512)]
                ypoints = [deque(maxlen=512)]

                blue_index = 0
                green_index = 0
                red_index = 0
                yellow_index = 0

                paintWindow[67:,:,:] = 255
                
            else:
                if x1 == 0 and y1 == 0 and flag == True:
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]

                    blue_index = 0
                    green_index = 0
                    red_index = 0
                    yellow_index = 0
                    
                if y2 <= 65:
                    if 160 <= x2 <= 255:
                        colorIndex = 0 # Blue
                    elif 275 <= x2 <= 370:
                        colorIndex = 1 # Green
                    elif 390 <= x2 <= 485:
                        colorIndex = 2 # Red
                    elif 505 <= x2 <= 600:
                        colorIndex = 3 # Yellow
                else :
                    val = (x2,y2)
                    if colorIndex == 0:
                        bpoints[blue_index].appendleft(val)
                    elif colorIndex == 1:
                        gpoints[green_index].appendleft(val)
                    elif colorIndex == 2:
                        rpoints[red_index].appendleft(val)
                    elif colorIndex == 3:
                        ypoints[yellow_index].appendleft(val)

                points = [bpoints, gpoints, rpoints, ypoints]
                for i in range(len(points)):
                    for j in range(len(points[i])):
                        for k in range(1, len(points[i][j])):
                            if points[i][j][k - 1] is None or points[i][j][k] is None:
                                continue
                            
                            canvas = cv2.line(canvas, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                            cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

        
        # After the line is drawn the new points become the previous points.
        x1,y1= x2,y2
        
        # Now if the area is greater than the wiper threshold then set the clear variable to True
        if area > wiper_thresh:
           cv2.putText(canvas,'Clearing Canvas',(0,200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 1, cv2.LINE_AA)
           clear = True 

    else:
        # If there were no contours detected then make x1,y1 = 0
        x1,y1 =0,0
    
   
    # Now this piece of code is just for smooth drawing. (Optional)
    _,mask = cv2.threshold(cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY), 20, 255, cv2.THRESH_BINARY)
    foreground = cv2.bitwise_and(canvas, canvas, mask = mask)
    background = cv2.bitwise_and(frame, frame, mask = cv2.bitwise_not(mask))
    frame = cv2.add(foreground,background)

    
    # Switch the images depending upon what we're using, pen or eraser.
    if switch != 'Pen':
        cv2.circle(frame, (x1, y1), 20, (255,255,255), -1)
        frame[0: 50, 0: 50] = eraser_img
    else:
        frame[0: 50, 0: 50] = pen_img

    cv2.imwrite('paintWindow.png', paintWindow)
    cv2.imshow("Output", frame) 
    cv2.imshow("Paint", paintWindow)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
    
    # Clear the canvas after 1 second, if the clear variable is true
    if clear == True:
        
        time.sleep(1)
        canvas = None
        
        # And then set clear to false
        clear = False
        
cv2.destroyAllWindows()
cap.release()