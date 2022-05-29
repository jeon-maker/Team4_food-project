#참고자료: https://github.com/Practical-CV/Measuring-Size-of-Objects-with-OpenCV
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import math
     
class Image:
    """카메라로 찍은 사진(음식, ref물체 포함)"""

    def __init__(self, img_path):
        self.img_path = img_path
        self.original_img = self.getImage() #아무작업 안 한 오리지널 사진
        self.contours = self.getValidContours() #물체로 인식된 윤곽선들 모음
        self.marked_img = self.getMarkedImage() #여러가지 표시가 되어있는 사진
        self.contour_ref = None # contour of reference object
        self.PX_PER_MM = None # 1픽셀 당 mm(길이)
        self.WIDTH_REF_OBJECT = 24 #100원 동전의 지름(mm)
        
    def getImage(self, path=None):
        """path에서 이미지 파일 리턴"""
        if path is None: path = self.img_path

        image = cv2.imread(path)
        return image

    def getValidContours(self, image=None, ignoreLessThan_px=100):
        """
        image에서 윤곽선 따서 쓸만한 윤곽선들의 list 리턴
        ignoreLessThan_px 보다 적은 영역으로 된 윤곽은 버림
        """
        if image is None:
            image = self.original_img

        # 이미지 grayscale로 변경. 조금 blur시키기.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # 이미지 엣지 따고, 확장 수축을 통해 자잘한 경계선들을 제거
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        # edged 이미지에서 윤곽선따기, cnts 좌->우로 정렬
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        (cnts, _) = contours.sort_contours(cnts)

        # 필요한 contours만 분류해서 valid_cnts에 저장(면적이 ignoreLessThan_px보다 작은 것 무시)
        valid_cnts = list()
        for cnt in cnts:
            if cv2.contourArea(cnt) < ignoreLessThan_px: continue
            else: valid_cnts.append(cnt)

        return valid_cnts
    
    def getMarkedImage(self, original_img=None, contours=None):
        """original_img에서 물체들을 탐지하여 사각형 및 index를 표시한 이미지 리턴"""
        if original_img == None: original_img = self.original_img
        if contours == None: contours = self.contours

        marked_img = original_img.copy()

        cntIndex = 0
        for cnt in contours:
            box = self.getBoundingBox(cnt)

            # bbox 꼭짓점 찍고, 상자 그리기
            for (x, y) in box: cv2.circle(marked_img, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.drawContours(marked_img, [box.astype("int")], -1, (0, 255, 0), 2)

            # bbox 각 변의 중간점 좌표 구하기
            (tl, tr, br, bl) = box
            (tX, tY) = midpoint(tl, tr)
            (bX, bY) = midpoint(bl, br)
            (lX, lY) = midpoint(tl, bl)
            (rX, rY) = midpoint(tr, br)

            # bbox의 무게중심 좌표 구하기
            (cX, cY) = midpoint((tX, tY), (bX, bY))

            # bbox 각 변의 중간점 그리기
            cv2.circle(marked_img, (int(tX), int(tY)), 5, (255, 0, 0), -1)
            cv2.circle(marked_img, (int(bX), int(bY)), 5, (255, 0, 0), -1)
            cv2.circle(marked_img, (int(lX), int(lY)), 5, (255, 0, 0), -1)
            cv2.circle(marked_img, (int(rX), int(rY)), 5, (255, 0, 0), -1)

            # bbox 중간점을 잇는 선 그리기
            cv2.line(marked_img, (int(tX), int (tY)), (int(bX), int(bY)), (255, 0, 255), 2)
            cv2.line(marked_img, (int(lX), int (lY)), (int(rX), int(rY)), (255, 0, 255), 2)

            # 각 contour의 index 그리기
            cv2.putText(marked_img, "[{}]".format(cntIndex), (int(cX)-35, int(cY)), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)

            # contour 그리기
            # cv2.drawContours(marked_img, cnt, -1, (255,0,0), 3)

            cntIndex += 1

        return marked_img
    
    def getBoundingBox(self, contour):
        """
        전달받은 contour을 감싸는 사각형(bbox)의 꼭짓점 좌표 리턴
        형식: top-left, top-right, bottom-right, bottom-left
        """
        # Rotated bounding box 방식으로 bbox 처리
        # TODO: cv2.boundingRect(contour)로 바꿔서 계산하는 것 고려
        box = cv2.minAreaRect(contour)
        box = cv2.boxPoints(box) # box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box) # 보통은 cv2아니라서 주석처리
        box = np.array(box, dtype="int")

        # 꼭짓점 좌표를 tl, tr, br, bl 순으로 조정
        box = perspective.order_points(box)

        return box

    def getWidthHeight_px(self, contour):
        """전달받은 contour의 bbox에서 width, height 계산 후 리턴"""
        box = self.getBoundingBox(contour)

        # bbox 각 변의 중간점 좌표 구하기
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        # bbox의 가로 세로 길이 구하기(단위: px)
        width_px = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
        height_px = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))

        return width_px, height_px

    def getAreaSize_px(self, contour):
        """전달받은 contour의 내부 면적 리턴"""
        return cv2.contourArea(contour)

    def setContour_ref(self, index):
        """입력된 index에 해당하는 contour을 self.contour_ref로 지정"""
        self.contour_ref = self.contours[index]

    def setPixelsPerMetric(self):
        self.PX_PER_MM = self.getWidthHeight_px(self.contour_ref)[0]  / self.WIDTH_REF_OBJECT

