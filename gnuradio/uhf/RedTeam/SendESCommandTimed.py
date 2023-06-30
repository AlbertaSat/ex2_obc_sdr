#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# File : SendESCommandTimed.py
#
# Purpose : Generate complete EnduroSAT ESTTC commands as selected
#  by the user, place them in a packet as defined in the EnduroSat
#  manual including the CRC16 at the end, and send via UDP to a
#  client application for a specific duration at a specific rate. 
#  For example, the client may be a GNU Radio flowgraph that 
#  modulates the received packet bits and sends the result to a
#  UHD USRP Sink block.
#
# Author : Steven Knudsen
# Date : June 22, 2023
# Copyright : University of Alberta, AlbertaSat, 2023
#
# Requirements : 
#
# InquirerPy - pip3 install InquirerPy
# pycrc      - pip3 install pycrc
#

from __future__ import print_function, unicode_literals
from pprint import pprint
from InquirerPy import prompt, inquirer
from InquirerPy.validator import EmptyInputValidator
from prompt_toolkit.validation import ValidationError, Validator

import binascii
import pycrc.algorithms
import math
from os import system
import socket
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("127.0.0.1", 52001)

clear = lambda: system('clear')

#
# The CRC parameters are selected to match the CRC16 algorithm used by
# EnduroSat, namely 
#
#    CRC-16/CCITT-FALSE
#
#  which has
#    num bits    = 16
#    poly        = 0x1021
#    reflect-in  = false
#    xor-in      = 0xFFFF
#    reflect-out = false
#    xor-out     = 0x0000
#
# The calculated CRC16 can be checked at crccalc.com
#

crc = pycrc.algorithms.Crc(width = 16, poly = 0x1021,
        reflect_in = False, xor_in = 0xFFFF,
        reflect_out = False, xor_out = 0x0000 )

#
# InquirerPy question lists
#
esttc_msg_questions = [
    {
        'type': 'list',
        'name': 'esttc_msg',
        'message': 'What ESTTC command would you like to send?',
        'choices': [
            'Read Status Control Word (SCW)',
            'Enable beacons',
            'Disable beacons',
            'Set beacon period',
            'Get radio uptime',
            'Get radio received packets',
            'Quit',
        ]
    },
]

baud_questions = [
    {
        'type': 'list',
        'name': 'baud',
        'message': 'Select the radio baud rate [sps is bps for 2GFSK]:',
        'choices': [
            str(600),
            str(1200),
            str(2400),
            str(4800),
            str(9600),
            str(19200),
        ]
    },
]

#
# Functions to generate the ASCII ESTTC command strings
#
def readSCW():
    print('Command is Read Status Control Word.')
    readSCWMsg = b"ES+R2200 BD888E1F"+b"\x0D"
    return readSCWMsg

def enableBeacons():
    print('Command is Enable beacons bit in ESTTC Status Control Word and write SCW.')
    ebMsg = b"ES+W22003440 9287EF3A"+b"\0D"
    return ebMsg

def disableBeacons():
    print('Command is Disable beacons bit in ESTTC Status Control Word and wrirte SCW.')
    dbMsg = b"ES+W22003400 F6EB2A3E"+b"\0D"
    return dbMsg

def setBeaconPeriod():
    print('Command is Set beacon period, which is hard-coded to 5 seconds.')
    beaconPeriodMsg = b"ES+W220700000005 AE2A4F6E"+b"\0D"
    return beaconPeriodMsg

def readUptime():
    print('Read radio uptime.')
    uptimeMsg = b"ES+R2202 5386EF33"+b"\0D"
    return uptimeMsg

def readNumReceivedPackets():
    print('Read radio number of received packets.')
    numPacketsMsg = b"ES+R2204 BAE54A06"+b"\0D"
    return numPacketsMsg

#
# Functions to query for program parameters
#
def getTotalTransmissionDuration(minDur=0,maxDur=300):
    txSecs = inquirer.number(
        message="Enter the total number of seconds to transmit packets [0,300]:",
        min_allowed=minDur,
        max_allowed=maxDur,
        validate=EmptyInputValidator(),
    ).execute()
    print('Will transmit for '+txSecs+' seconds.')
    return txSecs

