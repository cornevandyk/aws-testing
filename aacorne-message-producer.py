from __future__ import print_function
import boto3
import json
import random
import string

def snsPublish(topic, subject, message):
    """
    publishes a message to an SNS topic
    :param topic: the SNS topic ARN
    :param subject: subject line
    :param message: message body, should be JSON format
    """

    boto3.setup_default_session(profile_name='default')
    sns = boto3.client('sns')
    print(message)
    response = sns.publish(TopicArn=topic, Subject=subject, Message=json.dumps(message, indent=4))
    print(json.dumps(response, indent=4))


def lambda_handler(event, context):

    topic = "arn:aws:sns:eu-west-1:282415712953:aacorne-alfoffloader"
    subject = "random message to SNS"
    message = {"key": "".join([random.choice(string.ascii_lowercase) for n in xrange(10)])}

    snsPublish(topic, subject, message)

    success = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(message, indent=4)
    }

    return success


lambda_handler("1", "2")