#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

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
            if ( positionNumber == -1 ):
                print('No match found!')
             #  exit(0)
            else:
                #print('Found template at position #' + str(positionNumber))
                print('Unlocked!') #The accuracy score is: ' + str(accuracyScore))
                unlock = [1]
                lock.writebytes(unlock)
                time.sleep(1)
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
        

    if option == 3:
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
            if ( positionNumber == -1 ):
                print('No match found!')
             #  exit(0)
            else:
                #print('Found template at position #' + str(positionNumber))
                print('locked!') #The accuracy score is: ' + str(accuracyScore
                locked = [0]
                lock.writebytes(locked)
                time.sleep(1) 
        ## OPTIONAL stuff ##
        ## Loads the found template to charbuffer 1
        #f.loadTemplate(positionNumber, 0x01)
        ## Downloads the characteristics of template loaded in charbuffer 1
        #characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
        ## Hashes characteristics of template
        #print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            #exit(1)
