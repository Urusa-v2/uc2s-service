#!/bin/bash

# shellcheck disable=SC1073
# shellcheck disable=SC1065
# 작업 공간 만들어주는 명령 실행
ssh 10.10.10.12 "/root/jenkinsjob/createworkspace.sh $1 $2"
# 임시
echo($1 $2 $3 $4 $5 $6)