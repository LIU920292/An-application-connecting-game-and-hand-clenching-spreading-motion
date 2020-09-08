import cv2
import numpy as np
import copy
import math
import time
import pyautogui
#from appscript import app

# Environment:
# OS    : Mac OS EL Capitan
# python: 3.7
# opencv: 2.4.13
set_clench_left = [-1] * 10
set_clench_right = [-1] * 10
test_number = 100
get_number = 0
count_sec = 0
event_1 = "no event"
start_flag = False
# clock = pygame.time.Clock()
left_clench, right_clench = False, False
action_output = "None"
def appending(left,datas):
    if -1 in left:
        count = 0
        while left[count] == -1:
            count += 1
            if count == len(left):
                break
        left[count - 1] = datas
    else:        

        left.pop(0)
        left.append(datas)

# def get_accuracy():
#     return str(get_number / (test_number) * 100 ) + "%" 

def reset():
    set_clench_left = [-1] * 10
    set_clench_right = [-1] * 10
    get_number = 0
    count_sec = 0

def call_data(data):
    a = str(data)
    return a
# parameters
cap_region_x_begin=0.8  # start point/total width
cap_region_y_end=0.2  # start point/total width
threshold = 60  #  BINARY threshold
blurValue = 41  # GaussianBlur parameter
bgSubThreshold = 50
learningRate = 0

right_boundaries = 850
left_boundaries = 400
start_height = 100
end_height = 500


# variables
isBgCaptured = 0   # bool, whether the background captured
triggerSwitch = False  # if true, keyborad simulator works

def printThreshold(thr):
    print("! Changed threshold to "+str(thr))


def removeBG(frame):
    fgmask = bgModel.apply(frame,learningRate=learningRate)
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # res = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res


def calculateFingers(res,drawing):  # -> finished bool, cnt: finger count
    #  convexity defect
    hull = cv2.convexHull(res, returnPoints=False)
    if len(hull) > 3:
        defects = cv2.convexityDefects(res, hull)
        if type(defects) != type(None):  # avoid crashing.   (BUG not found)

            cnt = 0
            for i in range(defects.shape[0]):  # calculate the angle
                s, e, f, d = defects[i][0]
                start = tuple(res[s][0])
                end = tuple(res[e][0])
                far = tuple(res[f][0])
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  # cosine theorem
                if angle <= math.pi / 2:  # angle less than 90 degree, treat as fingers
                    cnt += 1
                    cv2.circle(drawing, far, 8, [211, 84, 0], -1)
            return True, cnt
    return False, 0

def past(n):
    global action_output
    global left_clench
    global right_clench
    global set_clench_left
    global set_clench_right
    #rule settings
    left_top = set_clench_left[-n - 1]
    right_top = set_clench_right[-n - 1]

    #initial setting
    if left_top == -1:
        left_clench = False

    elif left_top >= 2:
        left_clench = False
    
    else:
        left_clench = True
    
    if right_top == -1:
        right_clench = False
    
    elif right_top >= 2:
        right_clench = False
    
    else:
        right_clench = True
    # #action output
    # if left_clench and right_clench:
    #     action_output = "clenching on both hands"

    # elif left_clench and not right_clench:
    #     action_output = "clenching left hand only"

    # elif not left_clench and right_clench:
    #     action_output = "clenching right hand only"
    
    return left_clench, right_clench

# Camera start
def basic():
    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(10,200)
    cv2.namedWindow('trackbar')
    cv2.createTrackbar('trh1', 'trackbar', threshold, 100, printThreshold)
    return camera
