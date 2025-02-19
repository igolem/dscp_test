# ipv4_dscp_test

## Description
ipv4_dscp_test.py is Python script that can be used to send IP packets to a specified destination with an aribtrary DSCP value set.
The purpose is to test the handling of the specified DSCP value by network infrastructure.
A UDP datagram contains a message copmrised of a timestamp when the message was sent and the hostname.
A receiver daemon is not strictly required. I will add a receiver function to the script in the future.

There are no explicit or implied guarantees or warranties with this script. See required Python modules below.

## Usage:
The switch requires a target host IP specified using the -t switch.

The following switches are supported:
- -t [target IP host]
- -d [DSCP value]; default 46
- -p [UDP port]; default 5060
- -c [number of packets to send]; default 5
- -l toggle logging messages (sent/received) to file
- -h help
- -l log

Note: logging only logs the messages sent as a record. Additional logging may be added in the future.

## Required Python Modules:
- argparse
- socket
- struct
- datetime
- time
