# ipv4_dscp_test

## Description
ipv4_dscp_test.py is Python script that can be used to send IP packets to a specified destination with an aribtrary DSCP value set.
The purpose is to test the handling of the specified DSCP value by network infrastructure.
A UDP datagram contains a message copmrised of a timestamp when the message was sent and the hostname.
A receiver host must be live on the network.
A receiver daemon is not strictly required, but if one is not invoked, ICMP unreachable messages will be sent by the receiving host.
This script can perform both sending and receiving operations.

There are no explicit or implied guarantees or warranties with this script. See required Python modules below.

## Usage:
The script requires a target host IP specified using the -t switch when originating traffic.
The script may be invoked as a traffic receiver using the -r switch.
Make sure the UDP ports match on both sender and receiver.

The following switches are supported:
- -t [target IP host]
- -d [DSCP value]; default 46
- -p [UDP port]; default 5060
- -c [number of packets to send]; default 5
- -l toggle logging messages to file
- -r invoke script is a UDP listener
- -h help

Note: logging only logs the messages sent/received as a record. Additional logging may be added in the future.

## Required Python Modules:
- argparse
- socket
- struct
- datetime
- time
