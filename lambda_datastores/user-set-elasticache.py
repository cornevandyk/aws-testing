from __future__ import print_function

import json
import random

import elasticache_auto_discovery
from pymemcache.client.hash import HashClient

print('Loading function')

# lasticache settings
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
    # quotes list to pick randomly from
    quotes = [
        'Introducing the double-decker couch! So everyone can watch TV together and be buddies!',
        'Come with me if you want to not die.',
        'I hope there\'s still a good cop in me somewhere.',
        ' We\'re going to crash into the sun!',
        ' This is not how Batman dies!',
        'Stay... positive......stay.........ah, forget it! DIIIIIIIIIE!!!!!',
        'I only use black.. and sometimes dark shades of gray.',
        'He\'s coming, cover your butt.']

    # key-value pair to insert later
    key = event['queryStringParameters']['name']
    value = quotes[random.randint(0,7)]
    print(key)
    print(value)

    # insert to memcache
    time_before = context.get_remaining_time_in_millis()
    try:
        memcache_client.set(key, value)
        print('apparently successful with memcache setting')
        #print('elapsed cache set time...' + str(time_before - time_after))
    except:
        print('memcache failed for some reason')
    time_after = context.get_remaining_time_in_millis()

    response = {}
    response[key] = value
    response['cache response time...'] = (time_before - time_after)
    success = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)
    }

    return success
