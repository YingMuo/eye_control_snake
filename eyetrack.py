import cv2
import dlib
import numpy as np
import queue
import collections

def get_point_68(face):
	coords = np.zeros((68, 2), dtype=np.int64)
	for i in range(0, 68):
		coords[i] = [face.part(i).x, face.part(i).y]
	return coords

def eye_rect(points):
    x, y = [e[0] for e in points], [e[1] for e in points]
    bias = 5
    xmin, ymin = min(x) -bias, min(y) -bias
    xmax, ymax = max(x) +bias, max(y) +bias
    return [(xmin, ymin), [xmax, ymax]]

def contouring(thresh, points, frame):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        radius = 4
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00']) + points[0][0]
        cy = int(M['m01']/M['m00']) + points[0][1]
        cv2.circle(frame, (cx, cy), radius, (0, 0, 255), -1)
        return cx, cy, True
    except:
        return 0,0,False

# 沒動0 上1 右2 下3 左4
def judge_dir(curPos, mainPos):
    xyScale, eyeThresh = 1.5, 8
    difx, dify = curPos - mainPos
    absx, absy = abs(difx * xyScale), abs(dify)
    if absx > eyeThresh or absy > eyeThresh:
        if absx > absy:
            if difx < 0: return 4
            else: return 2
        else:
            if dify < 0: return 1
            else: return 3
    return 0

def combine_eyes(ldir, rdir):
    if ldir == rdir: return ldir
    elif ldir == 0:  return rdir
    elif rdir == 0:  return ldir
    return 0

def judge_slideWin(slidingWindow):
    c = collections.Counter(slidingWindow)
    mc = c.most_common()[0]
    if mc[1] > 3: return mc[0]
    else: return 0

def get_dir(dir):
    if dir == 1: return 'up'
    elif dir == 2: return 'right'
    elif dir == 3: return 'down'
    elif dir == 4: return 'left'
    return

# filepath = './video/center_focus.mp4'
# filepath = './video/center_left_center.mp4'
# filepath = './video/asiagodtone.mp4'

vc = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./src/shape_predictor_68_face_landmarks.dat')
left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

kernel = np.ones((9, 9), np.uint8)
lPosList, rPosList = np.empty((0,2), np.int64), np.empty((0,2), np.int64)
lscanned, rscanned = False, False
mainPos = [[], []]
slidingWindow = []
avgNum = 50
ldir, rdir = 0, 0

while True:
    ret, frame = vc.read()
    if not ret:
        print("video finish")
        break
    
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    rects = detector(gray, 1)
    for rect in rects:
        face = predictor(gray, rect)
        points = get_point_68(face)

        # 找到眼部的點
        lpoints, rpoints = [points[i] for i in left], [points[i] for i in right]
        lpoints, rpoints = eye_rect(lpoints), eye_rect(rpoints)
        leye = gray[lpoints[0][1]:lpoints[1][1], lpoints[0][0]:lpoints[1][0]]
        reye = gray[rpoints[0][1]:rpoints[1][1], rpoints[0][0]:rpoints[1][0]]

        thresh = 10
        # 左眼
        if leye.all():
            # leye = cv2.resize(leye, (400,200))
            cv2.rectangle(frame, lpoints[0], lpoints[1], (0, 255, 0), 2)
            leye = cv2.equalizeHist(leye)
            _, lthreshold = cv2.threshold(leye, thresh, 255, cv2.THRESH_BINARY_INV)
            lthreshold = cv2.medianBlur(lthreshold, 3)
            lx, ly, ret = contouring(lthreshold, lpoints, frame)
            if ret:
                lPosList = np.append(lPosList, np.array([[lx,ly]]), axis=0)
                if len(lPosList) > avgNum:
                    lPosList = np.delete(lPosList, 0, axis=0)
                    mainPos[0] = np.average(lPosList, axis=0)
                    if not lscanned:
                        lscanned = True

            if lscanned:
                ldir = judge_dir([lx, ly], mainPos[0])
                
        # 右眼
        if reye.all():
            cv2.rectangle(frame, rpoints[0], rpoints[1], (0, 255, 0), 2)
            reye = cv2.equalizeHist(leye)
            _, rthreshold = cv2.threshold(leye, thresh, 255, cv2.THRESH_BINARY_INV)
            rthreshold = cv2.medianBlur(rthreshold, 3)
            rx, ry, ret = contouring(rthreshold, rpoints, frame)
            if ret:
                rPosList = np.append(rPosList, np.array([[rx,ry]]), axis=0)
                if len(rPosList) > avgNum:
                    rPosList = np.delete(rPosList, 0, axis=0)
                    mainPos[1] = np.average(rPosList, axis=0)
                    if not rscanned:
                        rscanned = True
            
            if rscanned:
                rdir = judge_dir([rx, ry], mainPos[1])
        
    if lscanned and rscanned:
        # 顯示平均藍點
        cv2.circle(frame, (int(mainPos[0][0]), int(mainPos[0][1])), 4, (255, 0, 0), -1)
        cv2.circle(frame, (int(mainPos[1][0]), int(mainPos[1][1])), 4, (255, 0, 0), -1)
        
        res = combine_eyes(ldir, rdir)
        slidingWindow.append(res)
        # print(slidingWindow)
        eyeDir = judge_slideWin(slidingWindow)
        output = get_dir(eyeDir)
        if output: print(output)
        if len(slidingWindow) >= 5:
            slidingWindow.pop(0)

    cv2.imshow('123', frame)
    if cv2.waitKey(1) == ord('q'):
        break
    # cv2.imwrite('./123.mp4', frame)