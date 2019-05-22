import cv2

vid_cap = cv2.VideoCapture(0)
vid_cap.set(3, 1280)
vid_cap.set(4, 720)

if not vid_cap.isOpened():
	raise Exception("could not open video device")

for x in range(10):
	ret, frame = vid_cap.read()

cv2.imwrite("test.jpg", frame)

vid_cap.release()