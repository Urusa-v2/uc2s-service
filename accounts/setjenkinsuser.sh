#!/bin/bash

userid=$1
userpassword=${1}"pass"

ssh 10.0.0.249 "/home/ec2-user/cicdjob/jenkinsjob/createuser.sh $userid $userpassword"
