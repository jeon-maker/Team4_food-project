#이 코드는 https://github.com/Practical-CV/Measuring-Size-of-Objects-with-OpenCV 를 기반으로 만들어졌음

# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import math

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def object_size(img_path, ref_width):
	listABs = []

	# load the image, convert it to grayscale, and blur it slightly
	image = cv2.imread(img_path)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (7, 7), 0)

	# perform edge detection, then perform a dilation + erosion to
	# close gaps in between object edges
	edged = cv2.Canny(gray, 50, 100)
	edged = cv2.dilate(edged, None, iterations=1)
	edged = cv2.erode(edged, None, iterations=1)

	# find contours in the edge map
	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	# sort the contours from left-to-right and initialize the
	# 'pixels per metric' calibration variable
	(cnts, _) = contours.sort_contours(cnts)
	pixelsPerMetric = None
	# print(type(cnts))#testcode
	# print(len(cnts))#testcode

	orig = image.copy()
	# loop over the contours individually
	for c in cnts:
		# print(type(c))#testcode
		# print(len(c))#testcode
		# cv2.drawContours(image, c, -1, (255,0,0), 3)#testcode
		# if the contour is not sufficiently large, ignore it
		if cv2.contourArea(c) < 100:
			continue
		else:
			cArea = cv2.contourArea(c)
			cv2.drawContours(image, c, -1, (255,0,0), 3)
		
		# cArea = cv2.contourArea(c)#testcode
		# cv2.drawContours(image, c, -1, (255,0,0), 3)#testcode

		# compute the rotated bounding box of the contour
		# TODO: cv2.boundingRect(contour)로 바꿔서 계산
		box = cv2.minAreaRect(c)
		box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
		box = np.array(box, dtype="int")

		# order the points in the contour such that they appear
		# in top-left, top-right, bottom-right, and bottom-left
		# order, then draw the outline of the rotated bounding
		# box
		box = perspective.order_points(box)
		cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

		# loop over the original points and draw them
		for (x, y) in box:
			cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

		# unpack the ordered bounding box, then compute the midpoint
		# between the top-left and top-right coordinates, followed by
		# the midpoint between bottom-left and bottom-right coordinates
		(tl, tr, br, bl) = box
		(tltrX, tltrY) = midpoint(tl, tr)
		(blbrX, blbrY) = midpoint(bl, br)

		# compute the midpoint between the top-left and top-right points,
		# followed by the midpoint between the top-righ and bottom-right
		(tlblX, tlblY) = midpoint(tl, bl)
		(trbrX, trbrY) = midpoint(tr, br)

		# draw the midpoints on the image
		cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

		# draw lines between the midpoints
		cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
			(255, 0, 255), 2)
		cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
			(255, 0, 255), 2)

		# compute the Euclidean distance between the midpoints
		dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
		dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
#--------------------------------------여기까지 함--------------------------------------#

		# if the pixels per metric has not been initialized, then
		# compute it as the ratio of pixels to supplied metric
		# (in this case, mm)
		if pixelsPerMetric is None:
			pixelsPerMetric = dB / ref_width

		# compute the size of the object
		dimA = dA / pixelsPerMetric
		dimB = dB / pixelsPerMetric
		cArea = cArea / (pixelsPerMetric**2)

		# draw the object sizes on the image
		cv2.putText(orig, "{:.1f}mm".format(dimA),
			(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (255, 255, 255), 2)
		cv2.putText(orig, "{:.1f}mm".format(dimB),
			(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (255, 255, 255), 2)

		listABs.append((dimA, dimB, cArea))

	# show the output image
	cv2.imshow("Image", orig)
	cv2.waitKey(0)
		
	# print(listABs, listABs[0][0]*listABs[0][1], listABs[1][0]*listABs[1][1]) #testcode
	return listABs

# % python .\object_size_v.py -i1 .\images\top.png -i2 .\images\side.png -w 24
if __name__ == "__main__":
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i1", "--image1", required=True,
		help="path to the first input image")
	ap.add_argument("-i2", "--image2", required=True,
		help="path to the second input image")
	ap.add_argument("-w", "--width", type=float, required=True,
		help="width of the left-most object in the image (in mm)")
	args = vars(ap.parse_args())

	# 두 이미지에 대해 dimensions를 받기
	dims1 = object_size(args["image1"], args["width"])
	dims2 = object_size(args["image2"], args["width"])

	camAngle_sin = dims2[0][0]/dims1[0][0]
	x = dims1[1][1]
	y = dims1[1][0]
	z = dims2[1][1] / (1/(math.sqrt(1-camAngle_sin**2)))
	print(dims2[1][1])#testcode
	print(camAngle_sin)#testcode


	top_proportion = dims1[1][2]/(dims1[1][0]*dims1[1][1])
	side_proportion = dims2[1][2]/(dims2[1][0]*dims2[1][1])

	print("box x, y, z: ({}, {}, {})".format(x, y, z))
	print("box volume:", x*y*z, "mm^3")
	print("topP: {}, vol_estm: {}mm^3".format(top_proportion, x*y*z*top_proportion))
	print("sideP: {}, vol_estm: {}mm^3".format(side_proportion, x*y*z*side_proportion))
	print("average: {}mm^3".format((x*y*z*top_proportion + x*y*z*side_proportion)/2))