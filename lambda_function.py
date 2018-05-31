import boto3
from portland import scan

PHONE_NUMBER = ""
LATITUDE = 0.0
LONGITUDE = 0.0


def lambda_handler(event, context):
    client = boto3.client('sns')
    lat_lng = (LATITUDE, LONGITUDE)
    incidents = scan(seconds=3600, miles=1.0, lat_lng=lat_lng)
    for incident in incidents:
        client.publish(PhoneNumber=PHONE_NUMBER, Message=incident)
