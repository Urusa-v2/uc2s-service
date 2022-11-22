#!/bin/bash

# shellcheck disable=SC1073
# shellcheck disable=SC1065

# 젠킨스 유저 패스워드 설정
userpassword=${1}"pass"

# cicd 명령 실행
ssh 10.10.10.12 "/root/cicdjob/main.sh $1 $userpassword $2 $3 $4 $5 $6 $7 $8"