#참고자료: https://github.com/Practical-CV/Measuring-Size-of-Objects-with-OpenCV
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

# TODO: 코드 서순
    # 1. 탑뷰 이미지에서 발견한 물체들 나열
    # 2. 사이드뷰 이미지에서 발견한 물체들 나열
    # 3. 1,2 에서 발견한 물체들 중 각각 referance object(refO)과 target object(tarO) 하나씩 선택
    # 4. refO과 tarO의 top, side에서의 width, height 리스트에 저장
    # 5. tarO의 top, side에서의 contour area(cArea)를 리스트에 저장
    # 6. 4에서 구한 refO의 width들로 각도(camAngle_sin)를 계산
    # 7. tarO_top의 height와 camAngle_sin으로 3차원 높이(3dHeight) 계산
    # 8. 물체를 둘러싸는 큐브 부피 구하기
    # 9. cArea를 이용해서 top_proportion과 side_proportion구한 뒤 prism부피 계산
    # 10. 두개의 prism부피 평균값 구한 뒤 리턴

WIDTH_REF_OBJECT = 24 #100원 동전의 지름(mm)

class Object:
    """사진에 찍혀있는 실제물체 하나"""
    def __init__(self, topImg=None, sideImg=None, topContourIndex=None, sideContourIndex=None):
        self.topImg = topImg
        self.sideImg = sideImg
        self.top_cntIndex = topContourIndex
        self.side_cntIndex = sideContourIndex 
    
    def setContourIndex(self, top_idx, side_idx):
        self.top_cntIndex = top_idx
        self.side_cntIndex = side_idx


class RefObject(Object):
    """물체 중 길이를 가늠하기 위한 reference Object(ex> 100원 동전)"""
    def __init__(self, topImg=None, sideImg=None, topContourIndex=None, sideContourIndex=None, refObj_width=WIDTH_REF_OBJECT):
        super().__init__(topImg, sideImg, topContourIndex, sideContourIndex)
        self.width = refObj_width

class Object3D(Object):
    """높이가 있는 3D 물체"""
    def __init__(self, topImg=None, sideImg=None, topContourIndex=None, sideContourIndex=None):
        super().__init__(topImg, sideImg, topContourIndex, sideContourIndex)
        self.top_dimensions = None # 형식 (width, height, area)
        self.side_dimensions = None # 형식 (width, height, area)
        self.volume = None

    def calc2dDimensions(self, image, contour):
        """
        물체를 한 이미지(top/side)에서 봤을 때 width, height, area를 리턴(단위:mm, mm^2)
        image: self.topImg or self.sideImg
        contour: Image.coutours[ContourIndex]
        """
        width, height = image.getWidthHeight(contour)
        width = width / image.PX_PER_MM
        height = height / image.PX_PER_MM

        area = image.getAreaSize_px(contour)
        area = area / (image.PX_PER_MM**2)

        return width, height, area

    def set2dDimensions(self):
        self.top_dimensions = self.calc2dDimensions(self.topImg, self.topImg.contours[self.topContourIndex]) 
        self.side_dimensions = self.calc2dDimensions(self.topImg, self.sideImg.contours[self.sideContourIndex])

class Image:
    """카메라로 찍은 사진(음식, ref물체 포함)"""
    def __init__(self, img_path):
        self.img_path = img_path
        self.original_img = self.getImage() #아무작업 안 한 오리지널 사진
        self.contours = self.getValidContours() #물체로 인식된 윤곽선들 모음
        self.marked_img = self.getMarkedImage() #여러가지 표시가 되어있는 사진
        self.refObj = None # reference object - RefObject()
        self.tarObj = None # target object - Object3D()
        self.PX_PER_MM = None # 1픽셀 당 mm(길이)
        
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
        # cv2.imshow("test", rescaleFrame(edged, 0.5));cv2.waitKey(0)#testcode

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
        (tX, tY) = midpoint(tl, tr)
        (bX, bY) = midpoint(bl, br)
        (lX, lY) = midpoint(tl, bl)
        (rX, rY) = midpoint(tr, br)

        # bbox의 가로 세로 길이 구하기(단위: px)
        width_px = dist.euclidean((tX, tY), (bX, bY))
        height_px = dist.euclidean((lX, lY), (rX, rY))

        return width_px, height_px

    def getAreaSize_px(self, contour):
        """전달받은 contour의 내부 면적 리턴"""
        return cv2.contourArea(contour)
        
    def setObjects(self, refObj: RefObject, tarObj: Object3D):
        self.refObj = refObj
        self.tarObj = tarObj


    def setPixelsPerMetric(self):
        pass

    def px2mm(self):pass
    def px2sqmm(self):pass
          
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

if __name__ == "__main__":
    #test
    idx = 3
    if idx == 1: idx = ''
    refObj = RefObject()
    foodObj = Object3D()
    topImage = Image("images/top{}.png".format(idx))
    sideImage = Image("images/side{}.png".format(idx))
    cv2.imshow('top', rescaleFrame(topImage.marked_img, 0.5))
    cv2.imshow('side', rescaleFrame(sideImage.marked_img, 0.5))
    cv2.waitKey(1)
    
    # 사용자가 refObject와 foodObject를 번호로 지정
    print("<Top Image>")
    top_ref_index = input("Reference 물체의 번호:")
    top_tar_index = input("부피 측정을 원하는 음식의 번호:")
    print("<Side Image>")
    side_ref_index = input("Reference 물체의 번호:")
    side_tar_index = input("부피 측정을 원하는 음식의 번호:")

    # Object들에 index 설정
    refObj.setContourIndex(top_ref_index, side_ref_index)
    foodObj.setContourIndex(top_tar_index, side_tar_index)

    # Image들에 Object 설정
    topImage.setObjects(refObj, foodObj)
    sideImage.setObjects(refObj, foodObj)

    
    #tset
    