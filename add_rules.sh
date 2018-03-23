#!/bin/bash

iptables -t filter -A OUTPUT -s 10.0.10.0/24 -j NFQUEUE --queue-num 1
#iptables -t mangle -A INPUT -d 10.0.10.0/24 -j NFQUEUE --queue-num 1
#iptables -A FORWARD -s 10.0.10.0/24 -j NFQUEUE --queue-num 1
