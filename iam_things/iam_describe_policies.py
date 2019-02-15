import boto3
import json
import logging
from datetime import datetime

# set logger object
FORMAT = "%(levelname)s %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DateTimeEncoder(json.JSONEncoder):
    """
    subclass the JSONEncoder, so that it can handle 'datetime.datetime not JSON serializable' errors
    # usage: print json.dumps(objects, indent=4, cls=DateTimeEncoder)
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def get_iam_policies(iam_client):

    policy_list = []

    paginator = iam_client.get_paginator("list_policies")
    for response in paginator.paginate(OnlyAttached=True):
        policy_list += response["Policies"]

    # logger.info(json.dumps(policy_list, indent=4, cls=DateTimeEncoder))

    clean_policy_list = []
    for policy in policy_list:
        clean_policy_list.append(
            {
                "policy_arn": policy["Arn"],
                "policy_version": policy["DefaultVersionId"]
            }
        )

    # logger.info(json.dumps(clean_policy_list, indent=4))

    return clean_policy_list


def describe_policy(iam_client, policy_arn, policy_version):
    logger.info("Policy statement for {} version {}\n{}".format(
        policy_arn,
        policy_version,
        json.dumps(
            iam_client.get_policy_version(
                PolicyArn=policy_arn,
                VersionId=policy_version
            )["PolicyVersion"],
            indent=4,
            cls=DateTimeEncoder
        )
    ))


def main():
    iam_client = boto3.Session(profile_name="prod").client("iam")
    for policy in get_iam_policies(iam_client):
        describe_policy(iam_client, policy["policy_arn"], policy["policy_version"])


if __name__ == "__main__":
    main()

