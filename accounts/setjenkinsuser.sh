#!/bin/bash
# jenkins 유저를 생성하도록 Jenkins Node 의 유저 생성 shell 파일을 실행하도록 ssh 를 통해 명령을 전달한다
# 이때, userid 와 password 를 회원가입한 userid 를 통해 지정하고, 이를 위치 매개 변수 로 보낸다
userid=$1
userpassword=${1}"pass"

ssh 10.0.0.249 "/home/ec2-user/cicdjob/jenkinsjob/createuser.sh $userid $userpassword"