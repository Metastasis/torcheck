#!/bin/bash

#iptables -A ONEW -o lo -j NFQUEUE --queue-num 1
iptables -A OUTPUT -p tcp -o enp0s3 -j NFQUEUE --queue-num 1
#iptables -A INPUT -p tcp -i enp0s3 -j NFQUEUE --queue-num 1
#iptables -A FORWARD -p tcp -j NFQUEUE --queue-num 1

#iptables -A OUTPUT -m owner --uid-owner tor -j NFQUEUE --queue-num 1
#iptables -A INPUT -m owner --uid-owner tor -j NFQUEUE --queue-num 1
