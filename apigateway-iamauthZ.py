"""
curl -X PUT
    --header 'x-api-key: zbd1yDcarlGqysyLMRai8RHB2M0f9qo2tcIH6d89'
    --header 'Content-Type: application/json'
    -d '{
        "Data": {
            "type": "user",
            "name": "corne.vandy",
            "email": "corne.vandy@jumo.world",
        }
    }' 'https://fmkry7g7k7.execute-api.eu-west-1.amazonaws.com/staging'


CanonicalRequest =
  HTTPRequestMethod + '\n' +            # GET
  CanonicalURI + '\n' +                 # /
  CanonicalQueryString + '\n' +         # None
  CanonicalHeaders + '\n' +             #
  SignedHeaders + '\n' +
  HexEncode(Hash(RequestPayload))



Authorization:
    AWS4-HMAC-SHA256 Credential=AKIAIEUAZ2SQPWIVK7UA/20170516/eu-west-1/execute-api/aws4_request,
    SignedHeaders=content-length;content-type;host;x-amz-date;x-api-key,
    Signature=5179514c9b500f66c873cc70654e4bd74483276bf0c4266d308d50cb79707b59

"""
# See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a POST request and passes request parameters
# in the body (payload) of the request. Auth information is passed in
# an Authorization header.
import sys, os, base64, datetime, hashlib, hmac
import json
import requests


# ************* REQUEST VALUES *************
method = 'PUT'
service = 'execute-api'
host = 'fmkry7g7k7.execute-api.eu-west-1.amazonaws.com'
region = 'eu-west-1'
endpoint = "https://fmkry7g7k7.execute-api.eu-west-1.amazonaws.com/staging"
x_api_key = "zbd1yDcarlGqysyLMRai8RHB2M0f9qo2tcIH6d89"

# POST requests use a content type header. For DynamoDB,
# the content is JSON.
content_type = 'application/json'

# Request parameters for CreateTable--passed in a JSON block.
request_parameters = str({
    "Data": {
        "type": "user"
    }
})
content_length = str(len(request_parameters))
print("Content-Length = " + content_length)

# Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def getSignatureKey(key, date_stamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning


# Read AWS access key from env. variables or configuration file. Best practice is NOT
# to embed credentials in code.
access_key = "AKIAIEUAZ2SQPWIVK7UA"
secret_key = "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"

if access_key is None or secret_key is None:
    print('No access key is available.')
    sys.exit()

# Create a date for headers and the credential string
t = datetime.datetime.utcnow()
amz_date = t.strftime('%Y%m%dT%H%M%SZ')
date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope


# ************* TASK 1: CREATE A CANONICAL REQUEST *************
# http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

# Step 1 is to define the verb (GET, POST, etc.)--already done.

# Step 2: Create canonical URI--the part of the URI from domain to query
# string (use '/' if no path)
canonical_uri = '/staging'

## Step 3: Create the canonical query string. In this example, request
# parameters are passed in the body of the request and the query string
# is blank.
canonical_querystring = ''

# Step 4: Create the canonical headers. Header names must be trimmed
# and lowercase, and sorted in code point order from low to high.
# Note that there is a trailing \n.
canonical_headers = 'content-type:' + content_type + '\n' + \
                    'host:' + host + '\n' + \
                    'x-amz-date:' + amz_date + '\n' + \
                    'x-api-key:' + x_api_key + '\n'
                    #'content-length' + content_length + '\n'

# Step 5: Create the list of signed headers. This lists the headers
# in the canonical_headers list, delimited with ";" and in alpha order.
# Note: The request can include any headers; canonical_headers and
# signed_headers include those that you want to be included in the
# hash of the request. "Host" and "x-amz-date" are always required.
# For DynamoDB, content-type and x-amz-target are also required.
signed_headers = 'content-type;host;x-amz-date;x-api-key'
# signed_headers = 'content-type;content-length;host;x-amz-date;x-api-key'

# Step 6: Create payload hash. In this example, the payload (body of
# the request) contains the request parameters.
payload_hash = hashlib.sha256(request_parameters).hexdigest()

# Step 7: Combine elements to create create canonical request
canonical_request = method + '\n' + \
                    canonical_uri + '\n' + \
                    canonical_querystring + '\n' + \
                    canonical_headers + '\n' + \
                    signed_headers + '\n' + \
                    payload_hash


# ************* TASK 2: CREATE THE STRING TO SIGN*************
# Match the algorithm to the hashing algorithm you use, either SHA-1 or
# SHA-256 (recommended)
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request).hexdigest()


# ************* TASK 3: CALCULATE THE SIGNATURE *************
# Create the signing key using the function defined above.
signing_key = getSignatureKey(secret_key, date_stamp, region, service)

# Sign the string_to_sign using the signing_key
signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()


# ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
# Put the signature information in a header named Authorization.
authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

# For DynamoDB, the request can include any headers, but MUST include "host", "x-amz-date",
# "x-amz-target", "content-type", and "Authorization". Except for the authorization
# header, the headers must be included in the canonical_headers and signed_headers values, as
# noted earlier. Order here is not significant.
# # Python note: The 'host' header is added automatically by the Python 'requests' library.
headers = {
    'Content-Type': content_type,
    'X-Amz-Date': amz_date,
    'x-api-key': x_api_key,
    'Authorization': authorization_header
}


# ************* SEND THE REQUEST *************
print '\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++'
print 'Request URL = ' + endpoint

print("data")
print(request_parameters)
print("headers")
print(json.dumps(headers, indent=4))

r = requests.put(endpoint, data=request_parameters, headers=headers)

print '\nRESPONSE++++++++++++++++++++++++++++++++++++'
print 'Response code: %d\n' % r.status_code
print r.text

