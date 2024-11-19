import requests
import hmac
import hashlib
import time
import http.client
import json 

conn = http.client.HTTPSConnection("api.exchange.coinbase.com")
payload = ''
headers = {
    'Content-Type': 'application/json',
    'cb-access-key': '17c8c2e201e66f2a21f12f1c0db006f2',
    'cb-access-passphrase': 'n3xxjdv2lys',
    'cb-access-sign': '',
    'cb-access-timestamp': '',
}
conn.request("GET", "/accounts", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

# def get_coinbase_accounts(api_key, api_secret):
#     url = 'https://api.exchange.coinbase.com/accounts'
#     timestamp = str(int(time.time()))
#     message = timestamp + 'GET' + '/v2/accounts'
#     signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

#     headers = {
#         'CB-ACCESS-KEY': api_key,
#         'CB-ACCESS-SIGN': signature,
#         'CB-ACCESS-TIMESTAMP': timestamp,
#         'Content-Type': 'application/json',
#         'User-Agent': 'YourAppName/1.0'
#     }

#     response = requests.get(url, headers=headers)
#     return response.json()

# # Example usage

# api_key = '39dbf242-5bca-49d0-ab81-c992c6b353af'
# api_secret = 'MHcCAQEEIEBw2jDOkuD2toeQ328tLQ8/1aaHOcmQqK0Ww8espB0DoAoGCCqGSM49AwEHoUQDQgAEOaThYjf/2to8/J2kMiK2Q4tYu/e4OTyvEKIi1yOqnfa0W2/9KwG2+JZCsRlxJJqqzHyN8227oaQupRmm4aKmoA=='
# accounts = get_coinbase_accounts(api_key, api_secret)
# print(accounts)
