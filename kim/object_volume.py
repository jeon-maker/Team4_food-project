from scipy.spatial import distance
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

#한 이미지에 들어있는 물체들
class objectsInImg:
    def __init__(self, imagePath):
        self.imgPath = imagePath
        self.objList = list()

#ref width는 100원의 지름인 24mm를 기본값으로
def getTargetVolume(imgPath_topview, imgPath_sideview, refMatarial_width=24):
    """
    TODO: 코드 서순
    1. 탑뷰 이미지에서 발견한 물체들 나열
    2. 사이드뷰 이미지에서 발견한 물체들 나열
    3. 1,2 에서 발견한 물체들 중 각각 referance matarial(refM)과 target matarial(tarM) 하나씩 선택
    4. refM과 tarM의 top, side에서의 width, height 리스트에 저장
    5. tarM의 top, side에서의 contour area(cArea)를 리스트에 저장
    6. 4에서 구한 refM의 width들로 각도(camAngle_sin)를 계산
    7. tarM_top의 height와 camAngle_sin으로 3차원 높이(3dHeight) 계산
    8. 물체를 둘러싸는 큐브 부피 구하기
    9. cArea를 이용해서 top_proportion과 side_proportion구한 뒤 prism부피 계산
    10. 두개의 prism부피 평균값 구한 뒤 리턴
    """

def midpoint(point1, point2):
    return ((point1[0] + point2[0])/2, (point1[1] + point2[1])/2)

if __name__ == "__main__":
    print("hello")