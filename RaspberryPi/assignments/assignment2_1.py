import cv2
img = cv2.imread("Square_500x500.jpg")
cv2.imshow('original', img)

dimensions = img.shape
print(dimensions)

height = img.shape[0]
width = img.shape[1]

x1 = int(width / 2)
y1 = 100
x2 = 100
y2 = height - 100
x3 = width - 100
y3 = height - 100
x4 = int(width / 2)
y4 = int(height / 2)

thickness = 2

cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), thickness)
cv2.line(img, (x1, y1), (x3, y3), (0, 255, 0), thickness)
cv2.line(img, (x3, y3), (x2, y2), (0, 0, 255), thickness)

text = 'Homework 2'
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_thickness = thickness 

text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

text_x = (width - text_size[0]) // 2
text_y = (height + text_size[1]) // 2

cv2.putText(img, text, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)

cv2.imshow('Draw Triangle with Text', img)

cv2.waitKey(0)
cv2.destroyAllWindows()