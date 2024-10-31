import cv2

img = cv2.imread("Square_500x500.jpg")
cv2.imshow('original',img)

dimensions = img.shape
print(dimensions)

height = img.shape[0]
width = img.shape[1]

x1 = int(width/2)
y1 = 100
x2 = 100
y2 = height-100
x3 = width-100
y3 = height-100
x4 = int(width/2)
y4 = int(height/2)

print(x1, y1, x2, y2)
thickness = 2

cv2.line(img,(x1,y1),(x2,y2),(255,0,0),thickness)
cv2.line(img,(x1,y1),(x3,y3),(0,255,0),thickness)
cv2.line(img,(x3,y3),(x2,y2),(0,0,255),thickness)
cv2.imshow('Draw line',img)
font = cv2.FONT_HERSHEY_SIMPLEX
fontsize = 1
cv2.putText(img,'OpenCV',(x4,y4), font, fontsize ,(0,0,0),thickness,cv2.LINE_AA)
cv2.imshow('Homework 2',img)

cv2.waitKey(0)
cv2.destroyAllWindows()