#read basic
def init(camera, activation_flag):
    setting = time.time()
    ret, frame = camera.read(())
    threshold = cv2.getTrackbarPos('trh1', 'trackbar')
    frame = cv2.bilateralFilter(frame, 5, 50, 100)  # smoothing filter
    frame = cv2.flip(frame, 1)  # flip the frame horizontally
    cv2.rectangle(frame, (right_boundaries, start_height),
                 (frame.shape[1], end_height), (255, 0, 0), 2)
    cv2.rectangle(frame, ( 0 , start_height),
                 (left_boundaries, end_height), (0, 255, 0), 2)
    set_clench_left_1 = "left finger number:" + str(set_clench_left[-1])
    set_clench_right_1 = "right finger number:" + str(set_clench_right[-1])
    additional_rule = "press b to capture, r to reset, esc to exit"
    cv2.putText(frame,set_clench_left_1,(500,600),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
    cv2.putText(frame,set_clench_right_1,(500,650),cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
    cv2.putText(frame,additional_rule,(500,700),cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
    if activation_flag:
        cv2.imshow('original', frame)
        cv2.moveWindow('original',100,0)

bgModel = None
isBgCaptured = 0
triggerSwitch = False

#ready for serve
def ready(camera, run):
    global bgModel, isBgCaptured, triggerSwitch
    #     # Keyboard OP
    k = cv2.waitKey(10)
    if k == 27:  # press ESC to exit
        camera.release()
        cv2.destroyAllWindows()
        run = False
    elif k == ord('b'):  # press 'b' to capture the background
        bgModel = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
        isBgCaptured = 1
        triggerSwitch = True
        print( '!!!Background Captured!!!')
        return bgModel, isBgCaptured, triggerSwitch, run
    elif k == ord('r'):  # press 'r' to reset the background
        bgModel = None
        triggerSwitch = False
        isBgCaptured = 0
        reset()
        return bgModel, isBgCaptured, triggerSwitch, run
    return bgModel, isBgCaptured, triggerSwitch, run

#for judging the rule
def start(camera, run, activation_flag):
    global event_1, start_flag
    ci_1, ci_2 = 0,0
    ret, frame = camera.read()
        #  Main operation
    s = ready(camera, run)
    bgModel = s[0]
    # print(s)
    if s[1] == 1:  # this part wont run until background captured
        activation_flag = False
        img = removeBG(frame)
        img_1 = img[start_height:end_height,
                    0:left_boundaries]  # clip the ROI-1
        img_2 = img[start_height:end_height,
                    right_boundaries:frame.shape[1]] #clip the ROI-2
        # cv2.imshow('mask1', img_1)
        # cv2.imshow('mask2', img_2)

        # convert the image into binary image
        gray_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2GRAY)
        gray_2 = cv2.cvtColor(img_2, cv2.COLOR_BGR2GRAY)
        blur_1 = cv2.GaussianBlur(gray_1, (blurValue, blurValue), 0)
        blur_2 = cv2.GaussianBlur(gray_2, (blurValue, blurValue), 0)
        # cv2.imshow('blur', blur)
        ret_1, thresh_1 = cv2.threshold(blur_1, threshold, 255, cv2.THRESH_BINARY)
        ret_2, thresh_2 = cv2.threshold(blur_2, threshold, 255, cv2.THRESH_BINARY)
        # cv2.imshow('ori_1', thresh_1)
        # cv2.imshow('ori_2', thresh_2)
        # cv2.moveWindow('ori_2', 100,200)
        # bg


        # get the coutours
        thresh1 = copy.deepcopy(thresh_1)
        contours_1, hierarchy_1 = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        thresh2 = copy.deepcopy(thresh_2)
        contours_2, hierarchy_2 = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        length_1 = len(contours_1)
        length_2 = len(contours_2)
        # print(length_1, length_2)
        maxArea = -1
        if length_1 > 0:
            for i in range(length_1):  # find the biggest contour (according to area)
                temp_1 = contours_1[i]
                area_1 = cv2.contourArea(temp_1)
                if area_1 > maxArea:
                    maxArea = area_1
                    ci_1 = i
            res_1 = contours_1[ci_1]
            hull_1 = cv2.convexHull(res_1)
            drawing_1 = np.zeros(img_1.shape, np.uint8)
            cv2.drawContours(drawing_1, [res_1], 0, (0, 255, 0), 2)
            cv2.drawContours(drawing_1, [hull_1], 0, (0, 0, 255), 3)
            isFinishCal_1,cnt_1 = calculateFingers(res_1,drawing_1)
            # print("hand on left:" ,cnt_1)
            if triggerSwitch is True:
                if isFinishCal_1 is True :
                    appending(set_clench_left, cnt_1)
                    cv2.namedWindow('output_1', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('output_1',300 ,300)
                    cv2.imshow('output_1', drawing_1) #left
                    cv2.moveWindow("output_1", 1000,0)
        if length_2 > 0:
            for i in range(length_2):
                temp_2 = contours_2[i]
                area_2 = cv2.contourArea(temp_2)
                if area_2 > maxArea:
                    maxArea = area_2
                    ci_2 = i

            res_2 = contours_2[ci_2]
            hull_2 = cv2.convexHull(res_2)
            drawing_2 = np.zeros(img_2.shape, np.uint8)

            cv2.drawContours(drawing_2, [res_2], 0, (0, 255, 0), 2)
            cv2.drawContours(drawing_2, [hull_2], 0, (0, 0, 255), 3)


            isFinishCal_2,cnt_2 = calculateFingers(res_2,drawing_2)
            # print("hand on right:", cnt_2)
            if triggerSwitch is True:
                if isFinishCal_2 is True: 
                    appending(set_clench_right, cnt_2)
                    cv2.namedWindow('output_2', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('output_2', 300,300)
                    cv2.imshow('output_2', drawing_2) #right
                    cv2.moveWindow("output_2", 0,0)



            # print("time:" , get_number)
            # print(set_clench_left, set_clench_right)
                #show output to check the output of the array


            # my_img_1 = np.zeros((256, 1280, 1), dtype = "uint8")
            # left_data = "left data: "+ call_data(set_clench_left) 
            # right_data = "right data: " + call_data(set_clench_right)
            # length1 = "existing coutours left:" + str(length_1)
            # length2 = "existing coutours right:" + str(length_2)
            # cv2.putText(my_img_1,left_data,(60,60),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            # cv2.putText(my_img_1,right_data,(60,100),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            # cv2.putText(my_img_1,length1,(60,140),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            # cv2.putText(my_img_1,length2,(60,180),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            if length_1 >= 6 and length_2 >= 6:
                activation_flag = True
                cv2.destroyWindow('output_1')
                cv2.destroyWindow('output_2')
                
      
            previous_left, previous_right = past(1)
            #force to push back
            left_clench, right_clench = past(0)
            # cv2.putText(my_img_1,"motion:",(30,210),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            if not (-1 in set_clench_left) and not (-1 in set_clench_right):
                # pyautogui.FAILSAFE = False
                if left_clench and not previous_left:
                    #press
                    # pyautogui.keyDown("space")
                    # pyautogui.keyUp("space")

   
                    # print("1")
                    pyautogui.click(100, 100)
                    pyautogui.keyDown("1")
                    pyautogui.keyUp("1")
                    event_1 = "clench right"
                    times = time.time()
                    # print("passed:",round(times - setting, 2))
                    # cv2.putText(my_img_1,"press left",(120,210),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
                
                elif right_clench and not previous_right:
                    #press
                    # print("0")
                    pyautogui.click(100, 100)
                    pyautogui.keyDown("0")
                    pyautogui.keyUp("0")
                    # see = time.time()
                    # while time.time() - see < 1.5:
                    #     pyautogui.keyDown("s")
                    # pyautogui.keyUp("s")
                    event_1 = "clench left"
                    # times = time.time()
                    # print("passed:",round(times - setting, 2))
      
                  # cv2.putText(my_img_1,"press right",(120,210),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
                else:

                    event_1 = "no event"
            else:
                event_1 = "no event"


            # cv2.putText(my_img_1,"time passed:" + str(round(times - setting, 2)),(300,210),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
            # cv2.imshow('Single Channel Window', my_img_1)  
            # cv2.moveWindow('Single Channel Window', 0, 0)          
            # print(ci_1, ci_2)
    else:
        activation_flag = True       
    run = s[3]
    if triggerSwitch:
        start_flag = True
    return activation_flag, run, set_clench_left, set_clench_right, event_1, start_flag

camera = basic()
run = True
activate = True

# while run:

#     init(camera, activate)
#     setting, run, set_clench_left ,set_clench_right, event, starting = start(camera, run, activate)
#     if not run:
#         break
#     if activate == False and setting == True:
#         bgModel = None
#         isBgCaptured = 0
#         triggerSwitch = False
#         cv2.destroyWindow('output_1')
#         cv2.destroyWindow('output_2')
#     elif activate == True and setting == False:
#         cv2.destroyWindow("original")
#     if event != "no event":
#         print(event)
#     activate = setting
#     # print(activate)




