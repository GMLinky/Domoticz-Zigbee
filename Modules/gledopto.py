#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Implementation of Zigbee for Domoticz plugin.
#
# This file is part of Zigbee for Domoticz plugin. https://github.com/zigbeefordomoticz/Domoticz-Zigbee
# (C) 2015-2024
#
# Initial authors: zaraki673 & pipiche38
#
# SPDX-License-Identifier:    GPL-3.0 license

from Modules.readAttributes import (ReadAttributeRequest_0006_0000,
                                    ReadAttributeRequest_0008_0000)


def pollingGledopto(self, key):

    """
    This fonction is call if enabled to perform any Manufacturer specific polling action
    The frequency is defined in the pollingSchneider parameter (in number of seconds)
    """

    rescheduleAction = False

    # if  ( self.busy or self.ControllerLink.loadTransmit() > MAX_LOAD_ZIGATE):
    #    return True

    ReadAttributeRequest_0006_0000(self, key)
    ReadAttributeRequest_0008_0000(self, key)

    return rescheduleAction


def callbackDeviceAwake_Gledopto(self, Devices, NwkId, EndPoint, cluster):

    """
    This is fonction is call when receiving a message from a Manufacturer battery based device.
    The function is called after processing the readCluster part
    """

    self.log.logging("Gledopto", "Debug", "callbackDeviceAwake_Legrand - Nwkid: %s, EndPoint: %s cluster: %s" % (
        NwkId, EndPoint, cluster))
