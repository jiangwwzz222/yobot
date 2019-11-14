import requests


def shorten(url: str) -> str:
    shorten_api = 'http://io.yobot.monster/go/yourls-api.php'
    data = {
        'signature': 'b7b55a841d',
        'action': 'shorturl',
        'url': url,
        'format': 'simple'
    }
    resp = requests.post(shorten_api, data=data)
    if resp.status_code == 200:
        url = resp.text
    return url
