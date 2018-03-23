#!/bin/bash

#iptables -D ONEW -o lo -j NFQUEUE --queue-num 1
iptables -D OUTPUT -p tcp -o enp0s3 -j NFQUEUE --queue-num 1
#iptables -D INPUT -p tcp -i enp0s3 -j NFQUEUE --queue-num 1
#iptables -D FORWARD -p tcp -j NFQUEUE --queue-num 1

#iptables -D OUTPUT -m owner --uid-owner tor -j NFQUEUE --queue-num 1
#iptables -D INPUT -m owner --uid-owner tor -j NFQUEUE --queue-num 1
