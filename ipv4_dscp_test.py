#!/usr/local/bin/python3

# script: ipv4_dscp_test.py
# author: jason mueller
# created: 2025-02-18
# last modified: 2025-03-05
#
# purpose:
# Script to test basic send data with IP DSCP value set.
# Allows measurement and testing of QoS in networking equipment.
# Messages are sent with a one second interval.
#
# usage:
# python3 ipv4_dscp_test.py -t 10.10.10.10
#     sends 5 IP packets with DSCP priority of 46 with UDP port 5060 to 10.10.10.10
# python3 ipv4_dscp_test.py -t 10.10.10.10 -d 34 -p 5001 -c 10
#     sends 10 IP packets with DSCP priority of 34 with UDP port 5001 to 10.10.10.10
# help: python3 ipv4_dscp_test.py -h
#
# python version: 3.9.6


import argparse
import socket
import struct
import datetime
import time


def get_cli_switches():
    cli_parser = argparse.ArgumentParser(
        description = 'DSCP test script.',
        epilog = '\033[91mNo guarantees. Use at your own risk.\033[0m\n')

    cli_parser.add_argument('-v', '--version',
                            action = 'version',
                            version = '%(prog)s 1.0.3')
    cli_parser.add_argument('-t',
                            dest = 'target',
                            type = str,
                            help = 'set script target/destination IP host. ')
    cli_parser.add_argument('-p',
                            dest = 'port',
                            default = 5060,
                            type = int,
                            help = 'set UDP unprivileged port.')
    cli_parser.add_argument('-c',
                            dest = 'count',
                            default = 5,
                            type = int,
                            help = 'set number of packets to send to destination ' +
                                   '(default is 5).')
    cli_parser.add_argument('-d',
                            dest = 'dscp',
                            default = 46,
                            type = int,
                            help = 'set DSCP priority value (range: 0-63).')
    cli_parser.add_argument('-i',
                            dest = 'interval',
                            default = 1,
                            type = int,
                            help = 'set interim delay betweeen messages (0 = no delay).')
    cli_parser.add_argument('-r',
                            dest = 'receiver',
                            action = 'store_true',
                            help = 'set script to receive data.')
    cli_parser.add_argument('-l',
                            dest = 'log',
                            action='store_true',
                            help = 'log for troubleshooting purposes.')

    cli_args = vars(cli_parser.parse_args())
    return(cli_args)


# is_ipv4_format
# verify supplied string is valid IPv4 address format
#   All IPv4 addresses from 0.0.0.0 through 255.255.255.255 are true
# returns: True or False
# recycled from my net_eng.py module to remove dependency
def is_ipv4_format(candidate):
    is_ipv4 = True            

    try:
        octets = list(map(int, candidate.split('.')))

        # verify IP address contains four components
        if len(octets) != 4:
            is_ipv4 = False

        # verify values are integer versions of binary octets in candidate IP
        else:
            for octet in octets:
                if (octet < 0 or octet > 255):
                    is_ipv4 = False
    except:
        is_ipv4 = False
        
    return is_ipv4


# valid_ipv4_unicast
# verify supplied string is valid IPv4 unicast address
# returns: True or False
# recycled from my net_eng.py to remove dependency
def valid_ipv4_unicast(candidate):
    valid_unicast = True            

    try:
        octets = list(map(int, candidate.split('.')))
        # verify supplied string conforms to IPv4 format

        valid_unicast = is_ipv4_format(candidate)

        # octet value checks
        if valid_unicast:
            # verify first octet is not multicast or experimental (also catches broadcast)
            if (octets[0] > 223):
                valid_unicast = False

            # select reserved address checks follow
            # comment or uncomment as you see fit
            
            # verify not "host on this network"; only valid as source (RFC 1122)
            if octets[0] == 0:
                valid_unicast = False
            
            # verify not loopback (RFC 1122); sometimes used in testing
            #if octets[0] == 127:
            #    valid_unicast = False
            
            # verify not self-assigned IP (RFC 3927)
            if (octets[0] == 169 and octets[1] == 254):
                valid_unicast = False

            # verify not reserved space for IETF protocol assignment (RFC 6890)
            if (octets[0] == 192 and octets[1] == 0 and octets[2] == 0):
                valid_unicast = False                
            
            # verify not automatic multicast tunneling (RFC 7450)
            if (octets[0] == 192 and octets[1] == 52 and octets[2] == 193):
                valid_unicast = False                
            
            # verify not AS 112 DNS redirection (RFC 7535)
            if (octets[0] == 192 and octets[1] == 31 and octets[2] == 196):
                valid_unicast = False                

            # verify not AS 112 DNS service (RFC 7534)
            if (octets[0] == 192 and octets[1] == 175 and octets[2] == 48):
                valid_unicast = False                
            
            # verify not 6to4 relay anycast (RFC 3068)
            if (octets[0] == 192 and octets[1] == 88 and octets[2] == 99):
                valid_unicast = False                
            
    except:
        valid_unicast = False

    return valid_unicast


