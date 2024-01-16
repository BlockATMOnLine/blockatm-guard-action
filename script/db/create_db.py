# -*- coding:utf-8 -*-
import os
import json
import sys
import time
import yaml
import argparse
import sqlite3
import traceback
from .acs import aesdecrypt
from .sqlcrypt import Connection


def create_db(file : str, app_conf : dict, aes_key : str, encrypt_dbname : str, decrypt_dbname : str, password : str, need_encrypt : bool):
    try:

        front_version = app_conf.get('front_version')
        update_conf_url = app_conf.get('update_conf_url')
        network_info = app_conf.get('network_info')
        network_info_str = json.dumps(network_info)

        print(f'network_info = {network_info}')

        print(f'need_encrypt = {need_encrypt}')
        
        (path, filename) = os.path.split(file)
        
        # 讀取yaml
        with open(file, encoding = 'utf-8') as f:
            data = f.read()
            decrypt_data = aesdecrypt(aes_key, data)
            conf = yaml.safe_load(decrypt_data)
        conf_str = json.dumps(conf)

        
        print(f'conf_str = {conf_str}')
        
        # 連接db
        # conn = sqlite3.connect(decrypt_dbname)
        conn = Connection(encrypt_dbname, password)

        # 建表
        conn.execute('''CREATE TABLE agent_order
                    (
                    order_no VARCHAR(128) PRIMARY KEY,
                    order_date INTEGER   NOT NULL,
                    import_date INTEGER   NOT NULL,
                    crypto VARCHAR(64)   NOT NULL,
                    chainid VARCHAR(128) NOT NULL,
                    network VARCHAR(128) NOT NULL,
                    wallet_address VARCHAR(128) NOT NULL,
                    amount VARCHAR(64)  NOT NULL,
                    uid VARCHAR(128) NOT NULL,
                    biz_name VARCHAR(128) NOT NULL,
                    status INTEGER NOT NULL,
                    txid VARCHAR(128),
                    is_del INTEGER
                    );''')
        
        conn.execute('''CREATE TABLE agent_history_order
                    (
                    order_no VARCHAR(128) PRIMARY KEY,
                    order_date INTEGER   NOT NULL,
                    import_date INTEGER   NOT NULL,
                    finish_date INTEGER   NOT NULL,
                    crypto VARCHAR(64)   NOT NULL,
                    chainid VARCHAR(128) NOT NULL,
                    network VARCHAR(128) NOT NULL,
                    wallet_address VARCHAR(128) NOT NULL,
                    amount VARCHAR(64)  NOT NULL,
                    uid VARCHAR(128) NOT NULL,
                    biz_name VARCHAR(128) NOT NULL,
                    txid VARCHAR(128)  NOT NULL
                    );''')

        conn.execute('''CREATE TABLE agent_login_log
                    (
                    token VARCHAR(128) PRIMARY KEY,
                    login_time INTEGER NOT NULL,
                    logout_time INTEGER NOT NULL,
                    wallet_address VARCHAR(128)    NOT NULL,
                    mac VARCHAR(128)   NOT NULL
                    );''')

        conn.execute('''CREATE TABLE agent_operate_log
                    (
                    login_time INTEGER NOT NULL,
                    wallet_address VARCHAR(128)   NOT NULL,
                    error_type VARCHAR(256) NOT NULL
                    );''')

        conn.execute('''CREATE TABLE agent_config
                    (
                    yaml_file VARCHAR(256) NOT NULL,
                    config JSON NOT NULL,
                    update_time int NOT NULL,
                    aes_key VARCHAR(256) NOT NULL,
                    front_version VARCHAR(32) NOT NULL,
                    update_conf_url VARCHAR(256) NOT NULL,
                    network_info VARCHAR(1024) NOT NULL
                    );''')

        # 插入配置
        update_time = int(time.time())
        sql = f"INSERT INTO agent_config(yaml_file, config, update_time, aes_key, front_version, update_conf_url, network_info) VALUES ('{filename}', '{conf_str}', {update_time}, '{aes_key}', '{front_version}', '{update_conf_url}', '{network_info_str}');"
        cursor = conn.execute(sql)
        
        sql = "select * from agent_config;"
        cursor = conn.execute(sql)
        print(cursor.fetchall())

        conn.close()

        return True

    except Exception as err:
        print('{} :{} '.format(err, str(traceback.format_exc())))

    finally:
        #os.remove(temp_dbname)
        pass


# python create_db.py -a b2b@github@2023. -f ../../configurations\19.yaml -ac E:/work/project/EPUERP/code/BlockAtmGuard-github/test_desktop_agent/app/conf.yaml
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-a", "--aes_key", required=False, default='b2b@github@2023.', help="password")
    parser.add_argument("-f", "--file", required=True, help="yaml file")
    parser.add_argument("-ac", "--app_config_file", required=True, help="app配置文件")
    parser.add_argument("-e", "--encrypt_dbname", default='agentapp_encrypt.db', help="加密db")
    parser.add_argument("-d", "--decrypt_dbname", default='agentapp_decrypt.db', help="非加密db")
    parser.add_argument("-p", "--password", default='123456', help="password")

    known_args = parser.parse_args()

    print(known_args.encrypt_dbname)

    with open(known_args.app_config_file) as fp:
        app_conf = yaml.full_load(fp)

    sys.exit(create_db(known_args.file, app_conf, known_args.aes_key, known_args.encrypt_dbname, known_args.decrypt_dbname, known_args.password, True))