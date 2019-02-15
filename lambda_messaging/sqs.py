import boto3
import json

session = boto3.Session(
    profile_name='default',
    region_name='eu-west-1'
)

sqs = boto3.client("sqs")

response = sqs.receive_message(
    QueueUrl="https://sqs.eu-west-1.amazonaws.com/282415712953/aacorne-snssqs",
    AttributeNames=["All"],
    #MessageAttributeNames=["All"],
    MaxNumberOfMessages=10
)

print(json.dumps(response, indent=4))