# is_unpriv_port
# verify supplied integer (or int version of string) corresponds to an unprivileged TCP/UDP port
# returns: True or False
# recycled from my net_eng.py module to remove dependency
def is_unpriv_port(port):
    unpriv_port = True

    try:
        if (int(port) < 1024 or int(port) > 65535):
            unpriv_port = False

    except:
        unpriv_port = False
    
    return unpriv_port


# normalize provided CLI arguments
def santize_args(cli_args):
    args = {}

   # check if script should execute as a UDP traffic receiver
    if cli_args['receiver']:
        args['receiver'] = True
    else:
        args['receiver'] = False

    # verify target IP
    if not valid_ipv4_unicast(cli_args['target']): 
        args['target'] = False
        if (cli_args['target'] == None and args['receiver'] == False):
            print('No target IP address provided.')
        elif args['receiver'] == False:
            print('Invalid target IP address provided:' + cli_args['target'] +  '.')
    else:
        args['target'] = cli_args['target']

    # verify port supplied is valid unprivileged port
    if not is_unpriv_port(cli_args['port']):
        args['port'] = 5060
        print('Port specified was not a valid unprivileged port number, using 5060.')
    else:
        args['port'] = cli_args['port']

    # set repeat count
    try:
        if not int(cli_args['count']) > 0:
            args['count'] = 5
        else:
            args['count'] = cli_args['count']
    except:
        args['count'] = 5
    
    # set interval
    try:
        if not int(cli_args['interval']) > -1:
            args['interval'] = 1
        else:
            args['interval'] = cli_args['interval']
    except:
        args['interval'] = 1

    # set dscp priority
    try:
        if (cli_args['dscp'] >= 0 and cli_args['dscp'] < 65):
            args['dscp'] = cli_args['dscp']
    except:
        args['dscp'] = 46

   # check if logging sent/received messages is set
    if cli_args['log']:
        args['log'] = True
    else:
        args['log'] = False

    return args


# send packets with DSCP set
def send_packets(args):
    try:
        # assign hostname
        try:
            host = socket.gethostname()
        except:
            host = 'hostname_undefined'

        # create logging filehandle
        if args['log']:
            sent_msgs_file = 'dscp_sent_messages.txt'
            sent_fh = open(sent_msgs_file, 'a')

        # create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        # set the DSCP value in the IP header
        # DSCP value in TOS is 6-bits, so 2 bit shirt is required
        tos = args['dscp'] << 2
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, tos)

        # send message to socket
        loopcount = 0
        while loopcount < args['count']:
            msg = str(datetime.datetime.now()) + '; ' + host + '; DSCP: ' \
                + str(args['dscp'])
            sock.sendto(msg.encode('utf-8'), (args['target'], args['port']))
            print('Sent message to {target}:{port}: "{message}."'
                  .format(target=args['target'], port=args['port'], message=msg))
            if args['log']:
                sent_fh.write('{message}\n'
                    .format(message = msg ))
            if args['interval'] > 0:
                time.sleep(args['interval'])
            loopcount += 1

        # Close the socket
        sock.close()
    except:
        print('Failed to send message.')


# receive packets (purpose: avoid ICMP port unreachable response)
def receive_packets(args):
    try:
        # create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', args['port']))

        print('UDP listener for DSCP test invoked at {time}.'
              .format(time=datetime.datetime.now()))
        print('Listening for traffic on UDP port {port}.\n'
              .format(port=args['port']))

        if args['log']:
            rcv_msgs_file = 'udp_rcv_message.txt'
            rcv_fh = open(rcv_msgs_file, 'a')
            print('\nUDP messages written to file: {file}.\n'
                  .format(file=rcv_msgs_file))
    
         # print data received on socket
        while True:
            rcv_msg = sock.recv(1024)
            rcv_time = datetime.datetime.now()
            print('{timestamp}, received UDP message: "{message}"'
                  .format(timestamp=rcv_time, message=str(rcv_msg)[2:-1]))
        
            if args['log']:
                rcv_fh.write('{timestamp}: {message}\n'
                    .format(timestamp = rcv_time, message = str(rcv_msg)[2:-1]))
    
    except:
        if not KeyboardInterrupt:
            print('\nScript exited due to an unexpected error.\n')
            print('Script could not create listener socket.\n')


def march_on_dunsinane():
    cli_args = get_cli_switches()

    args = santize_args(cli_args)

    if cli_args['receiver']:
        receive_packets(args)
    else:
        send_packets(args)        


if __name__ == '__main__':
    march_on_dunsinane()
