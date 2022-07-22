#!/usr/bin/python3

'''
Server program to send accepts commands for the RealAnt
over a Bluetooth socket

Copyright (c) 2022 Matt Stock, Simon D. Levy

MIT License
'''

from optparse import OptionParser
from time import sleep
import socket
import os

from realant import RealAnt

BLUETOOTH_ADDRESS = 'B8:27:EB:75:E6:45'
BLUETOOTH_PORT = 1
MSGSIZE = 1024


def serve_connection(client, ant):

    try:

        data = client.recv(MSGSIZE)

        if data:

            # Convert bytes into angles; then convert out-of-bounds to None
            angles = [a if abs(a) <= 90 else None
                      for a in [int(d)-90 for d in data]]
            print(angles)
            ant.set(angles)

    except ConnectionResetError:
        print('Client disconnected')


def serve_connections(ant):

    with socket.socket(socket.AF_BLUETOOTH,
                       socket.SOCK_STREAM,
                       socket.BTPROTO_RFCOMM) as s:

        s.bind((BLUETOOTH_ADDRESS, BLUETOOTH_PORT))

        s.listen(1)  # support only one client

        print('Waiting for connection...')
        client, address = s.accept()

        print(f'Connection from {address}')

        while True:

            try:
                serve_connection(client, ant)

            except KeyboardInterrupt:
                break


def get_options():

    # Allow user to specify a non-default com port and runtime
    parser = OptionParser()
    parser.add_option('-p', '--commport', dest='commport',
                      help='com port',
                      default='/dev/ttyACM0')
    (opts, _) = parser.parse_args()
    return opts


def main():

    # Wait a bit before starting
    sleep(5)

    # Enable bluetooth
    os.system('sudo hciconfig hci0 piscan')

    # Get command-line options
    opts = get_options()

    # Start the RealAnt
    ant = RealAnt(opts.commport)
    ant.connect()

    # Loop forever, accepting new clients
    while True:

        try:
            serve_connections(ant)

        except KeyboardInterrupt:
            break


main()
