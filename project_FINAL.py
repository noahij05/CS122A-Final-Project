#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""
import face_recognition
import picamera
import numpy as np
import time
from pyfingerprint.pyfingerprint import PyFingerprint
import spidev
def createSPI(device):
        spi = spidev.SpiDev()
        spi.open(0,device)
        spi.max_speed_hz = 1000000
        spi.mode = 0
        return spi

lock = createSPI(0)




## Enrolls new finger
##

## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)
# Get a reference to the Raspberry Pi camera.
# If this fails, make sure you have a camera connected to the RPi and that you
# enabled your camera in raspi-config and rebooted first.
camera = picamera.PiCamera()
camera.resolution = (320, 240)
output = np.empty((240, 320, 3), dtype=np.uint8)

# Load a sample picture and learn how to recognize it.
#print("Loading known face image(s)")
noah_image = face_recognition.load_image_file("noah3.jpg")
noah_face_encoding = face_recognition.face_encodings(noah_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []


option = 1
while(option != 0):
    option = int(input("Enter 1 to enroll fingerprint, 2 to authenticate fingerprint, 3 to lock, 0 to quit: "))
    
    if option == 1:
    ## Gets some sensor information
        #print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    ## Tries to enroll new finger
        try:
            print('Waiting for finger...')
        ## Wait that finger is read
            while ( f.readImage() == False ):
                pass
        ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)
        ## Checks if finger is already enrolled
            result = f.searchTemplate()
            positionNumber = result[0]
            if ( positionNumber >= 0 ):
                print('Template already exists!') #at position #' + str(positionNumber))
                #exit(0)
                continue
            print('Remove finger...')
            time.sleep(2)
            print('Waiting for same finger again...')
        ## Wait that finger is read again
            while ( f.readImage() == False ):
                pass
        ## Converts read image to characteristics and stores it in charbuffer 2
            f.convertImage(0x02)
        ## Compares the charbuffers
            if ( f.compareCharacteristics() == 0 ):
                raise Exception('Fingers do not match')
        ## Creates a template
            f.createTemplate()
        ## Saves template at new position number
            positionNumber = f.storeTemplate()
            print('Finger enrolled successfully!')
            #print('New template position #' + str(positionNumber))
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            #exit(1)

    if option == 2:
    ## Gets some sensor information
        #print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
    ## Tries to search the finger and calculate hash
        try:
            print('Waiting for finger...')
        ## Wait that finger is read
            while ( f.readImage() == False ):
                pass
        ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)
        ## Searchs template
            result = f.searchTemplate()
            positionNumber = result[0]
            accuracyScore = result[1]
            matchface = [0]
            #while(1):
            print("Capturing image.")
    # Grab a single frame of video from the RPi camera as a numpy array
            camera.capture(output, format="rgb")

    # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(output)
            print("Found {} faces in image.".format(len(face_locations)))
            face_encodings = face_recognition.face_encodings(output, face_locations)

    # Loop over each face found in the frame to see if it's someone we know.
            for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
                match = face_recognition.compare_faces([noah_face_encoding], face_encoding)
                name = "<Unknown Person>"

                if match[0]:
                    name = "Noah Jimenez"
                    print(name)
                    if (positionNumber == -1):
                        print('no match found!')
                    else:
                        print('Unlocked!')
                        unlocked = [1]
                        lock.writebytes(unlocked)
                        time.sleep(1)
                        
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
        

    if option == 3:
        print('locked!') 
        locked = [0]
        lock.writebytes(locked)
        time.sleep(1) 
