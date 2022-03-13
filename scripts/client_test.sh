#!/usr/bin/env bash
curl -X GET 192.168.6.10:5000/
curl -X POST -d 'username=linuxize' http://192.168.6.10:5000/login
curl -X PUT -d password=0000 192.168.6.10:5000/change_password