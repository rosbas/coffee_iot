#realtimecv + ultrasonic + netpie at the same time.

from imutils.video import VideoStream
from pyzbar.pyzbar import decode
import RPi.GPIO as GPIO
# from multiprocessing import Process
# import threading
from threading import Thread
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import random
import ssl
import argparse
import datetime
import imutils
import time
import cv2

#arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv", help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

# Realtime cv section
print("[INFO] starting video stream...")
# for using usb webcam
# vs = VideoStream(src=0).start()
# for using pi cam
vs = VideoStream(userPiCamera=True).start()
time.sleep(2.0)
csv = open(args["output"], "w")
found = set()

# ultrasonic section
print("[INFO] Initiating the ultrasonic sensor")
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 18
#echo pin require exactly 3.3V
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# netpie section.
port = 1883 # default port
Server_ip = "broker.netpie.io" 
Subscribe_Topic = "@msg/NodeRed"
Publish_Topic = "@msg/NodeRed"
Client_ID = "7ddaf291-1dce-4d8f-91d8-4f0a755d3338"
Token = "vmcqnthj6CnEdqmxjBDMGpPQYhMXKJof"
Secret = "OcoaJU9QeGFXK)CrU0de3u#S3iZ-XzAj"

MqttUser_Pass = {"username":Token,"password":Secret}
client_initiate();

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(Subscribe_Topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def client_initiate():
    client = mqtt.Client(protocol=mqtt.MQTTv311,client_id=Client_ID, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.subscribe(Subscribe_Topic)
    client.username_pw_set(Token,Secret)
    client.connect(Server_ip, port)
    client.loop_start()

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

#cam thread loop
def threadA():
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
                print("[Info] Barcode data {} is read\n".format(barcodeData))
                

        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

# ultrasonic thread loop
def threadB():
    while True:
        dist = distance()
        print("Measured Distance = %.1f cm" % dist)
        time.sleep(1)
    # try:
    #     while True:
    #         dist = distance()
    #         print("Measured Distance = %.1f cm" % dist)
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("Measurement stopped by User")
    #     GPIO.cleanup()

# netpie thread loop
def threadC():
    while True:
        data = {
        "Temp": random.randrange(30, 40),
        "Humi": random.randrange(50, 80)
        }
        data_out=json.dumps(data) # encode object to JSON
        client.publish(Publish_Topic, data_out, retain= True)
        print ("Publish.....")
        time.sleep(2)

if __name__ == "__main__":
    t1=Thread(target = threadA)
    t2=Thread(target = threadB)
    t3=Thread(target = threadC)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t3.setDaemon(True)
    t1.start()
    t2.start()
    t3.start()
    while True:
        pass

print("[INFO] cleaning up...")
csv.close()
cv2.destroyAllWindows()
vs.stop()