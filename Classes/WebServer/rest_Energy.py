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

import json
from time import time

from Classes.WebServer.headerResponse import (prepResponseMessage,
                                              setupHeadersResponse)


def rest_req_nwk_inter(self, verb, data, parameters):

    self.logging("Debug", "rest_req_nwk_inter")
    _response = prepResponseMessage(self, setupHeadersResponse())
    if verb == "GET":
        action = {"Name": "Nwk-Interferences", "TimeStamp": int(time())}
        _response["Data"] = json.dumps(action, sort_keys=True)

        if self.zigbee_communication == 'zigate' and self.pluginParameters["Mode2"] != "None" and self.networkenergy:
            self.networkenergy.start_scan()

        if self.zigbee_communication == 'zigpy' and self.pluginParameters["Mode2"] != "None" and self.networkenergy:
            self.networkenergy.zigbee_zigpy_energy_scan()

    return _response


def rest_req_nwk_full(self, verb, data, parameters):

    _response = prepResponseMessage(self, setupHeadersResponse())

    if verb == "GET":
        action = {"Name": "Nwk-Energy-Full", "TimeStamp": int(time())}
        _response["Data"] = json.dumps(action, sort_keys=True)

        if self.pluginParameters["Mode2"] != "None" and self.networkenergy:
            self.networkenergy.start_scan(root="0000", target="0000")

    return _response
