import boto3

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

        response = client.list_clusters()
        context = {'clusters': response['clusters']}
        print(response['clusters'])
        return context

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
        response_names = client.list_clusters()

        # cluster 이름으로 해당 describe 정보 받기
        for i in response_names['clusters']:
            response = client.describe_cluster(
                name=i
            )

        context = {'cluster_name': response['cluster']['name'],
                   'end_point': response['cluster']['endpoint'],
                   'ip': response['cluster']['kubernetesNetworkConfig']['serviceIpv4Cidr']}
        print('#cluster name :', response['cluster']['name'], '#end point :', response['cluster']['endpoint'], '#IP :',
              response['cluster']['kubernetesNetworkConfig']['serviceIpv4Cidr'])
        return context