class Object3D():
    """
    높이가 있는 3D 물체
    metric unit은 mm, mm^2, mm^3으로 통일(pixel 아님)
    """
    def __init__(self, topImg: Image, sideImg: Image):
        # 기초 맴버변수
        self.topImg = topImg
        self.sideImg = sideImg
        self.top_cntIndex = None
        self.side_cntIndex = None

        # 2D관련 정보들
        self.top_dimensions = None # 형식 (width, height, area)
        self.side_dimensions = None # 형식 (width, height, area)
        self.SINE_CAM_ANGLE = None
        
        # Bounding Cuboid의 dimensions
        self.bCuboid_width = None
        self.bCuboid_depth = None
        self.bCuboid_height = 0
        
        self.volume = None

    def setContourIndex(self, top_idx, side_idx):
        self.top_cntIndex = top_idx
        self.side_cntIndex = side_idx

    def calc2dDimensions(self, image: Image, contour):
        """
        물체를 한 이미지(top/side)에서 봤을 때 width, height, area를 리턴(단위:mm, mm^2)
        image: self.topImg or self.sideImg
        contour: Image.coutours[ContourIndex]
        """
        width, height = image.getWidthHeight_px(contour)
        width = width / image.PX_PER_MM
        height = height / image.PX_PER_MM

        area = image.getAreaSize_px(contour)
        area = area / (image.PX_PER_MM**2)

        return width, height, area

    def set2dDimensions(self):
        self.top_dimensions = self.calc2dDimensions(self.topImg, self.topImg.contours[self.top_cntIndex]) 
        self.side_dimensions = self.calc2dDimensions(self.sideImg, self.sideImg.contours[self.side_cntIndex])

    def calcCamAngle(self):
        """self.SINE_CAM_ANGLE 계산 후 설정"""
        # TODO: 각도 구하는 것 재검토 요망
        top_refH = self.topImg.getWidthHeight_px(self.topImg.contour_ref)[1] / self.topImg.PX_PER_MM
        side_refH = self.sideImg.getWidthHeight_px(self.sideImg.contour_ref)[1] / self.sideImg.PX_PER_MM
        self.SINE_CAM_ANGLE = side_refH / top_refH
    
    def setBCuboidDimensions(self):
        # TODO: 높이 구하는 것 재검토 요망(기존 object_size.py들과 다른 결과)
        self.bCuboid_width = self.top_dimensions[0] # topW
        self.bCuboid_depth = self.top_dimensions[1] # topH
        self.bCuboid_height = self.side_dimensions[1] / math.sqrt(1-self.SINE_CAM_ANGLE**2) # sideH/sqrt(1-sin^2)

    def calcVolume(self):
        """prism 형태의 도형 두가지를 계산하고 평균값 도출"""
        tArea = self.top_dimensions[2]
        tHeight = self.bCuboid_height
        sArea = self.side_dimensions[2]
        sHeight = self.bCuboid_depth

        top_prismV = tArea * tHeight
        side_prismV = sArea * sHeight

        self.volume = (top_prismV + side_prismV) / 2

    def setAll(self):
        """cnt_index만 설정되어있으면 나머지 맴버변수 모두 설정"""
        self.set2dDimensions()
        self.calcCamAngle()
        self.setBCuboidDimensions()
        self.calcVolume()
          
