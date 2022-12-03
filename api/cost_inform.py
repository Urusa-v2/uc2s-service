# cost_inform

# AWS API 통신 모듈
import boto3
import botocore

# 환율 정보를 위한 웹 크롤링 모듈
import urllib.request as req
import re
from bs4 import BeautifulSoup

# 날짜 계산을 위한 모듈
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


# 요금 조회
def getCost(access_key_set, secret_key_set, region):
    # DB로부터 사용자가 입력한 access key 정보를 쿼리셋으로 받아온다.
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']

        # 사용할 변수 및 리스트에 대한 선언
        sum_cos = 0
        past_day = str(date.today() - relativedelta(months=1))
        to_day = str(date.today() - timedelta(hours=1))
        yester_day = str(date.today() - timedelta(1))

        list_cos = []
        list_date = []

        # 환율 받기
        url = "https://finance.naver.com/marketindex/"
        res = req.urlopen(url)  # 해당 url에 대한 리퀘스트 후 응답을 변수에 저장

        # 응답으로 받은 소스코드를 html.parser 형식으로 데이터를 나눈 후 파이썬 객체로 저장
        soup = BeautifulSoup(res, "html.parser")

        # 태그로 이루어진 HTML 요소들을 python이 이해할 수 있도록 변환
        # 매개변수들은 데이터를 추출할 기준 지정.
        rate = str(soup.select_one("div.head_info > span.value").string)

        # 변수 rate에있는 ","문자열들을 ""으로 치환 하여 f_rate에 저장.
        f_rate = re.sub(",", "", rate)

        # api로 호출할 서비스 이름과 액세스 토큰,리전을 저장
        client = boto3.client(
            'ce',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # 잘못된 액세스 토큰을 입력했을 때를 대비한 try,except
        try:
            # 미리 저장한 인증정보를 바탕으로 원하는 날짜 등 파라미터를
            # boto3 모듈에 전달하여 해당 api 서비스를 리퀘스트.
            # 전달한 요청에 대한 응답을 response 변수에 저장
            response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': past_day,  # yyyy-mm-ddThh:mm:ss
                    'End': to_day
                },
                Granularity='DAILY',  # 'DAILY'|'MONTHLY'|'HOURLY'
                Metrics=['BlendedCost'],
                Filter={
                    'Tags': {
                        'Key': 'eks',
                        'Values': [
                            '',
                        ],
                    }
                }
            )

            # 응답으로 받은 데이터는 딕셔너리 자료형
            # key 값으로 원하는 데이터 추출,
            for i in response['ResultsByTime']:
                # 요금정보가 날짜별로 리스트 형태이므로 for문을 사용하여
                # 리스트를 순회하며 추출
                float_won = i['Total']['BlendedCost']['Amount']
                # api로 받아온 요금은 달러이므로 미리 받아놓은 환율정보를 이용하여 환전
                won = round(float(float_won) * float(f_rate), 2)
                # 환전된 요금과 날짜를 리스트에 저장
                list_cos.append(int(won))
                list_date.append(i['TimePeriod']['Start'])

            # 요금의 총액 산출
            for i in range(0, len(list_cos)):
                sum_cos = sum_cos + list_cos[i]

            result = {'dates': list_date, 'costs': list_cos, 'sum_cos': sum_cos}

            # 가공이 끝난 데이터를 리턴.
            return result

        # 잘못된 액세스 토큰으로 인해 api 호출이 불가능 할 경우 쓰래기값 리턴
        except botocore.exceptions.ClientError as err:

            result = {'dates': ['1001-01-01'], 'costs': ['0', '0', '0']}
            return result



def ec2Cost(access_key_set,secret_key_set,region):
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']

        ec2_sum = 0


        past_day = str(date.today() - relativedelta(months=1))

        to_day = str(date.today() - timedelta(hours=1))

        yester_day = str(date.today() - timedelta(1))

        lists_cos = []

        # 환율 받기
        url = "https://finance.naver.com/marketindex/"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        rate = str(soup.select_one("div.head_info > span.value").string)
        f_rate = re.sub(",", "", rate)

        client = boto3.client(
            'ce',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        try:
            response = client.get_cost_and_usage(
                TimePeriod={
                'Start': past_day,                # yyyy-mm-ddThh:mm:ss
                'End': to_day
                },
                Granularity='DAILY',                   #'DAILY'|'MONTHLY'|'HOURLY'
                Metrics=['BlendedCost'],
                Filter={
                    'Tags': {
                        'Key': 'ec2',
                        'Values': [
                            '',
                            ],
                        }
                    }
                )

            for i in response['ResultsByTime']:
                float_won = i['Total']['BlendedCost']['Amount']
                won = round(float(float_won) * float(f_rate), 2)
                lists_cos.append(int(won))

            for i in range(0,len(lists_cos)):

                ec2_sum = ec2_sum + lists_cos[i]
            result = {'ec2_costs' : lists_cos, 'ec2_sum' : ec2_sum}

            return result
        except botocore.exceptions.ClientError as err:

            result = { 'ec2_costs' : ['0','0','0'] }
            return result