import requests
import base64

from requests.models import Response

authUrl = "https://accounts.spotify.com/api/token"

authHeader = {}
authData = {}

def getAccessToken(clientID, clientSecret):
    message = f"{clientID}:{clientSecret}"
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    authHeader['Authorization'] = "Basic " + base64_message
    authData['grant_type'] = "client_credentials"

    res = requests.post(authUrl, headers=authHeader, data=authData)

    responseObject = res.json()

    accessToken = responseObject['access_token']

    return accessToken