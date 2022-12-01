import boto3
import botocore
from collections import defaultdict
# 모든 레포지토리에 대한 상세정보 조회
def getRepoDescription(access_key_set,secret_key_set,region):
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
                repos = {'errmsg' : alert}
                return repos
            else:
                repo_dict = defaultdict(list)
                for res in response['repositories']:
                    repo_dict['repo_name'].append(res['repositoryName'])
                    repo_dict['repo_uri'].append(res['repositoryUri'])
                    repo_dict['created_at'].append(res['createdAt'])

                dict_list = zip(repo_dict['repo_name'], repo_dict['repo_uri'], repo_dict['created_at'] )
                repos = {'dict_list': dict_list}
                print(repos)
                return repos

        except botocore.exceptions.ClientError as err:
            errcode = err.response['Error']['Code']
            errmsg = err.response['Error']['Message']
            repos = { 'errmsg' : errmsg, 'errcode' : errcode }
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