from __future__ import print_function
import boto3
import json
import random
import string
import uuid
from datetime import datetime


def sqs_consumer(queue_url, sqs_client):
    """
    SQS receive_message response format
    {
        'Messages': [
            {
                'MessageId': 'string',
                'ReceiptHandle': 'string',
                'MD5OfBody': 'string',
                'Body': 'string',
                'Attributes': {
                    'string': 'string'
                },
                'MD5OfMessageAttributes': 'string',
                'MessageAttributes': {
                    'string': {
                        'StringValue': 'string',
                        'BinaryValue': b'bytes',
                        'StringListValues': [
                            'string',
                        ],
                        'BinaryListValues': [
                            b'bytes',
                        ],
                        'DataType': 'string'
                    }
                }
            },
        ]
    }

    :return:
    """

    print("getting messages now")
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=9
    )

    messages = []
    receipt_handles = []
    # get message bodies
    if "Messages" in response:
        for message in response["Messages"]:
            # need to convert string to JSON format first before extract other bits
            m = json.loads(message["Body"])
            messages.append(m["Message"])
            receipt_handles.append(message["ReceiptHandle"])

    return messages, receipt_handles


def sqs_deleter(queue_url, receipt_handles, sqs_client):

    print("Deleting messages now")

    for handle in receipt_handles:
        print("Deleting message with handle %s" % handle)
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=handle
        )


def write_message_to_s3(messages, bucket):
    """
    """
    # create s3 object
    s3 = boto3.resource('s3')

    # write contents as JSON object
    localfile = '/tmp/writer'
    with open(localfile, 'w') as f:
        json.dump(messages, f)

    # generate object name and write to S3
    print("writing to s3")
    object = "saved_message_%s_%s" % (datetime.utcnow(), uuid.uuid4())
    s3.Bucket(bucket).upload_file(localfile, object)


def lambda_handler(event, context):

    queue_url = "https://sqs.eu-west-1.amazonaws.com/282415712953/aacorne-alfoffloader"
    message = {"key": "".join([random.choice(string.ascii_lowercase) for n in xrange(10)])}

    # boto setup
    boto3.setup_default_session(profile_name='default')
    sqs = boto3.client('sqs')

    # get messages from the queue
    messages, handles = sqs_consumer(queue_url, sqs)
    # only write to S3 and delete if we actually retrieved messages
    if len(messages) > 0:
        write_message_to_s3(messages, "corne-testbucket2")
        sqs_deleter(queue_url, handles, sqs)

    success = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(message, indent=4)
    }

    return success


lambda_handler("1", "2")