def midpoint(point1, point2):
    return ((point1[0] + point2[0])/2, (point1[1] + point2[1])/2)

def rescaleFrame(frame, scale=0.75):
    """
    이미지를 띄우는 창의 프레임을 일정비율로 재조정하는 함수
    사용법: resized_img = rescaleFrame(img, scale); cv2.imshow('~~~', resized_img)
    출처: https://github.com/jasmcaus/opencv-course/blob/master/Section%20%232%20-%20Advanced/rescale_resize.py
    """
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)

    dimensions = (width, height)

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def calcVolume(top_image_path, side_image_path):
    topImage = Image(top_image_path)
    sideImage = Image(side_image_path)

    foodObj = Object3D(topImage, sideImage)
    cv2.imshow('top', rescaleFrame(topImage.marked_img, 0.5))
    cv2.imshow('side', rescaleFrame(sideImage.marked_img, 0.5))
    cv2.waitKey(1)
    
    # 사용자가 refObject와 foodObject를 번호로 지정
    print("<Top Image>")
    top_ref_index = int(input("Reference 물체의 번호:"))
    top_tar_index = int(input("부피 측정을 원하는 음식의 번호:"))
    print("<Side Image>")
    side_ref_index = int(input("Reference 물체의 번호:"))
    side_tar_index = int(input("부피 측정을 원하는 음식의 번호:"))

    # Object들에 index 설정
    topImage.setContour_ref(top_ref_index)
    sideImage.setContour_ref(side_ref_index)
    foodObj.setContourIndex(top_tar_index, side_tar_index)

    # 각 이미지의 px_per_mm 설정
    topImage.setPixelsPerMetric()
    sideImage.setPixelsPerMetric()

    foodObj.setAll()

    return foodObj.volume


if __name__ == "__main__":
    #test
    idx = 3
    if idx == 1: idx = ''
    # topImage = Image("images/top{}.png".format(idx))
    # sideImage = Image("images/side{}.png".format(idx))

    # # topImage = Image("images/top5.jpg")
    # # sideImage = Image("images/side5.jpg")

    # foodObj = Object3D(topImage, sideImage)
    # cv2.imshow('top', rescaleFrame(topImage.marked_img, 0.5))
    # cv2.imshow('side', rescaleFrame(sideImage.marked_img, 0.5))
    # cv2.waitKey(1)
    
    # # 사용자가 refObject와 foodObject를 번호로 지정
    # print("<Top Image>")
    # top_ref_index = int(input("Reference 물체의 번호:"))
    # top_tar_index = int(input("부피 측정을 원하는 음식의 번호:"))
    # print("<Side Image>")
    # side_ref_index = int(input("Reference 물체의 번호:"))
    # side_tar_index = int(input("부피 측정을 원하는 음식의 번호:"))

    # # Object들에 index 설정
    # topImage.setContour_ref(top_ref_index)
    # sideImage.setContour_ref(side_ref_index)
    # foodObj.setContourIndex(top_tar_index, side_tar_index)

    # # 각 이미지의 px_per_mm 설정
    # topImage.setPixelsPerMetric()
    # sideImage.setPixelsPerMetric()

    # foodObj.setAll()
    # print("x,y,z = {}, {}, {}".format(foodObj.bCuboid_width, foodObj.bCuboid_depth, foodObj.bCuboid_height))#testcode

    print(calcVolume("images/top{}.png".format(idx), "images/side{}.png".format(idx)), "mm^3")
    #tset
    