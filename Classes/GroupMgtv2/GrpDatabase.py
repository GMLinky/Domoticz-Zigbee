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
Methodes which manipulate the Groups Data Structure
- ListOfGroups is the Data structure supporting Groups
  ListOfGroups[group id]['Name']            - Group Name as it will be created in Domoticz
  ListOfGroups[group id]['Devices']         - List of Devices associed to this group on Zigate
  ListOfGroups[group id]['Tradfri Remote']  - Manage the Tradfri Remote
'WidgetStyle'
'Cluster'
'Tradfri Remote'
"Device Addr"]

"""
import json
import os
import time

from Modules.domoticzAbstractLayer import (domoticz_error_api,
                                           domoticz_log_api,
                                           domoticz_status_api, getConfigItem,
                                           setConfigItem)
from Modules.tools import is_domoticz_db_available


def write_groups_list(self):
    """
    write GroupsList into Disk
    """
    self.logging("Debug", "Dumping: %s" % self.GroupListFileName)

    with open(self.GroupListFileName, "wt") as handle:
        json.dump(self.ListOfGroups, handle, sort_keys=True, indent=2)

    if is_domoticz_db_available(self) and self.pluginconf.pluginConf["useDomoticzDatabase"]:
        self.log.logging("Database", "Debug", "Save Plugin Group Db to Domoticz")
        setConfigItem(Key="ListOfGroups", Value={"TimeStamp": time.time(), "b64Groups": self.ListOfGroups})


def load_groups_list_from_json(self):
    """
    Load GroupsList into memory
    """
    if self.GroupListFileName is None:
        return

    if is_domoticz_db_available(self) and self.pluginconf.pluginConf["useDomoticzDatabase"]:
        _domoticz_grouplist = getConfigItem(Key="ListOfGroups")

        dz_timestamp = 0
        if "TimeStamp" in _domoticz_grouplist:
            dz_timestamp = _domoticz_grouplist["TimeStamp"]
            _domoticz_grouplist = _domoticz_grouplist["b64Groups"]
            self.logging(
                "Debug",
                "Groups data loaded where saved on %s"
                % (time.strftime("%A, %Y-%m-%d %H:%M:%S", time.localtime(dz_timestamp))),
            )

        txt_timestamp = 0
        if os.path.isfile(self.GroupListFileName):
            txt_timestamp = os.path.getmtime(self.GroupListFileName)
        domoticz_log_api("%s timestamp is %s" % (self.GroupListFileName, txt_timestamp))
        if dz_timestamp < txt_timestamp:
            domoticz_log_api("Dz Group is older than Json Dz: %s Json: %s" % (dz_timestamp, txt_timestamp))
            # We should load the json file

        if not isinstance(_domoticz_grouplist, dict):
            _domoticz_grouplist = {}

    if not os.path.isfile(self.GroupListFileName):
        self.logging("Debug", "GroupMgt - Nothing to import from %s" % self.GroupListFileName)
        return

    with open(self.GroupListFileName, "rt") as handle:
        self.ListOfGroups = json.load(handle)

    if is_domoticz_db_available(self) and self.pluginconf.pluginConf["useDomoticzDatabase"]:
        domoticz_log_api("GroupList Loaded from Dz: %s from Json: %s" % (len(_domoticz_grouplist), len(self.ListOfGroups)))


def build_group_list_from_list_of_devices(self):
    """ "
    Build the ListOfGroups from the ListOfDevices
    """
    for NwkId in self.ListOfDevices:
        if "GroupMemberShip" not in self.ListOfDevices[NwkId]:
            continue
        for Ep in self.ListOfDevices[NwkId]["GroupMemberShip"]:
            for GrpId in self.ListOfDevices[NwkId]["GroupMemberShip"][Ep]:
                if self.ListOfDevices[NwkId]["GroupMemberShip"][Ep][GrpId]["Status"] == "OK":
                    ieee = self.ListOfDevices[NwkId]["IEEE"]
                    device = [NwkId, Ep, ieee]
                    add_device_to_group(self, device, GrpId)


def update_due_to_nwk_id_change(self, OldNwkId, NewNwkId):
    """
    Short Id of the device has changed, we need to update ListOfGroups accordingly
    """

    # self.logging( 'Debug', "------> update_due_to_nwk_id_change From: %s to %s" %(OldNwkId, NewNwkId))
    for GrpId in list(self.ListOfGroups.keys()):
        for device in list(self.ListOfGroups[GrpId]["Devices"]):
            if device[0] != OldNwkId:
                continue
            # We have to update the NwkId ( update + add )
            newdevice = [NewNwkId, device[1], device[2]]
            self.ListOfGroups[GrpId]["Devices"].remove(device)
            self.ListOfGroups[GrpId]["Devices"].append(newdevice)

        # Check if there is not an Ikea Tradfri Remote to be migrated
        Ikea_update_due_to_nwk_id_change(self, GrpId, OldNwkId, NewNwkId)


def Ikea_update_due_to_nwk_id_change(self, GrpId, OldNwkId, NewNwkId):

    if (
        "Tradfri Remote" in self.ListOfGroups[GrpId]
        and self.ListOfGroups[GrpId]["Tradfri Remote"]["Device Addr"] == OldNwkId
    ):
        self.ListOfGroups[GrpId]["Tradfri Remote"]["Device Addr"] = NewNwkId


def checkNwkIdAndUpdateIfAny(self, NwkId, ieee):
    """
    will return NwkId or an updated one in case of change of ShortId.
    will return None is the NwkId doesn't exist anymore
    """
    if NwkId is self.ListOfDevices:
        return NwkId

    # NwkId not found, let's check if the Ieee is stil there
    if ieee in self.IEEE2NWK:
        NewNwkId = self.IEEE2NWK[ieee]
        update_due_to_nwk_id_change(self, NwkId, NewNwkId)
        return NewNwkId

    # Looks like this Device do not exist. We should then update All Groups where the devices belngs
    remove_nwkid_from_all_groups(self, NwkId)
    return None


def check_if_group_empty(self, GrpId):

    return len(self.ListOfGroups[GrpId]["Devices"]) == 0 and "Tradfri Remote" not in self.ListOfGroups[GrpId]


def create_group(self, GrpId, GrpName):

    if GrpId not in self.ListOfGroups:
        self.ListOfGroups[GrpId] = {}
        self.ListOfGroups[GrpId]["Name"] = GrpName
        self.ListOfGroups[GrpId]["Devices"] = []


def remove_group(self, GrpId):
    if GrpId not in self.ListOfGroups:
        return
    del self.ListOfGroups[GrpId]


def remove_nwkid_from_all_groups(self, NwkIdToRemove):

    for GrpId in list(self.ListOfGroups.keys()):
        for NwkId, Ep, Ieee in list(self.ListOfGroups[GrpId]["Devices"]):
            self.logging(
                "Debug", "remove_nwkid_from_all_groups Looking for NwkId: %s found %s" % (NwkIdToRemove, NwkId)
            )
            if NwkId == NwkIdToRemove:
                self.logging(
                    "Debug", "remove_nwkid_from_all_groups Request removal of [ %s, %s, %s] " % (NwkId, Ep, Ieee)
                )
                remove_device_from_group(self, [NwkId, Ep, Ieee], GrpId)


def add_device_to_group(self, device, GrpId):
    """
    add a device ( NwkId, ep, ieee) to a group
    """
    if GrpId not in self.ListOfGroups:
        self.ListOfGroups[GrpId] = {}
        self.ListOfGroups[GrpId]["Name"] = ""
        self.ListOfGroups[GrpId]["Devices"] = []

    if device not in self.ListOfGroups[GrpId]["Devices"]:
        self.ListOfGroups[GrpId]["Devices"].append(device)


def remove_device_from_group(self, device, GrpId):
    """
    remove a device from a group
    """
    if GrpId not in self.ListOfGroups:
        return
    if device not in self.ListOfGroups[GrpId]["Devices"]:
        return

    self.ListOfGroups[GrpId]["Devices"].remove(device)
    if len(self.ListOfGroups[GrpId]["Devices"]) == 0:
        # No devices attached to that Group.
        remove_group(self, GrpId)


def device_list_for_group(self, GrpId):
    """
    return a list of tuples ( devices, ep, ieee) for a particular group
    """

    if GrpId not in self.ListOfGroups:
        return []
    return self.ListOfGroups[GrpId]["Devices"]
