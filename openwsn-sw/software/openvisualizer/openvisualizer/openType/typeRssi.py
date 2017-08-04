# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('typeRssi')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import openType
import math

class typeRssi(openType.openType):
    
    def __init__(self):
        # log
        log.info("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        return '{0} dBm'.format(self.rssi)
    
    #======================== public ==========================================
    
    def update(self,rssi):
        # modified by Yoo DongHwa
        # 2017-07-08

        # line below was the original statement
        self.rssi = rssi

        # cc2420 base tx power value
        TxPower = -31

        # rssi to distance code
        # referenced from
        # https://www.quora.com/How-do-I-calculate-distance-in-meters-km-yards-from-rssi-values-in-dBm-of-BLE-in-android
        # https://gist.github.com/eklimcz/446b56c0cb9cfe61d575

        # if(rssi == 0):
        #    self.rssi = 0
        # else:
        #    ratio = rssi * 1.0 / TxPower

        #    if(ratio < 1.0):
        #        self.rssi = math.pow(ratio, 10)
        #    else:
        #        self.rssi = math.pow(10, (TxPower - rssi) / (10 * 2))
    
    #======================== private =========================================
    