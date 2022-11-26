#!/bin/bash

userid=$1
userpassword=${1}"pass"

ssh 10.10.10.12 "/home/ec2-user/cicdjob/jenkinsjob/createuser.sh $userid $userpassword"