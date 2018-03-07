#!/bin/bash

iptables -A OUTPUT -s 10.0.10.0/24 -j NFQUEUE --queue-num 1
