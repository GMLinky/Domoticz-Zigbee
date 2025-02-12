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

"""
    Module: heartbeat.py

    Description: Manage all actions done during the onHeartbeat() call

"""

import datetime
import time

from Modules.basicOutputs import getListofAttribute
from Modules.casaia import pollingCasaia
from Modules.danfoss import danfoss_room_sensor_polling
from Modules.domoticzAbstractLayer import (find_widget_unit_from_WidgetID,
                                           is_device_ieee_in_domoticz_db)
from Modules.domoTools import (RetreiveWidgetTypeList,
                               reset_device_ieee_unit_if_needed,
                               timedOutDevice)
from Modules.pairingProcess import (binding_needed_clusters_with_zigate,
                                    processNotinDBDevices)
from Modules.paramDevice import sanity_check_of_param
from Modules.pluginDbAttributes import STORE_CONFIGURE_REPORTING
from Modules.readAttributes import (READ_ATTRIBUTES_REQUEST,
                                    ReadAttribute_ZLinkyIndex,
                                    ReadAttributeReq,
                                    ReadAttributeReq_Scheduled_ZLinky,
                                    ReadAttributeReq_ZLinky,
                                    ReadAttributeRequest_0b04_050b_0505_0508,
                                    ReadAttributeRequest_0001,
                                    ReadAttributeRequest_0006_0000,
                                    ReadAttributeRequest_0008_0000,
                                    ReadAttributeRequest_0101_0000,
                                    ReadAttributeRequest_0102_0008,
                                    ReadAttributeRequest_0201_0012,
                                    ReadAttributeRequest_0402,
                                    ReadAttributeRequest_0405,
                                    ReadAttributeRequest_0702_0000,
                                    ReadAttributeRequest_0702_0017,
                                    ReadAttributeRequest_0702_PC321,
                                    ReadAttributeRequest_0702_ZLinky_TIC,
                                    ReadAttributeRequest_ff66,
                                    ping_device_with_read_attribute,
                                    ping_devices_via_group, ping_tuya_device)
from Modules.schneider_wiser import schneiderRenforceent
from Modules.switchSelectorWidgets import SWITCH_SELECTORS
from Modules.tools import (ReArrangeMacCapaBasedOnModel, deviceconf_device,
                           get_device_nickname, get_deviceconf_parameter_value,
                           getAttributeValue, getListOfEpForCluster, is_hex,
                           is_time_to_perform_work, mainPoweredDevice,
                           night_shift_jobs, removeNwkInList)
from Modules.tuya import tuya_polling
from Modules.tuyaTRV import tuya_switch_online
from Modules.zb_tables_management import mgmt_rtg, mgtm_binding
from Modules.zigateConsts import HEARTBEAT, MAX_LOAD_ZIGATE
from Zigbee.zdpCommands import (zdp_node_descriptor_request,
                                zdp_NWK_address_request)

# Read Attribute trigger: Every 10"
# Configure Reporting trigger: Every 15
# Network Topology start: 15' after plugin start
# Network Energy start: 30' after plugin start
# Legrand re-enforcement: Every 5'


