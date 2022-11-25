import boto3
import botocore
import yfinance as yf
import json
from datetime import datetime, timedelta

#pip install yfinance 필수!

#요금 조회
def getCost(access_key_set,secret_key_set,region):
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']


        now = datetime.now()
        past = []
        past.append(str(now.year))
        past.append(str(now.month))
        past.append(str('01'))
        past_day = '-'.join(past)

        today = []
        today.append(str(now.year))
        today.append(str(now.month))
        today.append(str(now.day))
        to_day = '-'.join(today)

        yesterday = []
        yesterday.append(str(now.year))
        yesterday.append(str(now.month))
        yesterday.append(str(now.day - 1))
        yester_day = '-'.join(yesterday)

        list_cos = []
        list_date = []

        end_date = to_day
        data = yf.download(['USDKRW=X'], start=past_day, end=end_date)
        change = data['Close'][yester_day]

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
                        'Key': 'EKS_cluster',
                        'Values': [
                            '',
                            ],
                        }
                    }
                )

            for i in range(1, now.day):
                float_won = response['ResultsByTime'][i - 1]['Total']['BlendedCost']['Amount']
                won = round(float(float_won) * change, 2)
                list_cos.append(int(won))
                list_date.append(response['ResultsByTime'][i - 1]['TimePeriod']['Start'])
            print(list_date)
            result = {'dates' : list_date, 'costs' : list_cos}

            return result
        except botocore.exceptions.ClientError as err:

            result = { 'dates' : ['1001-01-01'], 'costs' : ['0','0','0'] }
            return result