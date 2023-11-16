# -*- coding:utf-8 -*-
import os
import sys
import argparse
import yaml
import shutil
from db.create_db import create_db
from webhook.webhook import webhook_get_data, webhook_push_data
from tool.download import download_url

# python .\script\build.py -f .\pack_windows.yaml
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

    # 獲取前端版本信息
    print('get front version')
    front_version = ''
    app_conf_path_file = os.path.join(app_project_name, 'app', 'conf.yaml')
    with open(app_conf_path_file, encoding = 'utf-8') as f:
        conf : dict = yaml.full_load(f)
        front_version = conf.get('front_version', '')

    if not front_version:
        raise Exception('get front version error!')
    
    print('get front version success')

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
        if not create_db(config_file_path, front_version, key, encrypt_dbname, decrypt_dbname, db_password, True):
            raise Exception("create db error!")
    else:
        if not create_db(config_file_path, front_version, key, encrypt_dbname, decrypt_dbname, db_password, False):
            raise Exception("create db error!")

    print("create db success!")

    print('download app')
    app_url = ''
    app_dir = 'blockatm_guard_app'
    app_zip = 'blockatm_guard_app.zip'

    # 讀取配置，獲取exe下載地址
    # with open(f'{local_dir}/github_conf.yaml', encoding = 'utf-8') as f:
    #     github_conf : dict = yaml.full_load(f)
    # if OSName.OS_WINDOWS == os_name:
    #     app_url = github_conf['app_url']['windows']
    #     download_url(app_url, app_zip)
    # else:
    #     app_url = github_conf['app_url']['mac']
    
    #     cmd_download = f'curl -o {app_zip} {app_url}'
    #     p = execCmd(cmd_download)
    #     print(p)

    shutil.unpack_archive(app_zip, os.path.join(local_dir, '..', app_dir))
    print('download success')

    exe_name = "blockatm-guard"
    if OSName.OS_WINDOWS == os_name:
        
        # 移動文件db
        db_file = os.path.join(local_dir, "..", app_dir, decrypt_dbname)
        force_move(decrypt_dbname, db_file)
        
        # 複製 app 目錄
        src_static = os.path.join(local_dir, "..", app_project_name, "app", "static")
        dec_static = os.path.join(local_dir, "..", app_dir, "static")
        force_copy_tree(src_static, dec_static)

        src_templates = os.path.join(local_dir, "..", app_project_name, "app", "templates")
        dec_templates = os.path.join(local_dir, "..", app_dir, "templates")
        force_copy_tree(src_templates, dec_templates)

        src_resource = os.path.join(local_dir, "..", app_project_name, "app", "resource")
        dec_resource = os.path.join(local_dir, "..", app_dir, "resource")
        force_copy_tree(src_resource, dec_resource)
        
        # 打包
        shutil.make_archive(exe_name, 'zip', app_dir)

    else:
        db_file = os.path.join(local_dir, "..", app_dir, decrypt_dbname)
        force_move(decrypt_dbname, db_file)

        # 複製 app 目錄
        src_static = os.path.join(local_dir, "..", app_project_name, "app", "static")
        dec_static = os.path.join(local_dir, "..", app_dir, "static")
        force_copy_tree(src_static, dec_static)

        src_templates = os.path.join(local_dir, "..", app_project_name, "app", "templates")
        dec_templates = os.path.join(local_dir, "..", app_dir, "templates")
        force_copy_tree(src_templates, dec_templates)

        src_resource = os.path.join(local_dir, "..", app_project_name, "app", "resource")
        dec_resource = os.path.join(local_dir, "..", app_dir, "resource")
        force_copy_tree(src_resource, dec_resource)
        
        # 打包
        shutil.make_archive(exe_name, 'zip', app_dir)

    # 上傳到網盤
    print('upload zip to bashupload.com')
    #push_name = exe_name.replace('-', '_')
    text = execCmd(f'curl https://bashupload.com/blockatmGUD.zip --data-binary @{exe_name}.zip')

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