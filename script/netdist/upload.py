# -*- coding:utf-8 -*-
import os
import sys
import argparse

def upload(file : str):
    os.system(f'curl https://bashupload.com/agent_app.zip --data-binary @{file}')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-f", "--file", required=True, help="file path")
    known_args = parser.parse_args()

    sys.exit(upload(known_args.file))

