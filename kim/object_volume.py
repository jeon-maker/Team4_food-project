#참고자료: https://github.com/Practical-CV/Measuring-Size-of-Objects-with-OpenCV
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
    def __init__(self, img_path):
        self.img_path = img_path
        self.original_img #아무작업 안 한 오리지널 사진
        self.marked_img #여러가지 표시가 되어있는 사진


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
    print("hello")