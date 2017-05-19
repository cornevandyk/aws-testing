from __future__ import print_function
import boto3
import json
from StringIO import StringIO

boto3.setup_default_session(profile_name='default')
client = boto3.client('lambda')


def lambda_handler(event, context):
    # TODO implement

    io = StringIO()
    json.dump(event, io)
    print(io.getvalue())

    print("in the try clause now")
    response = client.invoke(
        FunctionName='aacorne-callee',
        InvocationType='Event',
        Payload=json.dumps(event, cls=json.JSONEncoder)
    )

    return 'Hello from XXXX Caller'


event = {"key3": "value3","key2": "value2","key1": "value1"}
lambda_handler(event, "2")