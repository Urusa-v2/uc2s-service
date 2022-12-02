import boto3
import botocore
import urllib.request as req
import re
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup


#요금 조회
def getCost(access_key_set,secret_key_set,region):
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']

        sum_cos = 0


        '''
        past = []
        past.append(str(now.year))
        past.append(str(now.month))
        past.append(str('01'))
        past_day = '-'.join(past)
        '''

        past_day = str(date.today() - relativedelta(months=1))

        to_day = str(date.today() - timedelta(hours=1))

        yester_day = str(date.today() - timedelta(1))

        list_cos = []
        list_date = []

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
                        'Key': 'eks',
                        'Values': [
                            '',
                            ],
                        }
                    }
                )

            for i in response['ResultsByTime']:
                float_won = i['Total']['BlendedCost']['Amount']
                won = round(float(float_won) * float(f_rate), 2)
                list_cos.append(int(won))
                list_date.append(i['TimePeriod']['Start'])

            for i in range(0,len(list_cos)):
                sum_cos = sum_cos + list_cos[i]

            print(sum_cos)

            result = {'dates' : list_date, 'costs' : list_cos, 'sum_cos' : sum_cos }

            return result
        except botocore.exceptions.ClientError as err:

            result = { 'dates' : ['1001-01-01'], 'costs' : ['0','0','0'] }
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