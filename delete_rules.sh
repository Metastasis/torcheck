#!/bin/bash

#iptables -D OUTPUT -s 10.0.10.0/24 -j NFQUEUE --queue-num 1
iptables -D INPUT -d 10.0.10.0/24 -j NFQUEUE --queue-num 1
#iptables -D FORWARD -s 10.0.10.0/24 -j NFQUEUE --queue-num 1