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

# python .\create_db.py -f 19.yaml -e agentapp_encrypt.db -d agentapp_decrypt.db -p 123456
# python create_db.py -f 19.yaml -v 3.1.4 -e agentapp_encrypt.db -d agentapp_decrypt.db -p 123456 -a b2b@github@2023.

def create_db(file : str, front_version : str, aes_key : str, encrypt_dbname : str, decrypt_dbname : str, password : str, need_encrypt : bool):
    try:

        print(f'need_encrypt = {need_encrypt}')
        
        (path, filename) = os.path.split(file)
        
        # 读取yaml
        with open(file, encoding = 'utf-8') as f:
            data = f.read()
            decrypt_data = aesdecrypt(aes_key, data)
            conf = yaml.safe_load(decrypt_data)
        conf_str = json.dumps(conf)
        
        # 连接db
        #conn = sqlite3.connect(decrypt_dbname)
        conn = Connection(encrypt_dbname, password)

        # 建表
        conn.execute('''CREATE TABLE agent_order
                    (
                    order_no VARCHAR(128) PRIMARY KEY,
                    order_date INTEGER   NOT NULL,
                    import_date INTEGER   NOT NULL,
                    crypto VARCHAR(64)   NOT NULL,
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
                    front_version VARCHAR(32) NOT NULL
                    );''')

        # 插入配置
        update_time = int(time.time())
        sql = f"INSERT INTO agent_config(yaml_file, config, update_time, aes_key, front_version) VALUES ('{filename}', '{conf_str}', {update_time}, '{aes_key}', '{front_version}');"
        cursor = conn.execute(sql)
        
        # sql = "select * from agent_config;"
        # cursor = conn.execute(sql)
        # print(cursor.fetchall())

        conn.close()

        return True

    except Exception as err:
        print('{} :{} '.format(err, str(traceback.format_exc())))

    finally:
        #os.remove(temp_dbname)
        pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-f", "--file", required=True, help="yaml file")
    parser.add_argument("-v", "--front_version", required=True, help="前端版本")
    parser.add_argument("-e", "--encrypt_dbname", required=True, help="加密db")
    parser.add_argument("-d", "--decrypt_dbname", required=True, help="非加密db")
    parser.add_argument("-p", "--password", required=True, help="password")
    parser.add_argument("-a", "--aes_key", required=False, default='b2b@github@2023.', help="password")

    known_args = parser.parse_args()

    sys.exit(create_db(known_args.file, known_args.front_version, known_args.aes_key, known_args.encrypt_dbname, known_args.decrypt_dbname, known_args.password, True))