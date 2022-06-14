# import cv2
# import numpy as np
#
# # The image display effect is black and white, but it is actually a color image of three channels
# img = cv2.imread('Black_and_white_squares.jpeg')
#
# # Become a single channel black-and-white picture
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# #
# # # For binarization, note that there are two return values, threshold and result
# ret, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
# #
# cv2.imshow('img', img)
# cv2.imshow('binary', binary)
# #
# # # For contour search, the new version returns two results, contour and level, and the old version returns three parameters, image, contour and level
# contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# #
# # # Print outline
# print(contours)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

import cv2
import numpy as np

img = cv2.imread('shapes.png')
original = img.copy()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

for contour in contours:
    approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
    cv2.drawContours(img, [approx], 0, (0, 0, 0), 5)
    x = approx.ravel()[0]
    y = approx.ravel()[1] - 5

    if len(approx) == 3:
        cv2.putText(img, "Triangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    elif len(approx) == 4:
        x1, y1, w, h = cv2.boundingRect(approx)
        aspectRatio = float(w) / h
        print(aspectRatio)
        if 0.95 <= aspectRatio <= 1.05:
            cv2.putText(img, "Square", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
        else:
            cv2.putText(img, "Rectangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    elif len(approx) == 5:
        cv2.putText(img, "Pentagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    elif len(approx) == 6:
        cv2.putText(img, "Hexagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    elif len(approx) == 7:
        cv2.putText(img, "Heptagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    elif len(approx) == 8:
        cv2.putText(img, "Octagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    elif len(approx) == 10:
        cv2.putText(img, "Star", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    else:
        cv2.putText(img, "circle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))

cv2.imshow("shapes", img)
cv2.waitKey(0)
cv2.destroyAllWindows()


# ROI_number = 0
# cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = cnts[0] if len(cnts) == 2 else cnts[1]
# for cnt in cnts:
#     approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
#     print(len(approx))
#     if len(approx)==5:
#         print("Blue = pentagon")
#         cv2.drawContours(img,[cnt],0,255,-1)
#     elif len(approx)==3:
#         print("Green = triangle")
#         cv2.drawContours(img,[cnt],0,(0,255,0),-1)
#     elif len(approx)==4:
#         print("Red = square")
#         cv2.drawContours(img,[cnt],0,(0,0,255),-1)
#     elif len(approx) == 6:
#         print("Cyan = Hexa")
#         cv2.drawContours(img,[cnt],0,(255,255,0),-1)
#     elif len(approx) == 8:
#         print("White = Octa")
#         cv2.drawContours(img,[cnt],0,(255,255,255),-1)
#     elif len(approx) > 12:
#         print("Yellow = circle")
#         cv2.drawContours(img,[cnt],0,(0,255,255),-1)
#
# cv2.imshow('image', img)
# cv2.imshow('Binary',thresh)
# cv2.waitKey()
#
