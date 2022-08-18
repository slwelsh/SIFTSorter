import cv2
import numpy as np

# load image
img = cv2.imread('mediumturtle.JPG')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale
# threshold to get just the signature (INVERTED)
retval, thresh_gray = cv2.threshold(gray, 100, maxval=255, type=cv2.THRESH_BINARY_INV)

contours, hierarchy = cv2.findContours(thresh_gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

def crop_minAreaRect(img, rect):
    # rotate img
    angle = rect[2]
    rows,cols = img.shape[0], img.shape[1]
    matrix = cv2.getRotationMatrix2D((cols/2,rows/2),angle,1)
    img_rot = cv2.warpAffine(img,matrix,(cols,rows))

    # rotate bounding box
    rect0 = (rect[0], rect[1], 0.0)
    box = cv2.boxPoints(rect)
    pts = np.int0(cv2.transform(np.array([box]), matrix))[0]
    pts[pts < 0] = 0

    # crop and return
    return img_rot[pts[1][1]:pts[0][1], pts[1][0]:pts[2][0]]


# Find object with the biggest bounding box
mx_rect = (0,0,0,0)      # biggest skewed bounding box
mx_area = 0
for cont in contours:
    arect = cv2.minAreaRect(cont)
    area = arect[1][0]*arect[1][1]
    if area > mx_area:
        mx_rect, mx_area = arect, area

# Output to files
roi = crop_minAreaRect(img, mx_rect)
cv2.imwrite('Image_crop.jpg', roi)

box = cv2.boxPoints(mx_rect)
box = np.int0(box)
cv2.drawContours(img,[box],0,(200,0,0),2)
cv2.imwrite('Image_cont.jpg', img)