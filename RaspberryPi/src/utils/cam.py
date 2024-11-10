import cv2 as cv

if __name__ == "__main__":
    cap = cv.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        cv.imshow("Webcam", frame)

        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv.destroyAllWindows()
