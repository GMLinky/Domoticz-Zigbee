#!/usr/bin/env python3
# coding: utf-8 -*-
#
# Author: zaraki673 & pipiche38
#
import Domoticz

from datetime import datetime
from time import time

from Modules.output import raw_APS_request, write_attribute, ReadAttributeRequest_0006_0000, ReadAttributeRequest_0008_0000
from Modules.logging import loggingPhilips


def pollingPhilips( self, key ):
    """
    This fonction is call if enabled to perform any Manufacturer specific polling action
    The frequency is defined in the pollingSchneider parameter (in number of seconds)
    """

    #if  ( self.busy or len(self.ZigateComm.zigateSendingFIFO) > MAX_LOAD_ZIGATE):
    #    return True

    ReadAttributeRequest_0006_0000( self, key)
    ReadAttributeRequest_0008_0000( self, key)

    return False


def callbackDeviceAwake_Philips(self, NwkId, EndPoint, cluster):
    """
    This is fonction is call when receiving a message from a Manufacturer battery based device.
    The function is called after processing the readCluster part
    """

    Domoticz.Log("callbackDeviceAwake_Legrand - Nwkid: %s, EndPoint: %s cluster: %s" \
            %(NwkId, EndPoint, cluster))

    return

def philipsReadRawAPS(self, Devices, srcNWKID, srcEp, ClusterID, dstNWKID, dstEP, MsgPayload):

    if srcNWKID not in self.ListOfDevices:
        return

    loggingPhilips( self, 'Log', "lumiReadRawAPS - Nwkid: %s Ep: %s, Cluster: %s, dstNwkid: %s, dstEp: %s, Payload: %s" \
            %(srcNWKID, srcEp, ClusterID, dstNWKID, dstEP, MsgPayload), srcNWKID)

    if 'Model' not in self.ListOfDevices[srcNWKID]:
        return
    
    _ModelName = self.ListOfDevices[srcNWKID]['Model']

    fcf = MsgPayload[0:2] # uint8
    sqn = MsgPayload[2:4] # uint8
    cmd = MsgPayload[4:6] # uint8
    data = MsgPayload[6:] # all the rest

    loggingPhilips( self, 'Log', "philipsReadRawAPS - Nwkid: %s/%s Cluster: %s, Command: %s Payload: %s" \
        %(srcNWKID,srcEp , ClusterID, cmd, data ))