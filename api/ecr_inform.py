# ecr_inform

# AWS API 통신 모듈
import boto3
import botocore

# 딕셔너리 자료형의 쉬운 사용을 위한 모듈
from collections import defaultdict


# ecr 레포지토리 정보 조회
def getRepoDescription(access_key_set, secret_key_set, region):
    # DB로부터 사용자가 입력한 access key 정보를 쿼리셋으로 받아온다.
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']

        # api로 호출할 서비스 이름과 액세스 토큰,리전을 저장
        client = boto3.client(
            'ecr',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # 잘못된 액세스 토큰을 입력했을 때를 대비한 try,except
        try:
            # 사용자의 모든 레포지토리 리스트를 출력하여 클러스터 이름들을 추출
            response = client.describe_repositories()
            check = response['repositories']

            # 리포지토리 존재하지 않는다면 아래 매세지를 출력
            if not check:
                alert = 'do not exist any repo'
                repos = {'errmsg': alert}
                return repos

            # 리포지토리가 존재한다면 아래 코드를 작동
            else:
                repo_dict = defaultdict(list)

                for res in response['repositories']:
                    repo_dict['repo_name'].append(res['repositoryName'])
                    repo_dict['repo_uri'].append(res['repositoryUri'])
                    repo_dict['created_at'].append(res['createdAt'])

            # 딕셔너리 자료형의 정보들을 zip 함수로 압축
            dict_list = zip(repo_dict['repo_name'], repo_dict['repo_uri'], repo_dict['created_at'])

            # context로 html에 넘겨주기 위해 또다시 딕셔너리 형태로 변환.
            repos = {'dict_list': dict_list}

            return repos

        # 액세스 토큰이 잘못되었을 경우 에러매세지 반환
        except botocore.exceptions.ClientError as err:
            errcode = err.response['Error']['Code']
            errmsg = err.response['Error']['Message']
            repos = {'errmsg': errmsg, 'errcode': errcode}
            return repos

def getRepoName(access_key_set,secret_key_set,region):
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']

        client = boto3.client(
            'ecr',  # 서비스 이름
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        try:
            response = client.describe_repositories()
            check = response['repositories']

            if not check:
                alert = 'do not exist any repo'
                return alert
            else:
                repo_dict = defaultdict(list)
                for res in response['repositories']:
                    repo_dict['repo_name'].append(res['repositoryName'])

                dict_list = zip(repo_dict['repo_name'])
                repos = {'dict_list': dict_list}
                print(repos)
                return repos
        except botocore.exceptions.ClientError as err:
            errcode = err.response['Error']['Code']
            errmsg = err.response['Error']['Message']
            repos = { 'errmsg' : errmsg, 'errcode' : errcode }
            return repos