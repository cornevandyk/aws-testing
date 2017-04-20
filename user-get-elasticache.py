from __future__ import print_function

import json

import elasticache_auto_discovery
from pymemcache.client.hash import HashClient

print('Loading function')

#elasticache settings
elasticache_config_endpoint = "memcache-hello-lego.hemujf.cfg.euw1.cache.amazonaws.com:11211"
nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
nodes = map(lambda x: (x[1], int(x[2])), nodes)
memcache_client = HashClient(nodes)


def lambda_handler(event, context):
    """
    set a value
    :param event:
    :param context:
    :return:
    """

    time_before = context.get_remaining_time_in_millis()
    # insert to memcache
    try:
        quote = memcache_client.get(event['queryStringParameters']['name'])
        #print('elapsed cache time...' + str(time_before - context.get_remaining_time_in_millis()))
    except:
        raise Exception("key doesn't exist")
    time_after = context.get_remaining_time_in_millis()

    response = {}
    response[event['queryStringParameters']['name']] = quote
    response['cache response time...'] = (time_before - time_after)
    success = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)
    }

    return success
