import cv2
import dlib
import numpy as np
import collections



class eyeTracker:
    # dlib眼睛點idx
    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]
    NumOfAvg = 50
    thresh = 10
    slidingWindowSize = 7

    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('./src/shape_predictor_68_face_landmarks.dat')

        self.lPosList, self.rPosList = np.empty((0,2), np.int64), np.empty((0,2), np.int64)
        self.lscanned, self.rscanned = False, False
        self.slidingWindow = []
        self.ldir, self.rdir = 0, 0
        self.curFrame = None

        # 綠框、瞳孔、平均
        self.eyeRect = [[], []]
        self.pupil = [[], []]
        self.mainPos = [[], []]

    def get_point_68(self, face):
        coords = np.zeros((68, 2), dtype=np.int64)
        for i in range(0, 68):
            coords[i] = [face.part(i).x, face.part(i).y]
        return coords

    def eye_rect(self, points):
        x, y = [e[0] for e in points], [e[1] for e in points]
        bias = 5
        xmin, ymin = min(x) -bias, min(y) -bias
        xmax, ymax = max(x) +bias, max(y) +bias
        return [(xmin, ymin), [xmax, ymax]]

    # 將當前與平均判斷單眼方向 沒動0 上1 右2 下3 左4
    def judge_dir(self, curPos, mainPos):
        xyScale, eyeThresh, maxThresh = 1.5, 8, 20
        difx, dify = curPos - mainPos
        absx, absy = abs(difx * xyScale), abs(dify)
        if maxThresh > absx > eyeThresh or maxThresh > absy > eyeThresh:
            if absx > absy:
                if difx < 0: return 4
                else: return 2
            else:
                if dify < 0: return 1
                else: return 3
        return 0

    def combine_eyes(self, ldir, rdir):
        if ldir == rdir: return ldir
        elif ldir == 0:  return rdir
        elif rdir == 0:  return ldir
        return 0

    def judge_slideWin(self):
        c = collections.Counter(self.slidingWindow)
        mc = c.most_common()[0]
        if mc[1] > self.slidingWindowSize//2: return mc[0]
        else: return 0

    def get_dir(self, dir):
        if dir == 1: return 'up'
        elif dir == 2: return 'right'
        elif dir == 3: return 'down'
        elif dir == 4: return 'left'
        return

    # return綠框的兩端點 [min(x, y), max(x, y)]
    def get_eye_rect(self, points, isLeft):
        eyePoints = [points[i] for i in self.left] if isLeft else [points[i] for i in self.right]
        eyePoints = self.eye_rect(eyePoints)

        return eyePoints

    # return瞳孔座標
    def get_pupil(self, gray, eyePos):
        eye = gray[eyePos[0][1]:eyePos[1][1], eyePos[0][0]:eyePos[1][0]]
        if eye.all():
            # eye = cv2.resize(eye, (400,200))
            eye = cv2.equalizeHist(eye)
            _, threshold = cv2.threshold(eye, self.thresh, 255, cv2.THRESH_BINARY_INV)
            threshold = cv2.medianBlur(threshold, 3)
            cnts, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            try:
                cnt = max(cnts, key = cv2.contourArea)
                M = cv2.moments(cnt)
                cx = int(M['m10']/M['m00']) + eyePos[0][0]
                cy = int(M['m01']/M['m00']) + eyePos[0][1]
                return [cx, cy], True
            except:
                return  [-1,-1], False
        return  [-1,-1], False

    # 紀錄平均
    def get_mainPos_coord(self, pupil, PosList, scanned):
        PosList = np.append(PosList, np.array([pupil]), axis=0)
        if len(PosList) > self.NumOfAvg:
            PosList = np.delete(PosList, 0, axis=0)
            if not scanned:
                scanned = True
        return np.average(PosList, axis=0), PosList, scanned

    # 產生最終結果
    def get_sliding_window_output(self):
        res = self.combine_eyes(self.ldir, self.rdir)
        self.slidingWindow.append(res)
        # print(slidingWindow)
        eyeDir = self.judge_slideWin()
        # print(eyeDir)
        output = self.get_dir(eyeDir)
        if len(self.slidingWindow) >= self.slidingWindowSize:
            self.slidingWindow.pop(0)

        return output

    def get_output_img(self):
        return self.curFrame
    
    # main function
    def eye_track(self, frame):
        self.curFrame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(self.curFrame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # 找到眼部兩眼的各6個座標
        rect = self.detector(gray, 1)
        if len(rect) == 0: return
        face = self.predictor(gray, rect[0])
        points = self.get_point_68(face)

        # 取得左右眼框位置
        leyePos, reyePos = self.get_eye_rect(points, True), self.get_eye_rect(points, False)
        cv2.rectangle(self.curFrame, leyePos[0], leyePos[1], (0, 255, 0), 2)
        cv2.rectangle(self.curFrame, reyePos[0], reyePos[1], (0, 255, 0), 2)
        self.eyeRect = [leyePos, reyePos]

        # 取得瞳孔位置
        lpupil, lret = self.get_pupil(gray, leyePos)
        rpupil, rret = self.get_pupil(gray, reyePos)
        self.pupil = [lpupil, rpupil]

        if lret:
            cv2.circle(self.curFrame, (lpupil[0], lpupil[1]), 4, (0, 0, 255), -1)
            self.mainPos[0], self.lPosList, self.lscanned = self.get_mainPos_coord(lpupil, self.lPosList, self.lscanned)
        if rret:
            cv2.circle(self.curFrame, (rpupil[0], rpupil[1]), 4, (0, 0, 255), -1)
            self.mainPos[1], self.rPosList, self.rscanned = self.get_mainPos_coord(rpupil, self.rPosList, self.rscanned)
                

        if self.lscanned and self.rscanned:
            # 顯示平均藍點
            cv2.circle(self.curFrame, (int(self.mainPos[0][0]), int(self.mainPos[0][1])), 4, (255, 0, 0), -1)
            cv2.circle(self.curFrame, (int(self.mainPos[1][0]), int(self.mainPos[1][1])), 4, (255, 0, 0), -1)
            
            self.ldir = self.judge_dir(lpupil, self.mainPos[0])
            self.rdir = self.judge_dir(rpupil, self.mainPos[1])

            out = self.get_sliding_window_output()
            if out: print(out)