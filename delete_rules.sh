#!/bin/bash

iptables -D INPUT -d 10.0.2.0/24 -j NFQUEUE --queue-num 1