def getTransmissionInterval(minInterval):

    interval_questions = [
        {
            'type': 'list',
            'name': 'interval',
            'message': 'Select the message interval [ms]:',
            'choices': [
                str(minInterval),
                str(minInterval*2),
                str(minInterval*3),
                str(minInterval*4),
                str(minInterval*5),
                str(minInterval*6),
                str(minInterval*7),
                str(minInterval*8),
                str(minInterval*9),
                str(minInterval*10),
            ]
        },
    ]

    intervalResult = prompt(interval_questions)
    txInterval = intervalResult['interval']
    return txInterval

def getPacketTimeInterval(minInt=0.1,maxInt=1):
    print(minInterval)
    print(txDuration)
    intervalSecs= inquirer.number(
        message="Enter the time between packets in seconds["+str(minInt)+","+str(maxInt)+"]:",
        float_allowed = True,
        validate=TimeIntervalValidator(minInt),
    ).execute()
    print('Will transmit every '+intervalSecs+' seconds.')
    return intervalSecs

#
# Make an ESTTC packet for the input command
#
def makeESTTCPacket(command):
    print("Make the ESTTC Packet")
    dataFields = len(command).to_bytes(1, "big")+command
    # Calculate the CRC16 over the Data Field 1 and 2 as per the ES manual
    dataFieldsCRC = crc.bit_by_bit_fast(dataFields)
    print('For '+str(dataFields)+' CRC is {:#04x}'.format(dataFieldsCRC))
    dataFieldsCRC = dataFields + dataFieldsCRC.to_bytes(2,"big")
    preambleSync = "AAAAAAAAAA7E"
    packet = bytes.fromhex(preambleSync)+dataFieldsCRC
    print("The whole packet is : "+str(packet))
    return packet

def main():
    #
    # Get the radio baud rate
    #
    clear()
    baudResult = prompt(baud_questions)
    baudRate = int(baudResult['baud'])

    #
    # Calculate some packet tx/rx times based on slowest baud rate.
    # Need to allow the radio time to receive and response
    #
    maxESPacketBits = (5 + 1 + 1 + 128 + 2) * 8 # based on ES packet definition
    # Need to account for ES radio response time, assume 1.5x as long as packet
    guardBits = math.ceil(1.5*maxESPacketBits)
    minInterval = math.ceil((maxESPacketBits + guardBits) / baudRate * 1000) # milliseconds

    #
    # Get the total duration to send and ESTTC command, the time between
    # commands, and the command
    #
    txDuration = float(getTotalTransmissionDuration())
    txIntervalMillis = float(getTransmissionInterval(minInterval)) 

    clear()
    print("Command will be transmitted every "+str(txIntervalMillis)+" ms for "+str(txDuration)+" s")
    time.sleep(3)
    clear()
    #
    # Now get the ESTTC command string to send
    #
    commandStr = ""
    result = prompt(esttc_msg_questions)
    if result['esttc_msg'] != 'Quit':
        if result['esttc_msg'] == 'Read Status Control Word (SCW)':
            commandStr = readSCW()

        if result['esttc_msg'] == 'Enable beacons':
            commandStr = enableBeacons()

        if result['esttc_msg'] == 'Disable beacons':
            commandStr = disableBeacons()

        if result['esttc_msg'] == 'Set beacon period':
            commandStr = setBeaconPeriod()

        if result['esttc_msg'] == 'Get radio uptime':
            commandStr = readUptime()

        if result['esttc_msg'] == 'Get radio received packets':
            commandStr = readNumReceivedPackets()

        clear()
        print("The command string is : "+str(commandStr))
        thePacket = makeESTTCPacket(commandStr)
        
        txDuration = txDuration * 1000 # Change to milliseconds
        packetCount = 1
        while txDuration > 0:
            txDuration = txDuration - txIntervalMillis;
            print("sending packet "+str(packetCount)+"...")
            client_socket.sendto(thePacket, addr)
            packetCount = packetCount + 1
            time.sleep(txIntervalMillis/1000.0)

    else:
        print("No command will be sent")

if __name__ == "__main__":
    main()