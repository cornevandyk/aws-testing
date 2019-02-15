import boto3
import json
import uuid
import time

session = boto3.Session(
    profile_name='default',
    region_name='eu-west-1'
)

sns = boto3.client("sns")
sqs = boto3.client("sqs")

count = 0
while True:
    count += 1
    response = sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:282415712953:aacorne-snssqs',
        Message='some random message body {}'.format(count),
        Subject='some random subject {}'.format(count),
        #MessageStructure='string',
        MessageAttributes={
            'randomId': {
                'DataType': 'String',
                'StringValue': uuid.uuid4().hex
            }
        }
    )
    print(json.dumps(response, indent=4))

    response = sqs.send_message(
        QueueUrl='https://sqs.eu-west-1.amazonaws.com/282415712953/aacorne-snssqs',
        MessageBody='bla',
        DelaySeconds=0,
        MessageAttributes={
            'someattrib': {
                'StringValue': 'string',
                'DataType': 'String'
            }
        }
    )
    print(json.dumps(response, indent=4))



    time.sleep(2)


