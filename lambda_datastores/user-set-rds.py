from __future__ import print_function
import sys
import os
import logging
import pymysql
from base64 import b64decode
import boto3
import json

# rds settings
ENCpassword = os.environ['password']
rdshost = os.environ['rdshost']
name = os.environ['name']
dbname = os.environ['dbname']

print ('password is...' + ENCpassword)

# Decrypt code should run once and variables stored outside of the function
# handler so that these are decrypted once per container
DECpassword = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCpassword))['Plaintext']
print ('password is...' + DECpassword)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rdshost, user=name, passwd=DECpassword, db=dbname, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")


def lambda_handler(event, context):

    with conn.cursor() as cur:
        # cur.execute("create table Employee1 ( EmpID  int NOT NULL AUTO_INCREMENT,
        # Name varchar(255) NOT NULL, PRIMARY KEY (EmpID))")
        sqlstatement = "insert into Employee1 (Name) values(\"" + event['queryStringParameters']['name'] + "\")"
        print(sqlstatement)
        cur.execute(sqlstatement)
        conn.commit()
        print("apparently successful insert?")

    response = {"added": str(event['queryStringParameters']['name'])}
    success = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)
    }

    return success
