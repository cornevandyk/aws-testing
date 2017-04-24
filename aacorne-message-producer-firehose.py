from __future__ import print_function
import boto3
import json

# declare this outside the handler for efficiency
firehose_client = boto3.client('firehose')


def publish_firehose(delivery_stream, record):
    """
    deliver record to the kinesis stream
    :param delivery_stream: name of the kinesis firehose stream
    :param record: record to store, should be in JSON format
    :return: the response received from kinesis
    """

    response = firehose_client.put_record(
        DeliveryStreamName=delivery_stream,
        Record={
            "Data": str(record)
        }
    )
    print(json.dumps(response, indent=4))

    return response


def lambda_handler(event, context):
    """
    lambda handler - entry point for the API Gateway call
    :param event: event includes the submitted data in the "body" key
    :param context: lambda-specific information, not used here
    :return: JSON message to return to API Gateway - returns the RecordID from Kinesis
    """

    # kinesis firehose stream, should be moved to an environment variable
    delivery_stream = "aacorne-alf-offloader"
    # call firehose
    response = publish_firehose(delivery_stream, event["body"])

    # message to return to API Gateway, needs to be in the format below
    # need to add error handling here
    success = {
        "statusCode": response["ResponseMetadata"]["HTTPStatusCode"],
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response["RecordId"], indent=4)
    }

    return success

event = {
    "body": {
        "key": "value"
    }
}

lambda_handler(event, "2")