QUIET_AFTER_START = (60 // HEARTBEAT)  # Quiet periode after a plugin start
NETWORK_TOPO_START = (900 // HEARTBEAT)
NETWORK_ENRG_START = (1800 // HEARTBEAT)
READATTRIBUTE_FEQ = (10 // HEARTBEAT)  # 10seconds ...
CONFIGURERPRT_FEQ = (( 30 // HEARTBEAT) + 1)
LEGRAND_FEATURES = (( 300 // HEARTBEAT ) + 3)
SCHNEIDER_FEATURES = (( 300 // HEARTBEAT) + 5)
BINDING_TABLE_REFRESH = (( 3600 // HEARTBEAT ) + 11)
NODE_DESCRIPTOR_REFRESH = (( 3600 // HEARTBEAT) + 13)
ATTRIBUTE_DISCOVERY_REFRESH = (( 3600 // HEARTBEAT ) + 7)
CHECKING_DELAY_READATTRIBUTE = (( 60 // HEARTBEAT ) + 7)
PING_DEVICE_VIA_GROUPID = 3567 // HEARTBEAT    # Secondes ( 59minutes et 45 secondes )
FIRST_PING_VIA_GROUP = 127 // HEARTBEAT


#def attributeDiscovery(self, NwkId):
#
#    rescheduleAction = False
#    # If Attributes not yet discovered, let's do it
#
#    if "ConfigSource" not in self.ListOfDevices[NwkId]:
#        return False
#
#    if self.ListOfDevices[NwkId]["ConfigSource"] == "DeviceConf":
#        return False
#
#    if "Attributes List" in self.ListOfDevices[NwkId] and len(self.ListOfDevices[NwkId]["Attributes List"]) > 0:
#        return False
#
#    if "Attributes List" not in self.ListOfDevices[NwkId]:
#        self.ListOfDevices[NwkId]["Attributes List"] = {'Ep': {}}
#    if "Request" not in self.ListOfDevices[NwkId]["Attributes List"]:
#        self.ListOfDevices[NwkId]["Attributes List"]["Request"] = {}
#
#    for iterEp in list(self.ListOfDevices[NwkId]["Ep"]):
#        if iterEp == "ClusterType":
#            continue
#        if iterEp not in self.ListOfDevices[NwkId]["Attributes List"]["Request"]:
#            self.ListOfDevices[NwkId]["Attributes List"]["Request"][iterEp] = {}
#
#        for iterCluster in list(self.ListOfDevices[NwkId]["Ep"][iterEp]):
#            if iterCluster in ("Type", "ClusterType", "ColorMode"):
#                continue
#            if iterCluster not in self.ListOfDevices[NwkId]["Attributes List"]["Request"][iterEp]:
#                self.ListOfDevices[NwkId]["Attributes List"]["Request"][iterEp][iterCluster] = 0
#
#            if self.ListOfDevices[NwkId]["Attributes List"]["Request"][iterEp][iterCluster] != 0:
#                continue
#
#            if not self.busy and self.ControllerLink.loadTransmit() <= MAX_LOAD_ZIGATE:
#                if int(iterCluster, 16) < 0x0FFF:
#                    getListofAttribute(self, NwkId, iterEp, iterCluster)
#                    # getListofAttributeExtendedInfos(self, NwkId, EpOut, cluster, start_attribute=None, manuf_specific=None, manuf_code=None)
#                elif (
#                    "Manufacturer" in self.ListOfDevices[NwkId]
#                    and len(self.ListOfDevices[NwkId]["Manufacturer"]) == 4
#                    and is_hex(self.ListOfDevices[NwkId]["Manufacturer"])
#                ):
#                    getListofAttribute(
#                        self,
#                        NwkId,
#                        iterEp,
#                        iterCluster,
#                        manuf_specific="01",
#                        manuf_code=self.ListOfDevices[NwkId]["Manufacturer"],
#                    )
#                    # getListofAttributeExtendedInfos(self, NwkId, EpOut, cluster, start_attribute=None, manuf_specific=None, manuf_code=None)
#
#                self.ListOfDevices[NwkId]["Attributes List"]["Request"][iterEp][iterCluster] = time.time()
#
#            else:
#                rescheduleAction = True
#
#    return rescheduleAction

def attributeDiscovery(self, NwkId):
    # If Attributes not yet discovered, let's do it
    if not self.ListOfDevices[NwkId].get("ConfigSource") or \
       self.ListOfDevices[NwkId]["ConfigSource"] == "DeviceConf" or \
       (self.ListOfDevices[NwkId].get("Attributes List") and len(self.ListOfDevices[NwkId]["Attributes List"]) > 0):
        return False

    self.ListOfDevices[NwkId].setdefault("Attributes List", {'Ep': {}})
    self.ListOfDevices[NwkId]["Attributes List"].setdefault("Request", {})

    for iterEp in self.ListOfDevices[NwkId]["Ep"]:
        if iterEp == "ClusterType":
            continue
        self.ListOfDevices[NwkId]["Attributes List"]["Request"].setdefault(iterEp, {})

        for iterCluster in self.ListOfDevices[NwkId]["Ep"][iterEp]:
            if iterCluster in ("Type", "ClusterType", "ColorMode"):
                continue
            if self.ListOfDevices[NwkId]["Attributes List"]["Request"][iterEp].get(iterCluster) != 0:
                continue

            if not self.busy and self.ControllerLink.loadTransmit() <= MAX_LOAD_ZIGATE:
                if int(iterCluster, 16) < 0x0FFF:
                    getListofAttribute(self, NwkId, iterEp, iterCluster)
                elif len(self.ListOfDevices[NwkId].get("Manufacturer", "")) == 4 and is_hex(self.ListOfDevices[NwkId].get("Manufacturer", "")):
                    getListofAttribute(self, NwkId, iterEp, iterCluster, manuf_specific="01", manuf_code=self.ListOfDevices[NwkId]["Manufacturer"])
                self.ListOfDevices[NwkId]["Attributes List"]["Request"][iterEp][iterCluster] = time.time()
            else:
                return True

    return False


def DeviceCustomPolling(self, NwkId, HB):
    # "CustomPolling": {
    #     "EPin": "01",
    #     "EPout": "01",
    #     "Frequency": 60,
    #     "ManufCode": "1234"
    #     "ClusterAttributesList": {
    #         "0702": [ "0000","0100","0102","0104","0106","0108","010a","0400" ],
    #         "0b01": [ "000a", "000c", "000d", "000e" ],
    #         "0b04": [ "0508", "0505" ],
    #     }
    # },
    self.log.logging( "Heartbeat", "Debug", "++ DeviceCustomPolling -  %s " % (NwkId,), NwkId, )

    if self.busy or self.ControllerLink.loadTransmit() > MAX_LOAD_ZIGATE:
        return True

    last_custom_polling = self.ListOfDevices[ NwkId ][ "LastCustomPolling"] if "LastCustomPolling" in self.ListOfDevices[ NwkId ] else None
    self.log.logging( "Heartbeat", "Debug", "++ DeviceCustomPolling -  %s %s %s" % (NwkId, last_custom_polling, HB), NwkId, )
    if last_custom_polling == HB:
        return False
    model_name = self.ListOfDevices[ NwkId ]["Model"] if "Model" in self.ListOfDevices[ NwkId ] else None
    
    if "Param" in self.ListOfDevices[ NwkId ] and "CustomPolling" in self.ListOfDevices[ NwkId ][ "Param" ]:
        custom_polling = self.ListOfDevices[ NwkId ][ "Param" ][ "CustomPolling" ]
        
    elif model_name and model_name in self.DeviceConf and "CustomPolling" in self.DeviceConf[model_name ]:
        custom_polling = self.DeviceConf[model_name ][ "CustomPolling" ]
        
    else:
        return False

    self.log.logging( "Heartbeat", "Debug", "++ DeviceCustomPolling -  %s  %s" % (NwkId,custom_polling), NwkId, )

    EpIn = custom_polling[ "EPin"] if "EPin" in custom_polling else "01"
    EpOut = custom_polling[ "EPout"] if "EPout" in custom_polling else "01"
    
    if "Frequency" not in custom_polling:
        return False
    if "ClusterAttributesList" not in custom_polling:
        return False
    
    frequency = int( custom_polling[ "Frequency" ]) // HEARTBEAT
    self.log.logging( "Heartbeat", "Debug", "++ DeviceCustomPolling -  Frequency: %s %s / %s" % (
        NwkId, frequency , HB ), NwkId, )

    if frequency == 0:  # Disable
        return False
    if (HB % frequency) != 0:
        return False

    self.log.logging( "Heartbeat", "Debug", "++ DeviceCustomPolling -  Poll attributes: %s " % (
        NwkId,), NwkId, )

    self.ListOfDevices[ NwkId ]["LastCustomPolling"] = HB
    self.log.logging( "Heartbeat", "Debug", "++ DeviceCustomPolling -  Ready to poll %s %s" % (
        NwkId, self.ListOfDevices[ NwkId ]["LastCustomPolling"]), NwkId, )

    manuf_specif = "00"
    manuf_code = "0000"
    if "ManufCode" in custom_polling:
        manuf_specif = "01"
        manuf_code = custom_polling[ "ManufCode"]

    for cluster in custom_polling["ClusterAttributesList"]:
        str_attribute_lst = custom_polling["ClusterAttributesList"][ cluster ]
        ListOfAttributes = [int( x, 16) for x in str_attribute_lst]
        self.log.logging( "Heartbeat", "Debug", "++ DeviceCustomPolling -  %s Cluster: %s Attributes: %s Manuf: %s/%s " % (
            NwkId, cluster, str_attribute_lst, manuf_specif, manuf_code ), NwkId, )
        ReadAttributeReq( self, NwkId, EpIn, EpOut, cluster, ListOfAttributes, manufacturer_spec=manuf_specif, manufacturer=manuf_code)

    return False


def ManufSpecOnOffPolling(self, NwkId):
    ReadAttributeRequest_0006_0000(self, NwkId)
    ReadAttributeRequest_0008_0000(self, NwkId)


def tuya_trv5_polling(self, NwkId):
    tuya_switch_online(self, NwkId, 0x01)


def check_delay_readattributes( self, NwkId ):
    
    if 'DelayReadAttributes' not in self.ListOfDevices[ NwkId ]:
        return
    
    if time.time() < self.ListOfDevices[ NwkId ]['DelayReadAttributes']['TargetTime']:
        return
    
    for cluster in list(self.ListOfDevices[ NwkId ]['DelayReadAttributes']['Clusters']):
        if self.busy or self.ControllerLink.loadTransmit() > MAX_LOAD_ZIGATE:
            return
        func = READ_ATTRIBUTES_REQUEST[cluster][0]
        func(self, NwkId)
        self.ListOfDevices[ NwkId ]['DelayReadAttributes']['Clusters'].remove( cluster )
        
    if len(self.ListOfDevices[ NwkId ]['DelayReadAttributes']['Clusters']) == 0:
        del self.ListOfDevices[ NwkId ]['DelayReadAttributes']


def check_delay_binding( self, NwkId, model ):
    # Profalux is the first one, but could get others
    # At pairing we need to leave time for the remote to get binded to the VR
    # Once it is done, then we can overwrite the binding

    if "DelayBindingAtPairing" in self.ListOfDevices[ NwkId ] and self.ListOfDevices[ NwkId ]["DelayBindingAtPairing"] == "Completed":
        self.log.logging( "Heartbeat", "Debug", "check_delay_binding -  %s DelayBindingAtPairing: %s" % (
            NwkId, self.ListOfDevices[ NwkId ]["DelayBindingAtPairing"]), NwkId, )
        return
    
    if model in ( "", {}):
        self.log.logging( "Heartbeat", "Debug", "check_delay_binding -  %s model: %s" % (
            NwkId, model), NwkId, )
        return

    if model not in self.DeviceConf or "DelayBindingAtPairing" not in self.DeviceConf[ model ] or self.DeviceConf[ model ]["DelayBindingAtPairing"] == 0:
        self.log.logging( "Heartbeat", "Debug", "check_delay_binding -  %s not applicable" % (
            NwkId), NwkId, )
        return
    
    if "ClusterToBind" not in self.DeviceConf[ model ] or len(self.DeviceConf[ model ]["ClusterToBind"]) == 0:
        self.log.logging( "Heartbeat", "Debug", "check_delay_binding -  %s Empty ClusterToBind" % (
            NwkId), NwkId, )
        return
    
    # We have a good candidate
    # We reached that step, because we have DelayindingAtPairing enabled and the BindTable is not empty.
    # Let's bind
    if self.configureReporting:
        if "Bind" in self.ListOfDevices[ NwkId ]:
            del self.ListOfDevices[ NwkId ]["Bind"]
            self.ListOfDevices[ NwkId ]["Bind"] = {}
        if STORE_CONFIGURE_REPORTING in self.ListOfDevices[ NwkId ]:
            del self.ListOfDevices[ NwkId ][STORE_CONFIGURE_REPORTING]
            self.ListOfDevices[ NwkId ]["Bind"] = {} 
        self.log.logging( "Heartbeat", "Debug", "check_delay_binding -  %s request Configure Reporting (and so bindings)" % (
            NwkId), NwkId, )
        binding_needed_clusters_with_zigate(self, NwkId)
        self.configureReporting.processConfigureReporting( NwkId=NwkId ) 
        self.ListOfDevices[ NwkId ]["DelayBindingAtPairing"] = "Completed"


def pollingManufSpecificDevices(self, NwkId, HB):

    FUNC_MANUF = {
        "TuyaTRV5Polling": tuya_trv5_polling,
        "OnOffPollingFreq": ManufSpecOnOffPolling,
        "PowerPollingFreq": ReadAttributeRequest_0b04_050b_0505_0508,
        "MeterPollingFreq": ReadAttributeRequest_0702_0000,
        "PC321PollingFreq": ReadAttributeRequest_0702_PC321,
        "AC201Polling": pollingCasaia,
        "TuyaPing": ping_tuya_device,
        "BatteryPollingFreq": ReadAttributeRequest_0001,
        "DanfossRoomFreq": danfoss_room_sensor_polling,
        "TempPollingFreq": ReadAttributeRequest_0402,
        "HumiPollingFreq": ReadAttributeRequest_0405,
        "BattPollingFreq": ReadAttributeRequest_0001,
        "ZLinkyIndexes": ReadAttributeReq_Scheduled_ZLinky,      # Based on a specific time
        "ZLinkyPollingPTEC": ReadAttributeReq_Scheduled_ZLinky,  # Every 15' by default
        "ZLinkyPolling0702": ReadAttributeRequest_0702_ZLinky_TIC,
        "ZLinkyPollingGlobal": ReadAttributeReq_ZLinky,
        "PollingCusterff66": ReadAttributeRequest_ff66,
        "InletTempPolling": ReadAttributeRequest_0702_0017,      # Retreive Inlet Temperature
    }

    if "Param" not in self.ListOfDevices[NwkId]:
        return False

    if self.busy or self.ControllerLink.loadTransmit() > MAX_LOAD_ZIGATE:
        return True

    if "LastPollingManufSpecificDevices" in self.ListOfDevices[ NwkId ] and self.ListOfDevices[ NwkId ][ "LastPollingManufSpecificDevices"] == HB:
        return False

    self.log.logging( "Heartbeat", "Debug", "++ pollingManufSpecificDevices -  %s " % (NwkId,), NwkId, )

    for param in self.ListOfDevices[NwkId]["Param"]:
        if param == "ZLinkyPollingPTEC":
            # We are requesting to execute at a particular time
            _current_time = datetime.datetime.now().strftime("%H:%M" )
            _target_time = self.ListOfDevices[NwkId]["Param"][ param ]
            self.log.logging( "Heartbeat", "Debug", "++ pollingManufSpecificDevices -  %s ScheduledZLinkyRead: Current: %s Target: %s" % (
                NwkId,_current_time, _target_time  ), NwkId, )

            if _current_time == _target_time and "ScheduledZLinkyRead" not in self.ListOfDevices[ NwkId ]:
                self.ListOfDevices[ NwkId ][ "ScheduledZLinkyRead" ] = True
                ReadAttributeReq_Scheduled_ZLinky( self, NwkId)
                ReadAttributeRequest_ff66( self, NwkId)

            elif _current_time != _target_time and "ScheduledZLinkyRead" in self.ListOfDevices[ NwkId ]:
                del self.ListOfDevices[ NwkId ][ "ScheduledZLinkyRead" ]

        elif param in FUNC_MANUF:
            _FEQ = self.ListOfDevices[NwkId]["Param"][param] // HEARTBEAT
            if _FEQ == 0:  # Disable
                continue
            self.log.logging( "Heartbeat", "Debug", "++ pollingManufSpecificDevices -  %s Found: %s=%s HB: %s FEQ: %s Cycle: %s" % (
                NwkId, param, self.ListOfDevices[NwkId]["Param"][param], HB, _FEQ, (HB % _FEQ)), NwkId, )
            if _FEQ and ((HB % _FEQ) != 0):
                continue
            self.log.logging( "Heartbeat", "Debug", "++ pollingManufSpecificDevices -  %s Found: %s=%s" % (
                NwkId, param, self.ListOfDevices[NwkId]["Param"][param]), NwkId, )

            func = FUNC_MANUF[param]
            func(self, NwkId)

    return False


def pollingDeviceStatus(self, NwkId):
    # """
    # Purpose is to trigger ReadAttrbute 0x0006 and 0x0008 on attribute 0x0000 if applicable
    # """

    if self.busy or self.ControllerLink.loadTransmit() > MAX_LOAD_ZIGATE:
        return True
    
    self.log.logging("Heartbeat", "Debug", "--------> pollingDeviceStatus Device %s" % NwkId, NwkId)
    if len(getListOfEpForCluster(self, NwkId, "0006")) != 0:
        ReadAttributeRequest_0006_0000(self, NwkId)
        self.log.logging("Heartbeat", "Debug", "++ pollingDeviceStatus -  %s  for ON/OFF" % (NwkId), NwkId)

    if len(getListOfEpForCluster(self, NwkId, "0008")) != 0:
        ReadAttributeRequest_0008_0000(self, NwkId)
        self.log.logging("Heartbeat", "Debug", "++ pollingDeviceStatus -  %s  for LVLControl" % (NwkId), NwkId)

    if len(getListOfEpForCluster(self, NwkId, "0102")) != 0:
        ReadAttributeRequest_0102_0008(self, NwkId)
        self.log.logging("Heartbeat", "Debug", "++ pollingDeviceStatus -  %s  for WindowCovering" % (NwkId), NwkId)

    if len(getListOfEpForCluster(self, NwkId, "0101")) != 0:
        ReadAttributeRequest_0101_0000(self, NwkId)
        self.log.logging("Heartbeat", "Debug", "++ pollingDeviceStatus -  %s  for DoorLock" % (NwkId), NwkId)

    if len(getListOfEpForCluster(self, NwkId, "0201")) != 0:
        ReadAttributeRequest_0201_0012(self, NwkId)
        self.log.logging("Heartbeat", "Debug", "++ pollingDeviceStatus -  %s  for Thermostat" % (NwkId), NwkId)
    return False


def checkHealth(self, NwkId):

    # Checking current state of the this Nwk
    if "Health" not in self.ListOfDevices[NwkId]:
        self.ListOfDevices[NwkId]["Health"] = ""
        
    if self.ListOfDevices[NwkId]["Health"] == "Disabled":
        return False
                 
    if "Stamp" not in self.ListOfDevices[NwkId]:
        self.ListOfDevices[NwkId]["Stamp"] = {'LastPing': 0, 'LastSeen': 0}
        self.ListOfDevices[NwkId]["Health"] = "unknown"

    if "LastSeen" not in self.ListOfDevices[NwkId]["Stamp"]:
        self.ListOfDevices[NwkId]["Stamp"]["LastSeen"] = 0
        self.ListOfDevices[NwkId]["Health"] = "unknown"

    if (
        int(time.time()) > (self.ListOfDevices[NwkId]["Stamp"]["LastSeen"] + 21200)
        and self.ListOfDevices[NwkId]["Health"] == "Live"
    ):
        if "ZDeviceName" in self.ListOfDevices[NwkId]:
            self.log.logging("Heartbeat", "Debug", "Device Health - %s NwkId: %s,Ieee: %s , Model: %s seems to be out of the network" % (
                self.ListOfDevices[NwkId]["ZDeviceName"], NwkId, self.ListOfDevices[NwkId]["IEEE"], self.ListOfDevices[NwkId]["Model"],))
        else:
            self.log.logging("Heartbeat", "Debug", "Device Health - NwkId: %s,Ieee: %s , Model: %s seems to be out of the network" % (
                NwkId, self.ListOfDevices[NwkId]["IEEE"], self.ListOfDevices[NwkId]["Model"]) )
        self.ListOfDevices[NwkId]["Health"] = "Not seen last 24hours"

    # If device flag as Not Reachable, don't do anything
    return ( "Health" not in self.ListOfDevices[NwkId] or self.ListOfDevices[NwkId]["Health"] != "Not Reachable")


def pingRetryDueToBadHealth(self, NwkId):

    now = int(time.time())
    # device is on Non Reachable state
    self.log.logging("Heartbeat", "Debug", "--------> ping Retry Check %s" % NwkId, NwkId)
    if "pingDeviceRetry" not in self.ListOfDevices[NwkId]:
        self.ListOfDevices[NwkId]["pingDeviceRetry"] = {"Retry": 0, "TimeStamp": now}
    if self.ListOfDevices[NwkId]["pingDeviceRetry"]["Retry"] == 0:
        return

    if "Retry" in self.ListOfDevices[NwkId]["pingDeviceRetry"] and "TimeStamp" not in self.ListOfDevices[NwkId]["pingDeviceRetry"]:
        # This could be due to a previous version without TimeStamp
        self.ListOfDevices[NwkId]["pingDeviceRetry"]["Retry"] = 0
        self.ListOfDevices[NwkId]["pingDeviceRetry"]["TimeStamp"] = now

    lastTimeStamp = self.ListOfDevices[NwkId]["pingDeviceRetry"]["TimeStamp"]
    retry = self.ListOfDevices[NwkId]["pingDeviceRetry"]["Retry"]

    self.log.logging(
        "Heartbeat",
        "Debug",
        "--------> ping Retry Check %s Retry: %s Gap: %s" % (NwkId, retry, now - lastTimeStamp),
        NwkId,
    )
    # Retry #1
    if (
        retry == 0
        and self.ControllerLink.loadTransmit() == 0
        and now > (lastTimeStamp + 30)
    ):  # 30s
        self.log.logging("Heartbeat", "Debug", "--------> ping Retry 1 Check %s" % NwkId, NwkId)
        self.ListOfDevices[NwkId]["pingDeviceRetry"]["Retry"] += 1
        self.ListOfDevices[NwkId]["pingDeviceRetry"]["TimeStamp"] = now
        lookup_ieee = self.ListOfDevices[ NwkId ]['IEEE']
        zdp_NWK_address_request(self, "0000", lookup_ieee)
        submitPing(self, NwkId)
        return

    # Retry #2
    if (
        retry == 1
        and self.ControllerLink.loadTransmit() == 0
        and now > (lastTimeStamp + 120)
    ):  # 30 + 120s
        # Let's retry
        self.log.logging("Heartbeat", "Debug", "--------> ping Retry 2 Check %s" % NwkId, NwkId)
        self.ListOfDevices[NwkId]["pingDeviceRetry"]["Retry"] += 1
        self.ListOfDevices[NwkId]["pingDeviceRetry"]["TimeStamp"] = now
        lookup_ieee = self.ListOfDevices[ NwkId ]['IEEE']
        zdp_NWK_address_request(self, "fffd", lookup_ieee)
        submitPing(self, NwkId)
        return

    # Retry #3
    if (
        retry == 2
        and self.ControllerLink.loadTransmit() == 0
        and now > (lastTimeStamp + 300)
    ):  # 30 + 120 + 300
        # Let's retry
        self.log.logging("Heartbeat", "Debug", "--------> ping Retry 3 (last) Check %s" % NwkId, NwkId)
        self.ListOfDevices[NwkId]["pingDeviceRetry"]["Retry"] += 1
        self.ListOfDevices[NwkId]["pingDeviceRetry"]["TimeStamp"] = now
        lookup_ieee = self.ListOfDevices[ NwkId ]['IEEE']
        zdp_NWK_address_request(self, "FFFD", lookup_ieee)
        submitPing(self, NwkId)


def pingDevices(self, NwkId, health, checkHealthFlag, mainPowerFlag):

    if self.pluginconf.pluginConf["pingViaGroup"]:
        self.log.logging( "Heartbeat", "Debug", "No direct pinDevices as Group ping is enabled" , NwkId, )
        return
    
    if "pingDeviceRetry" in self.ListOfDevices[NwkId]:
        self.log.logging( "Heartbeat", "Debug", "------> pinDevices %s health: %s, checkHealth: %s, mainPower: %s, retry: %s" % (
            NwkId, health, checkHealthFlag, mainPowerFlag, self.ListOfDevices[NwkId]["pingDeviceRetry"]["Retry"]), NwkId, )
    else:
        self.log.logging( "Heartbeat", "Debug", "------> pinDevices %s health: %s, checkHealth: %s, mainPower: %s" % (
            NwkId, health, checkHealthFlag, mainPowerFlag), NwkId, )

    if not mainPowerFlag:
        return

    if (
        "Param" in self.ListOfDevices[NwkId]
        and "TuyaPing" in self.ListOfDevices[NwkId]["Param"]
        and int(self.ListOfDevices[NwkId]["Param"]["TuyaPing"]) == 1
    ):
        self.log.logging(
            "Heartbeat",
            "Debug",
            "------> pingDevice disabled for %s as TuyaPing enabled %s"
            % (
                NwkId,
                self.ListOfDevices[NwkId]["Param"]["TuyaPing"],
            ),
            NwkId,
        )
        return

    if (
        "Param" in self.ListOfDevices[NwkId]
        and "pingBlackListed" in self.ListOfDevices[NwkId]["Param"]
        and int(self.ListOfDevices[NwkId]["Param"]["pingBlackListed"]) == 1
    ):
        self.log.logging(
            "Heartbeat",
            "Debug",
            "------> pingDevice disabled for %s as pingBlackListed enabled %s"
            % (
                NwkId,
                self.ListOfDevices[NwkId]["Param"]["pingBlackListed"],
            ),
            NwkId,
        )
        return

    now = int(time.time())

    if (
        "time" in self.ListOfDevices[NwkId]["Stamp"]
        and now < self.ListOfDevices[NwkId]["Stamp"]["time"] + self.pluginconf.pluginConf["pingDevicesFeq"]
    ):
        # If we have received a message since less than 1 hours, then no ping to be done !
        self.log.logging("Heartbeat", "Debug", "------> %s no need to ping as we received a message recently " % (NwkId,), NwkId)
        return

    if not health:
        pingRetryDueToBadHealth(self, NwkId)
        return

    if "LastPing" not in self.ListOfDevices[NwkId]["Stamp"]:
        self.ListOfDevices[NwkId]["Stamp"]["LastPing"] = 0
    lastPing = self.ListOfDevices[NwkId]["Stamp"]["LastPing"]
    lastSeen = self.ListOfDevices[NwkId]["Stamp"]["LastSeen"]
    if checkHealthFlag and now > (lastPing + 60) and self.ControllerLink.loadTransmit() == 0:
        submitPing(self, NwkId)
        return

    self.log.logging( "Heartbeat", "Debug", "------> pinDevice %s time: %s LastPing: %s LastSeen: %s Freq: %s" % (
        NwkId, now, lastPing, lastSeen, self.pluginconf.pluginConf["pingDevicesFeq"]), NwkId, )
    if (
        (now > (lastPing + self.pluginconf.pluginConf["pingDevicesFeq"]))
        and (now > (lastSeen + self.pluginconf.pluginConf["pingDevicesFeq"]))
        and self.ControllerLink.loadTransmit() == 0
    ):

        self.log.logging( "Heartbeat", "Debug", "------> pinDevice %s time: %s LastPing: %s LastSeen: %s Freq: %s" % (
            NwkId, now, lastPing, lastSeen, self.pluginconf.pluginConf["pingDevicesFeq"]), NwkId, )

        submitPing(self, NwkId)


def submitPing(self, NwkId):
    # Pinging devices to check they are still Alive
    self.log.logging("Heartbeat", "Debug", "------------> call readAttributeRequest %s" % NwkId, NwkId)
    self.ListOfDevices[NwkId]["Stamp"]["LastPing"] = int(time.time())
    ping_device_with_read_attribute(self, NwkId)

def hr_process_device(self, Devices, NwkId):
    # Begin
    # Normalize Hearbeat value if needed

    device_hearbeat = int(self.ListOfDevices.get(NwkId, {}).get("Heartbeat", 0))
    self.ListOfDevices[NwkId]["Heartbeat"] = str(device_hearbeat - 0xFFF0) if device_hearbeat > 0xFFFF else str(device_hearbeat)

    # Hack bad devices
    ReArrangeMacCapaBasedOnModel(self, NwkId, self.ListOfDevices[NwkId]["MacCapa"])

    # Check if this is a Main powered device or Not. Source of information are: MacCapa and PowerSource
    _mainPowered = mainPoweredDevice(self, NwkId)
    _checkHealth = self.ListOfDevices[NwkId]["Health"] == ""
    health = checkHealth(self, NwkId)

    # Pinging devices to check they are still Alive
    if self.pluginconf.pluginConf["pingDevices"]:
        pingDevices(self, NwkId, health, _checkHealth, _mainPowered)

    # Check if we are in the process of provisioning a new device. If so, just stop
    if self.CommiSSionning:
        return

    # If device flag as Not Reachable, don't do anything
    if not health:
        self.log.logging( "Heartbeat", "Debug", "hr_process_device -  %s stop here due to Health %s" % (NwkId, self.ListOfDevices[NwkId]["Health"]), NwkId, )
        return

    # If we reach this step, the device health is Live
    if "pingDeviceRetry" in self.ListOfDevices[NwkId]:
        self.log.logging("Heartbeat", "Log", f"Device {NwkId} '{get_device_nickname(self, NwkId=NwkId)}' recover from Non Reachable", NwkId)
        del self.ListOfDevices[NwkId]["pingDeviceRetry"]

    model = self.ListOfDevices[NwkId].get("Model", "") 
    enabledEndDevicePolling = get_deviceconf_parameter_value(self, model, "PollingEnabled", return_default=False)
    self.log.logging("Heartbeat", "Debug", f"Device {NwkId} Model {model} -> enabledEndDevicePolling {enabledEndDevicePolling}")

    check_param = self.ListOfDevices.get(NwkId, {}).get("CheckParam", False)
    if check_param and self.HeartbeatCount > QUIET_AFTER_START and self.ControllerLink.loadTransmit() < 5:
        sanity_check_of_param(self, NwkId)
        self.ListOfDevices[NwkId]["CheckParam"] = False

    if ( device_hearbeat % CHECKING_DELAY_READATTRIBUTE) == 0:
        check_delay_readattributes( self, NwkId )

    if ( 
        "DelayBindingAtPairing" in self.ListOfDevices[ NwkId ] 
        and isinstance(self.ListOfDevices[ NwkId ]["DelayBindingAtPairing"],int )
        and self.ListOfDevices[ NwkId ]["DelayBindingAtPairing"] > 0
        and time.time() > self.ListOfDevices[ NwkId ]["DelayBindingAtPairing"]
    ):   
        # Will check only after a Command has been sent, in order to limit.
        self.log.logging("Heartbeat", "Debug", "check_delay_binding inHB = %s" %device_hearbeat ) 
        check_delay_binding( self, NwkId, model )

    # Starting this point, it is ony relevant for Main Powered Devices.
    # Some battery based end device with ZigBee 30 use polling and can receive commands.
    # We should authporized them for Polling After Action, in order to get confirmation.
    
    if _mainPowered or enabledEndDevicePolling:
        process_main_powered_or_force_devices( self, NwkId, device_hearbeat, _mainPowered, enabledEndDevicePolling, model)

    
def process_main_powered_or_force_devices(self, NwkId, device_hearbeat, _mainPowered, enabledEndDevicePolling, model):
    self.log.logging("Heartbeat", "Debug",f"Calling process_main_powered_or_force_devices with arguments: NwkId={NwkId}, device_hearbeat={device_hearbeat}, _mainPowered={_mainPowered}, enabledEndDevicePolling={enabledEndDevicePolling}, model={model}", NwkId)

    rescheduleAction = False

    if self.pluginconf.pluginConf["forcePollingAfterAction"] and device_hearbeat == 1:
        self.log.logging("Heartbeat", "Debug", f"process_main_powered_or_force_devices - {NwkId} due to device_hearbeat {device_hearbeat}", NwkId)
        rescheduleAction = rescheduleAction or pollingDeviceStatus(self, NwkId)
        return

    rescheduleAction = ( rescheduleAction or tuya_polling(self, NwkId) )

    rescheduleAction = ( rescheduleAction or DeviceCustomPolling(self, NwkId, device_hearbeat) )

    rescheduleAction = ( rescheduleAction or pollingManufSpecificDevices(self, NwkId, device_hearbeat) )

    _doReadAttribute = (
        (self.pluginconf.pluginConf["enableReadAttributes"] or self.pluginconf.pluginConf["resetReadAttributes"])
        and device_hearbeat != 0
        and (device_hearbeat % READATTRIBUTE_FEQ) == 0
    )

    if should_delay_read_attribute(self, NwkId):
        return

    if _doReadAttribute:
        self.log.logging("Heartbeat", "Debug", f"process_main_powered_or_force_devices - {NwkId} device_hearbeat: {device_hearbeat} _mainPowered: {_mainPowered} doReadAttr: {_doReadAttribute}", NwkId)
        rescheduleAction = rescheduleAction or process_read_attributes(self, NwkId, model)

    if should_reenforce_schneider(self, NwkId):
        rescheduleAction = rescheduleAction or schneiderRenforceent(self, NwkId)

    if self.pluginconf.pluginConf["checkConfigurationReporting"]:
        rescheduleAction = rescheduleAction or check_configuration_reporting(self, NwkId, _mainPowered, device_hearbeat)

    if should_discover_attributes(self, NwkId, _mainPowered, enabledEndDevicePolling, device_hearbeat):
        rescheduleAction = rescheduleAction or attributeDiscovery(self, NwkId)

    if should_refresh_binding_table(self, NwkId, _mainPowered, enabledEndDevicePolling, device_hearbeat):
        mgtm_binding(self, NwkId, "BindingTable")

    if should_request_node_descriptor(self, NwkId, _mainPowered, device_hearbeat):
        rescheduleAction = rescheduleAction or zdp_node_descriptor_request(self, NwkId)

    if not self.busy and self.ControllerLink.loadTransmit() <= MAX_LOAD_ZIGATE:
        add_device_group_for_ping(self, NwkId)

    if rescheduleAction and device_hearbeat != 0:
        decrement_heartbeat(self, NwkId)
    else:
        clear_last_polling_data(self, NwkId)


def should_delay_read_attribute(self, NwkId):
    if (
        self.ControllerLink.loadTransmit() > 5
        and "PairingTime" in self.ListOfDevices[NwkId]
        and time.time() <= (self.ListOfDevices[NwkId]["PairingTime"] + (self.ControllerLink.loadTransmit() // 5) + 15)
    ):
        self.log.logging("Heartbeat", "Debug", f"hr_process_device - {NwkId} delay the next ReadAttribute close to the pairing {self.ListOfDevices[NwkId]['PairingTime']}", NwkId)
        return True
    return False


def should_reenforce_schneider(self, NwkId):
    return self.pluginconf.pluginConf["reenforcementWiser"] and (self.HeartbeatCount % self.pluginconf.pluginConf["reenforcementWiser"]) == 0


def should_discover_attributes(self, NwkId, _mainPowered, enabledEndDevicePolling, device_hearbeat):
    return night_shift_jobs(self) and _mainPowered and not enabledEndDevicePolling and device_hearbeat != 0 and ((device_hearbeat % ATTRIBUTE_DISCOVERY_REFRESH) == 0)


def should_refresh_binding_table(self, NwkId, _mainPowered, enabledEndDevicePolling, device_hearbeat):
    return night_shift_jobs(self) and _mainPowered and not enabledEndDevicePolling and device_hearbeat != 0 and ((device_hearbeat % BINDING_TABLE_REFRESH) == 0)


def should_request_node_descriptor(self, NwkId, _mainPowered, device_hearbeat):
    required_keys = ["Manufacturer", "DeviceType", "LogicalType", "PowerSource", "ReceiveOnIdle", "_rawNodeDescriptor"]
    return (
        night_shift_jobs(self)
        and _mainPowered
        and device_hearbeat != 0
        and (device_hearbeat % NODE_DESCRIPTOR_REFRESH) == 0
        and any(
            key not in self.ListOfDevices.get(NwkId, {})
            for key in required_keys
        )
    )


def decrement_heartbeat(self, NwkId):
    self.ListOfDevices[NwkId]["Heartbeat"] = str(int(self.ListOfDevices[NwkId]["Heartbeat"]) - 1)


def clear_last_polling_data(self, NwkId):
    for key in ["LastPollingManufSpecificDevices", "LastCustomPolling"]:
        self.ListOfDevices[NwkId].pop(key, None)


#def process_read_attributes(self, NwkId, model):
#    self.log.logging( "Heartbeat", "Debug", f"process_read_attributes  -  for {NwkId} {model}")
#    process_next_ep_later = False
#    now = int(time.time())  # Will be used to trigger ReadAttributes
#    
#    device_infos = self.ListOfDevices[NwkId]
#    for ep in device_infos["Ep"]:
#        if ep == "ClusterType":
#            continue
#        
#        if model == "lumi.ctrl_neutral1" and ep != "02" :  # All Eps other than '02' are blacklisted
#            continue
#        
#        if model == "lumi.ctrl_neutral2" and ep not in ("02", "03"):
#            continue
#
#        for Cluster in READ_ATTRIBUTES_REQUEST:
#            # We process ALL available clusters for a particular EndPoint
#
#            if ( Cluster not in READ_ATTRIBUTES_REQUEST or Cluster not in device_infos["Ep"][ep] ):
#                continue
#
#            if self.busy or self.ControllerLink.loadTransmit() > MAX_LOAD_ZIGATE:
#                self.log.logging( "Heartbeat", "Debug", "process_read_attributes  -  %s skip ReadAttribute for now ... system too busy (%s/%s)" % (
#                    NwkId, self.busy, self.ControllerLink.loadTransmit()), NwkId, )
#                process_next_ep_later = True
#
#            if READ_ATTRIBUTES_REQUEST[Cluster][1] in self.pluginconf.pluginConf:
#                timing = self.pluginconf.pluginConf[READ_ATTRIBUTES_REQUEST[Cluster][1]]
#            else:
#                self.log.logging( "Heartbeat", "Error", "proprocess_read_attributescessKnownDevices - missing timing attribute for Cluster: %s - %s" % (
#                    Cluster, READ_ATTRIBUTES_REQUEST[Cluster][1]), NwkId )
#                continue
#
#            # Let's check the timing
#            if not is_time_to_perform_work(self, "ReadAttributes", NwkId, ep, Cluster, now, timing):
#                continue
#
#            self.log.logging( "Heartbeat", "Debug", "process_read_attributes -  %s/%s and time to request ReadAttribute for %s" % (
#                NwkId, ep, Cluster), NwkId, )
#
#            func = READ_ATTRIBUTES_REQUEST[Cluster][0]
#            func(self, NwkId)
#            
#            if process_next_ep_later:
#                return True
#    return False

def process_read_attributes(self, NwkId, model):
    self.log.logging("Heartbeat", "Debug", f"process_read_attributes - for {NwkId} {model}")
    now = int(time.time())
    device_infos = self.ListOfDevices.get(NwkId, {})

    for ep, clusters in device_infos.get("Ep", {}).items():
        if ep == "ClusterType":
            continue
        if model == "lumi.ctrl_neutral1" and ep != "02":
            continue
        if model == "lumi.ctrl_neutral2" and ep not in ("02", "03"):
            continue

        for Cluster in READ_ATTRIBUTES_REQUEST:
            if Cluster not in READ_ATTRIBUTES_REQUEST or Cluster not in clusters:
                continue

            if self.busy or self.ControllerLink.loadTransmit() > MAX_LOAD_ZIGATE:
                self.log.logging("Heartbeat", "Debug", f"process_read_attributes - {NwkId} skip ReadAttribute for now... system too busy ({self.busy}/{self.ControllerLink.loadTransmit()})", NwkId)
                return True

            timing = self.pluginconf.pluginConf.get(READ_ATTRIBUTES_REQUEST[Cluster][1])
            if not timing:
                self.log.logging("Heartbeat", "Error", f"process_read_attributes - missing timing attribute for Cluster: {Cluster} - {READ_ATTRIBUTES_REQUEST[Cluster][1]}", NwkId)
                continue

            if not is_time_to_perform_work(self, "ReadAttributes", NwkId, ep, Cluster, now, timing):
                continue

            self.log.logging("Heartbeat", "Debug", f"process_read_attributes - {NwkId}/{ep} and time to request ReadAttribute for {Cluster}", NwkId)
            READ_ATTRIBUTES_REQUEST[Cluster][0](self, NwkId)
            return True

    return False


def check_configuration_reporting(self, NwkId, _mainPowered, device_hearbeat):
    
    self.log.logging( "ConfigureReporting", "Debug", "check_configuration_reporting for %s %s %s %s %s >%s<" %(
        NwkId, _mainPowered, self.HeartbeatCount, device_hearbeat, self.pluginconf.pluginConf["checkConfigurationReporting"], self.zigbee_communication), NwkId)

    if self.configureReporting is None:
        # Cfg Reporting Object not yet ready
        return

    if self.HeartbeatCount < QUIET_AFTER_START:
        #  leave time at startup
        return

    if "Status" not in self.ListOfDevices[NwkId] or self.ListOfDevices[NwkId]["Status"] != "inDB":
        # Device is not a good state
        return False

    if device_hearbeat != 0 and (device_hearbeat % (60 // HEARTBEAT)) != 0:
        # check only every minute
        return

    if (
        "checkConfigurationReporting" not in self.pluginconf.pluginConf
        or self.pluginconf.pluginConf["checkConfigurationReporting"] == 0
    ):
        # Check if checkConfigurationReporting is enable
        return

    if deviceconf_device(self, NwkId) == {}:
        # Do only for plugin known devices
        return

    if not _mainPowered:
        # Process only with main powered devices
        return

    if not night_shift_jobs( self ):
        # In case we are in a night shift mode, then wait for the nigh window
        return

    if self.busy and self.ControllerLink.loadTransmit() > 3:
        # Only if the load is reasonable
        return True


    if self.zigbee_communication == "zigpy":
        self.log.logging( "ConfigureReporting", "Debug", "check_configuration_reporting for %s %s %s %s %s >%s<" %(
            NwkId, _mainPowered, self.HeartbeatCount, device_hearbeat, self.pluginconf.pluginConf["checkConfigurationReporting"], self.zigbee_communication), NwkId)

        if ( not self.configureReporting.check_configuration_reporting_for_device( NwkId, checking_period=self.pluginconf.pluginConf["checkConfigurationReporting"] )):
            # Nothing trigger, let's check if the configure reporting are correct
            self.configureReporting.check_and_redo_configure_reporting_if_needed( NwkId)

    elif self.zigbee_communication == "native":
        self.log.logging( "ConfigureReporting", "Debug", "Trying Configuration reporting for %s/%s !" %(
            NwkId, get_device_nickname( self, NwkId=NwkId)), NwkId)
        self.configureReporting.processConfigureReporting( NwkId, batch=True )
    return False


def processListOfDevices(self, Devices):
    # Let's check if we do not have a command in TimeOut

    # self.ControllerLink.checkTOwaitFor()
    entriesToBeRemoved = []

    for NwkId in list(self.ListOfDevices.keys()):
        if NwkId in ("ffff", "0000"):
            continue
        
        if NwkId not in self.ListOfDevices:
            continue

        # If this entry is empty, then let's remove it .
        if len(self.ListOfDevices[NwkId]) == 0:
            self.log.logging("Heartbeat", "Debug", "Bad devices detected (empty one), remove it, adr:" + str(NwkId), NwkId)
            entriesToBeRemoved.append(NwkId)
            continue

        if "Param" in self.ListOfDevices[NwkId] and "Disabled" in self.ListOfDevices[NwkId]["Param"]:
            if self.ListOfDevices[NwkId]["Param"]["Disabled"] and self.ListOfDevices[NwkId]["Health"] == "Disabled":
                self.ListOfDevices[NwkId]["CheckParam"] = False
                continue
            
            if not self.ListOfDevices[NwkId]["Param"]["Disabled"] and self.ListOfDevices[NwkId]["Health"] == "Disabled":
                # Looks like it was disabled and it is not any more. 
                # We need to refresh it
                self.ListOfDevices[NwkId]["Health"] = ""
                del self.ListOfDevices[NwkId]["Stamp"]
                self.ListOfDevices[NwkId]["RIA"] = "0"
                
        status = self.ListOfDevices[NwkId]["Status"]
        if self.ListOfDevices[NwkId]["RIA"] not in ( "", {}):
            RIA = int(self.ListOfDevices[NwkId]["RIA"])
        else:
            RIA = 0
            self.ListOfDevices[NwkId]["RIA"] = "0"

        self.ListOfDevices[NwkId]["Heartbeat"] = str(int(self.ListOfDevices[NwkId]["Heartbeat"]) + 1)

        if status == "failDB":
            entriesToBeRemoved.append(NwkId)
            continue

        # Known Devices
        if status == "inDB":
            hr_process_device(self, Devices, NwkId)
            
            # Check and reset if needed Motion, Vibrator and Switch Selector
            check_and_reset_device_if_needed(self, Devices, NwkId)

        elif status == "Leave":
            timedOutDevice(self, Devices, NwkId=NwkId)
            # Device has sentt a 0x8048 message annoucing its departure (Leave)
            # Most likely we should receive a 0x004d, where the device come back with a new short address
            # For now we will display a message in the log every 1'
            # We might have to remove this entry if the device get not reconnected.
            if ((int(self.ListOfDevices[NwkId]["Heartbeat"]) % 36) and int(self.ListOfDevices[NwkId]["Heartbeat"]) != 0) == 0:
                if "ZDeviceName" in self.ListOfDevices[NwkId]:
                    self.log.logging( "Heartbeat", "Debug", "processListOfDevices - Device: %s (%s) is in Status = 'Left' for %s HB" % (
                        self.ListOfDevices[NwkId]["ZDeviceName"], NwkId, self.ListOfDevices[NwkId]["Heartbeat"]), NwkId, )
                else:
                    self.log.logging( "Heartbeat", "Debug", "processListOfDevices - Device: (%s) is in Status = 'Left' for %s HB" % (
                        NwkId, self.ListOfDevices[NwkId]["Heartbeat"]), NwkId, )
                # Let's check if the device still exist in Domoticz
                if not is_device_ieee_in_domoticz_db(self, Devices, self.ListOfDevices[NwkId]["IEEE"]):
                    # Not devices found in Domoticz, so we are safe to remove it from Plugin
                    if self.ListOfDevices[NwkId]["IEEE"] in self.IEEE2NWK:
                        self.log.logging( "Heartbeat", "Status", "processListOfDevices - Removing %s / %s from IEEE2NWK." % (
                            self.ListOfDevices[NwkId]["IEEE"], NwkId) )
                        del self.IEEE2NWK[self.ListOfDevices[NwkId]["IEEE"]]
                    self.log.logging( "Heartbeat", "Status", "processListOfDevices - Removing the entry %s from ListOfDevice" % (NwkId))
                    removeNwkInList(self, NwkId)

        elif status not in ("inDB", "UNKNOW", "erasePDM"):
            # Discovery process 0x004d -> 0x0042 -> 0x8042 -> 0w0045 -> 0x8045 -> 0x0043 -> 0x8043
            processNotinDBDevices(self, Devices, NwkId, status, RIA)
    # end for key in ListOfDevices

    if (
        self.groupmgt 
        and self.pluginconf.pluginConf["pingViaGroup"]
        and (
            self.HeartbeatCount == FIRST_PING_VIA_GROUP        # Let's do a group ping 2 minutes after start
            or (self.HeartbeatCount % PING_DEVICE_VIA_GROUPID ) == 0   # Let's do a group ping every PING_DEVICE_VIA_GROUPID seconds
        )
    ):
        ping_devices_via_group(self)
    
    
    for iterDevToBeRemoved in entriesToBeRemoved:
        if "IEEE" in self.ListOfDevices[iterDevToBeRemoved]:
            del self.ListOfDevices[iterDevToBeRemoved]["IEEE"]
        del self.ListOfDevices[iterDevToBeRemoved]

    if self.CommiSSionning or self.busy:
        self.log.logging( "Heartbeat", "Debug", "Skip LQI, ConfigureReporting and Networkscan du to Busy state: Busy: %s, Enroll: %s" % (
            self.busy, self.CommiSSionning), )
        return  # We don't go further as we are Commissioning a new object and give the prioirty to it

    # Network Topology
    if self.networkmap:
        phase = self.networkmap.NetworkMapPhase()
        self.log.logging("Heartbeat", "Debug", "processListOfDevices checking Topology phase: %s" % phase)
        # if phase == 0:
        #    self.networkmap.start_scan( )
        if phase == 1:
            self.log.logging("Heartbeat", "Status", "Starting Network Topology")
            self.networkmap.start_scan()
        elif phase == 2:
            self.log.logging( "Heartbeat", "Debug", "processListOfDevices Topology scan is possible %s" % self.ControllerLink.loadTransmit(), )
            if self.ControllerLink.loadTransmit() < MAX_LOAD_ZIGATE:
                self.networkmap.continue_scan()

    # if (self.HeartbeatCount > QUIET_AFTER_START) and (self.HeartbeatCount > NETWORK_ENRG_START):
    #    # Network Energy Level
    if self.networkenergy and self.ControllerLink.loadTransmit() <= MAX_LOAD_ZIGATE:
        self.networkenergy.do_scan()

    self.log.logging( "Heartbeat", "Debug", "processListOfDevices END with HB: %s, Busy: %s, Enroll: %s, Load: %s" % (
        self.HeartbeatCount, self.busy, self.CommiSSionning, self.ControllerLink.loadTransmit()), )
    return


def check_and_reset_device_if_needed(self, Devices, NwkId):

    self.log.logging( "Heartbeat", "Debug", "Check for reseting %s" %NwkId)

    now = time.time()
    device_ieee = self.ListOfDevices[NwkId]["IEEE"]
    ClusterTypeList = RetreiveWidgetTypeList(self, Devices, device_ieee, NwkId)
    for WidgetEp, Widget_Idx, WidgetType in ClusterTypeList:
        
        if WidgetType in ( "Motion", "Vibration", SWITCH_SELECTORS):
            device_unit = find_widget_unit_from_WidgetID(self, Devices, Widget_Idx )
            self.log.logging( "Heartbeat", "Debug", "Candidate for reseting %s %s %s %s %s" %(device_ieee, device_unit, NwkId, WidgetType, Widget_Idx))
            reset_device_ieee_unit_if_needed( self, Devices, device_ieee, device_unit, NwkId, WidgetType, Widget_Idx, now)


def add_device_group_for_ping(self, NwkId):

    if self.groupmgt is None or not self.pluginconf.pluginConf["pingViaGroup"]:
        return
    
    if not mainPoweredDevice(self, NwkId):
        return
    
    if self.ListOfDevices[NwkId][ "LogicalType" ] != "Router":
        return
    
    if "Capability" in self.ListOfDevices[NwkId] and "Full-Function Device" not in self.ListOfDevices[NwkId][ "Capability" ]:
        return
    
    target_ep = None
    for ep in self.ListOfDevices[NwkId]["Ep"]:
        if "0004" in self.ListOfDevices[NwkId]["Ep"][ ep ]:
            target_ep = ep

    if target_ep is None:
        return
    
    target_groupid = "%04x" %self.pluginconf.pluginConf["pingViaGroup"]
    if (
        "GroupMemberShip" in self.ListOfDevices[NwkId] 
        and target_groupid in self.ListOfDevices[NwkId][ "GroupMemberShip"][ target_ep ]
    ):
        return
        
    target_ep = None
    for ep in self.ListOfDevices[NwkId]["Ep"]:
        if "0004" in self.ListOfDevices[NwkId]["Ep"][ ep ]:
            target_ep = ep
    
    if target_ep:
        self.groupmgt.addGroupMemberShip(NwkId, target_ep, target_groupid)
