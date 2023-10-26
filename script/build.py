# -*- coding:utf-8 -*-
import os
import sys
import argparse
import uuid
import traceback
import yaml
import shutil
import requests
import zipfile
from pypi_sqlite_cipher.pysqlite_cipher import get_exe_file
from db.create_db import create_db
from webhook.webhook import webhook_get_data, webhook_push_data

# python .\py\build_init.py -f .\pack_windows.yaml
def execCmd(cmd):  
    r = os.popen(cmd)  
    text = r.read()  
    r.close()  
    return text

def force_copy_file(src, des):
    if os.path.exists(des):
        os.remove(des)
    shutil.copyfile(src, des)

def force_copy_tree(src, des):
    if os.path.exists(des):
        shutil.rmtree(des)
    shutil.copytree(src, des)

def force_rename_tree(old, news):
    if os.path.exists(news):
        shutil.rmtree(news)
    os.rename(old, news)

def force_move(src, des):
    if os.path.exists(des):
        os.remove(des)
    shutil.move(src, des)

def force_remove(src):
    if os.path.exists(src):
        os.remove(src)

class OSName():
    OS_WINDOWS = "Windows"
    OS_MAC = "Darwin"

def main(file : str):
    app_project_name = 'blockatm-guard'

    # print('Install python environment!')
    # os.system(f"python3 -m pip install -r {app_project_name}/requirements.txt")

    # 讀取 pack_windows.yaml(pack_mac.yaml)
    print(file)
    
    os_name = OSName.OS_WINDOWS
    if 'mac' in file:
        os_name = OSName.OS_MAC
    print(f'os_name = {os_name}')

    # 讀取 ack_windows.yaml(pack_mac.yaml) 數據
    with open(file, encoding = 'utf-8') as f:
        pack_yaml : dict = yaml.full_load(f)
    
    print(pack_yaml)

    config_id = pack_yaml['config_file']
    webhook_token = pack_yaml['webhook']

    print(f'config_id = {config_id}')
    print(f'webhook_token = {webhook_token}')

    # 獲取 webhook.sit 中的 key 數據
    print('webhook get data')
    data = webhook_get_data(webhook_token)
    if not data or not isinstance(data, dict):
        raise Exception('webhook get data error!')
    key = data.get('key', '')
    if not key:
        raise Exception('webhook get key error!')
    
    print('webhook get key success')

    # 創建 db
    local_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(local_dir, "..", "configurations", f"{config_id}.yaml")
    
    encrypt_dbname = 'agentapp_encrypt.db'
    decrypt_dbname = 'agentapp_decrypt.db'

    force_remove(encrypt_dbname)
    force_remove(decrypt_dbname)

    print("create db!")
    db_password = key
    #db_password = '123456'
    #print(f'db_password = {db_password}')
    if OSName.OS_WINDOWS == os_name:
        if not create_db(config_file_path, key, encrypt_dbname, decrypt_dbname, db_password, True):
            raise Exception("create db error!")
    else:
        if not create_db(config_file_path, key, encrypt_dbname, decrypt_dbname, db_password, False):
            raise Exception("create db error!")

    print("create db success!")

    print('create config file')
    # 創建py文件
    with open('config.py', 'w') as f:
        f.writelines(f"DB_PASSWORD = '{db_password}'\r\n")
        f.writelines(f"VERSION_TYPE = 'RELEASE'")
    
    print('create config file success')
    
    # 移動文件config.py
    config_file = os.path.join(local_dir, "..", app_project_name, "app", "core", "config.py")
    force_move("config.py", config_file)

    print('pack app')
    # 打包
    exe_name = "blockatm-guard"
    if OSName.OS_WINDOWS == os_name:
        cmd = f'pyinstaller -F -w -i ./{app_project_name}/app/resource/favicon.ico -n {exe_name} ./{app_project_name}/app/main.py'
    else:
        cmd = f'pyinstaller -F -w -n {exe_name} ./{app_project_name}/app/main.py'
    os.system(cmd)

    print('pack app success')

    if OSName.OS_WINDOWS == os_name:
        
        # 移動文件db
        db_file = os.path.join(local_dir, "..", "dist", encrypt_dbname)
        force_move(encrypt_dbname, db_file)
        
        # 移動sqlcipher-shell64.exe文件
        sqlite_exe_file = os.path.join(local_dir, "..", "dist", "sqlcipher-shell64.exe")
        force_copy_file(get_exe_file(), sqlite_exe_file)

        # 複製 app 目錄
        src_static = os.path.join(local_dir, "..", app_project_name, "app", "static")
        dec_static = os.path.join(local_dir, "..", "dist", "static")
        force_copy_tree(src_static, dec_static)

        src_templates = os.path.join(local_dir, "..", app_project_name, "app", "templates")
        dec_templates = os.path.join(local_dir, "..", "dist", "templates")
        force_copy_tree(src_templates, dec_templates)

        src_resource = os.path.join(local_dir, "..", app_project_name, "app", "resource")
        dec_resource = os.path.join(local_dir, "..", "dist", "resource")
        force_copy_tree(src_resource, dec_resource)
        
        # 打包
        shutil.make_archive(exe_name, 'zip', f'dist')

    else:
        db_file = os.path.join(local_dir, "..", "dist", decrypt_dbname)
        force_move(decrypt_dbname, db_file)

        # 複製 app 目錄
        src_static = os.path.join(local_dir, "..", app_project_name, "app", "static")
        dec_static = os.path.join(local_dir, "..", "dist", "static")
        force_copy_tree(src_static, dec_static)

        src_templates = os.path.join(local_dir, "..", app_project_name, "app", "templates")
        dec_templates = os.path.join(local_dir, "..", "dist", "templates")
        force_copy_tree(src_templates, dec_templates)

        src_resource = os.path.join(local_dir, "..", app_project_name, "app", "resource")
        dec_resource = os.path.join(local_dir, "..", "dist", "resource")
        force_copy_tree(src_resource, dec_resource)
        
        # 打包
        shutil.make_archive(exe_name, 'zip', f'dist')

    # 上傳到網盤
    print('upload zip to bashupload.com')
    push_name = exe_name.replace('-', '_')
    text = execCmd(f'curl https://bashupload.com/{push_name}.zip --data-binary @{exe_name}.zip')

    if not text:
        raise Exception('upload zip to bashupload.com fail')
    
    print('upload zip to bashupload.com success')
    
    download_url = text.split('\n')[5].split(' ')[1]

    print(f'download url is:{download_url}')

    # 將 download url推送到webhook.sit
    print('push download url to webhook')
    if not webhook_push_data(webhook_token, {"download_url":download_url}):
        raise Exception('push download url to webhook fail')
    
    print('push download url to webhook success')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-f", "--file", required=True, help="pack_windows.yaml file path")
    known_args = parser.parse_args()

    sys.exit(main(known_args.file))