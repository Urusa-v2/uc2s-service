import boto3
import botocore
from collections import defaultdict
#dsafds
# 클러스터 목록 조회
def getEksCluster(access_key_set,secret_key_set,region):
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']

        client = boto3.client(
            'eks',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        try:
            response = client.list_clusters()
            check = response['clusters']
            if not check:
                errmsg = 'Do not exist any cluster'
                alert = { 'errmsg' : errmsg}
                return alert
            else:
                clusters = {'clusters': response['clusters']}
                print(response['clusters'])
                return clusters
        except botocore.exceptions.ClientError as err:
            cluster = { 'errmsg' : err.response['error']['Message'], 'errcode' : err.response['error']['Code'] }
            return cluster


# 모든 클러스터에 대한 상세정보 조회
def getEksDescription(access_key_set,secret_key_set,region):
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']

        client = boto3.client(
            'eks',  # 서비스 이름
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # cluster 이름 정보 불러오기
        try:
            response_names = client.list_clusters()
            check = response_names['clusters']
            if not check:
                errmsg = 'Do not exist any cluster'
                alert = {'errmsg' : errmsg}
                return alert
            else:
                cluster_dict = defaultdict(list)

                # cluster 이름으로 해당 describe 정보 받기
                for i in response_names['clusters']:
                    response = client.describe_cluster(
                        name=i
                    )
                    cluster_dict['cluster_name'].append(response['cluster']['name'])
                    cluster_dict['end_point'].append(response['cluster']['endpoint'])
                    cluster_dict['ip'].append(response['cluster']['kubernetesNetworkConfig']['serviceIpv4Cidr'])
                    cluster_dict['createdAt'].append(response['cluster']['createdAt'])
                    '''
                    print('#cluster name :', response['cluster']['name'], '#end point :', response['cluster']['endpoint'],
                          '#IP :',
                          response['cluster']['kubernetesNetworkConfig']['serviceIpv4Cidr'])
                    '''
                print(cluster_dict)
                dict_list = zip(cluster_dict['cluster_name'], cluster_dict['end_point'], cluster_dict['ip'],
                                cluster_dict['createdAt'])
                clusters = {'dict_list': dict_list}
                print('dic',dict_list)
                return clusters
        except botocore.exceptions.ClientError as err:
            errcode = err.response['Error']['Code']
            errmsg = err.response['Error']['Message']
            cluster = { 'errmsg' : errmsg, 'errcode' : errcode }
            return cluster
