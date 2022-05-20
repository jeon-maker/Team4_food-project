#참고자료: https://github.com/Practical-CV/Measuring-Size-of-Objects-with-OpenCV
from cv2 import MARKER_DIAMOND
from scipy.spatial import distance
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

WIDTH_REF_OBJECT = 24 #100원 동전의 지름(mm)

class Object:
    """음식을 포함한 물체"""
    def __init__(self, topImg, sideImg):
        self.topImg = topImg
        self.sideImg = sideImg

class RefObject(Object):
    """물체 중 길이를 가늠하기 위한 reference Object(ex> 100원 동전)"""
    def __init__(self, topImg, sideImg, refObj_width=WIDTH_REF_OBJECT):
        super().__init__(topImg, sideImg)
        self.width = refObj_width
    
class Image:
    """카메라로 찍은 사진(음식, ref물체 포함)"""
    def __init__(self, img_path):
        self.img_path = img_path
        self.original_img = self.getImage() #아무작업 안 한 오리지널 사진
        self.contours = self.getValidContours() #
        self.marked_img = self.getMarkedImage() #여러가지 표시가 되어있는 사진
        
    def getImage(self, path=None):
        """path에서 이미지 파일 리턴"""
        if path is None:
            path = self.img_path

        image = cv2.imread(path)
        return image

    def getValidContours(self, image=None, ignoreLessThan_px=100):
        """
        image에서 윤곽선 따서 쓸만한 윤곽선들만 리턴
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
        cv2.imshow("test", rescaleFrame(edged, 0.5));cv2.waitKey(0)#testcode

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
    
    def getMarkedImage(self, image=None):
        """"""
        marked_img = self.original_img.copy()#testcode
        cv2.drawContours(marked_img, self.contours, -1, (255,0,0), 3)#testcode

        return marked_img
        
        


def getTargetVolume(imgPath_topview, imgPath_sideview, refObject_width=WIDTH_REF_OBJECT):
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
    return
    

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
    testimg = Image("images/top3.png")
    resized_testimg = rescaleFrame(testimg.marked_img, 0.5)
    cv2.imshow("test", resized_testimg);cv2.waitKey(0)#testcode
    #tset