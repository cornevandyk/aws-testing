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


# Decrypt code should run once and variables stored outside of the function
# handler so that these are decrypted once per container
DECpassword = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCpassword))['Plaintext']
print('password is...' + DECpassword)

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
        # Read a single record
        sqlstatement = "SELECT MAX(EmpID), Name FROM Employee1"
        cur.execute(sqlstatement)
        result = cur.fetchone()
        #print(result)

    success = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": str(result)
    }

    return success
