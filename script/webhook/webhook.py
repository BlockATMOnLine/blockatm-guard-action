import requests
import json
import traceback

def webhook_delete_data(token : str):
    url = f"https://webhook.site/{token}"

    headers = {'content-type': 'application/json'}

    response = requests.delete(url, headers=headers)

    if not response.ok:
        print("delete webhook.sit data error!")
        return

def webhook_get_data(token)->dict:
    try:

        url = f"https://webhook.site/token/{token}/request/latest/raw"

        payload = {}
        headers = {
            'accept': 'application/json',
            'api-key': token
        }

        response = requests.get(url, headers=headers, data=payload)

        if not response.ok:
            print("get webhook.sit data error!")
            print(f"response text = {response.text}")
            return
        
        return response.json()
    
    except Exception as err:
        print('{} :{} '.format(err, str(traceback.format_exc())))
    
    finally:
        webhook_delete_data(token)

def webhook_push_data(token : str, data : dict):
    try:
        url = f"https://webhook.site/{token}"

        payload = json.dumps(data)

        headers = {'content-type': 'application/json'}

        response = requests.post(url, headers=headers, data=payload)

        if not response.ok:
            print("push webhook.sit data error!")
            return
        
        print(response.text)

        return True

    except Exception as err:
        print('{} :{} '.format(err, str(traceback.format_exc())))
