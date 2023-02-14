# Python program for capturing and detecting the brightest spot on a picture
import cv2
import numpy as np
import cropsquare
import serial

serialPort = serial.Serial("/dev/cu.usbmodem101", 9600)
serialPort.open
 
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 10)

box_bound_offset = 50 # number of pixels away from the center that is acceptable for the bounding box
    
box_bound_upper = 500 + box_bound_offset # 500, 500 is the center of the screen
box_bound_lower = 500 - box_bound_offset

#ARDUINO STUFF
iterations = 0 # helps with lag management

# This drives the program into an infinite loop.
while(1):
#TEST STUFF FOR ARDUINO

# Captures the live stream frame-by-frame
    _, frame = cap.read()
    ret, background = cap.read()
    background = cv2.flip(background, 1)

# Converts images from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# color is stored in hue saturation and value, leaving this comment because i forgot that.
    lower_white = np.array([0,0,255])
    upper_white= np.array([255,125,255])

#creates a mask based off of the hsv values
    mask = cv2.inRange(hsv, lower_white, upper_white)
    mask = cv2.flip(mask,1)

#we only need the mask and background to be shown for now in 1000x1000 pixel squares
    background = cropsquare.crop_square(background, 1000)
    cv2.imshow('background' ,background)
    mask = cropsquare.crop_square(mask, 1000)
    cv2.imshow('mask',mask)

#thresh the mask to binary
    ret,thresh = cv2.threshold(mask,127,255,0)
    blurred_thresh = cv2.GaussianBlur(thresh, (25, 25), 0)
    
    contours, hierarchy = cv2.findContours(blurred_thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    Multiple_Avg_Sum_x = 0 #sum of the center of all countours on the x axis
    Multiple_Avg_Sum_y = 0 #sum of the center of all countours on the y axis
    weight_by_area = 0 #sum of the area of all counters
    avg_x = 0 #the avg of all light emitting pixels on the x axis
    avg_y = 0 #the avg of all light emitting pixels on the y axis
    singular_avgx = 0 #avg of a indivual contour
    singular_avgy = 0 

    Contours_amount = 0
    Singular_Sum_x = 0
    Singular_Sum_y = 0
    
    
    for c in contours:
# calculate moments for each contour
        M = cv2.moments(c)

        if(M["m00"] != 0):
#does math to find the center of each countour
            xone = round(M['m10'] / M['m00'])
            yone = round(M['m01'] / M['m00'])
            
#finds the area of each counter
            area = cv2.contourArea(c)

#this is to display the cneter of each indivual contour
        Singular_Sum_x = xone
        Singular_Sum_y = yone
    
        Contours_amount += 1
        singular_avgx = round(Singular_Sum_x)
        singular_avgy = round(Singular_Sum_y)
        cv2.circle(background, (singular_avgx, singular_avgy), 10, (150, 150, 0), -1)


#Displays the average center of all countours
        Multiple_Avg_Sum_x += (xone * area)
        Multiple_Avg_Sum_y += (yone * area)
        weight_by_area += area

#uses the total sum of the center of each contour divided by the total area of each countour to find the center
    if(weight_by_area != 0):
        avg_x = round(Multiple_Avg_Sum_x/weight_by_area)
        avg_y = round(Multiple_Avg_Sum_y/weight_by_area)

# Draw a circle based centered at total average coordinates
    cv2.circle(background, (avg_x, avg_y), 10, (125, 0, 125), -1)

#check if the avg point is within the bounding box and change the color of the box accordingly
    if(box_bound_lower < avg_x < box_bound_upper and box_bound_lower < avg_y < box_bound_upper):
        cv2.rectangle(background, (box_bound_lower,box_bound_lower), (box_bound_upper,box_bound_upper), (0, 255, 0), 2)
    else:
        cv2.rectangle(background, (box_bound_lower,box_bound_lower), (box_bound_upper,box_bound_upper), (0, 0, 255), 2)

#check if the avg_y is above or below the bounding box (lower is higher up as 0,0 is the top left corner)
        
        if(avg_y > box_bound_upper):
            cv2.arrowedLine(background, (500, box_bound_upper), (500, avg_y), (0, 0, 255), 2)
        else: 
            if(avg_y < box_bound_lower):
                cv2.arrowedLine(background, (500, box_bound_lower), (500, avg_y), (0, 0, 255), 2)
        

#same as above but for the avg_x
        if(avg_x > box_bound_upper):
            cv2.arrowedLine(background, (box_bound_upper, 500), (avg_x, 500), (0, 0, 255), 2)
        else: 
            if(avg_x < box_bound_lower):
                cv2.arrowedLine(background, (box_bound_lower, 500), (avg_x, 500), (0, 0, 255), 2)
# prints the vars
    print("avg X: " + str(avg_x), "avg Y: " + str(avg_y), "Amount of Light sources " + str(Contours_amount))
    
# display the image
    cv2.imshow("final", background)


# more arduino stuff
    iterations += 1 #every 10 iterations (roughly .5 seconds, run the code)

    if(iterations == 5):
        avg_y_string = "<"
        avg_y_string += str(avg_y)
        avg_y_string += ">"
        serialPort.write((avg_y_string).encode())
        print("string sent succesfully")
        iterations = 0
    

#break key
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

# Destroys all of the HighGUI windows.
cv2.destroyAllWindows()

# release the captured frame
cap.release()
