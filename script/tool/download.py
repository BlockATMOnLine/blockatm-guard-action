import requests

def download_file(url : str, file : str):
    print(f"download url = {url}")
    res = requests.get(url, allow_redirects=True)

    if res.ok:
        print('download requests ok')

        with open(file, 'wb') as f:
            f.write(res.content)
            f.close()
        
        print('download save ok')