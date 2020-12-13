#realtimecv + ultrasonic + uart at the same time.

from imutils.video import VideoStream
from pyzbar.pyzbar import decode
# from multiprocessing import Process
# import threading
import argparse
import datetime
import imutils
import time
import cv2

#arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv", help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

print("[INFO] starting video stream...")

# for using usb webcam
# vs = VideoStream(src=0).start()
# for using pi cam
vs = VideoStream(userPiCamera=True).start()
time.sleep(2.0)

csv = open(args["output"], "w")
found = set()

print("[INFO] Initiating the ultrasonic sensor")
GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 18
#echo pin require exactly 3.3V
GPIO_ECHO = 24

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    GPIO.output(GPIO_TRIGGER,True)

    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER,False)

    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300)/2

    return distance


while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    barcodes = decode(frame)

    for barcode in barcodes:
        (x,y,w,h) = barcode.rect
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        text = "{} ({})".format(barcodeData,barcodeType)
        cv2.putText(frame,text,(x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255),2)

        if barcodeData not in found:
            csv.write("{},{}\n".format(datetime.datetime.now(), barcodeData))
            csv.flush()
            found.add(barcodeData)
    cv2.imshow("Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    # ultrasonic loop, might need async options
    dist = distance()
    print("Measured Distance = %.1f cm" % dist)
    time.sleep(1)

print("[INFO] cleaning up...")
csv.close()
cv2.destroyAllWindows()
vs.stop()