import requests
import shutil

url = 'https://github.com/upx/upx/releases/download/v4.2.1/upx-4.2.1-win64.zip'

r = requests.get(url, allow_redirects=True)

if r.ok:
    print('upx requests ok')

    with open('upx-4.2.1-win64.zip', 'wb') as f:
        f.write(r.content)
        f.close()
    
    print('upx download ok')

    shutil.unpack_archive('upx-4.2.1-win64.zip', '.')
else:
    print("upx requests error")
