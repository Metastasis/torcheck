#!/bin/bash

#sudo iptables -D ONEW -o lo -j NFQUEUE --queue-num 1
sudo iptables -A OUTPUT -p tcp -s 10.0.10.0/24 -j NFQUEUE --queue-num 1
#sudo iptables -D INPUT -p tcp -i enp0s3 -j NFQUEUE --queue-num 1
#sudo iptables -D FORWARD -p tcp -j NFQUEUE --queue-num 1
#sudo iptables -D OUTPUT -m owner --uid-owner tor -j NFQUEUE --queue-num 1
#sudo iptables -D INPUT -m owner --uid-owner tor -j NFQUEUE --queue-num 1
