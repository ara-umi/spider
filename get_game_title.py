# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/4 下午11:44

import datetime
import json
import os
import pathlib
import time

import aiohttp
import asyncio

from tqdm import tqdm

from dealer.gamesky_title import GameskyTitleDealer
from generator import GameskyGenerator
from model import GameskyPost
from middleware.downloader import Downloader
from middleware.request import IDChecker
from middleware.utils.save_post_list import PostListSaver
from middleware.utils.load_post_list import PostListLoader


async def get_data_from_list(year: int):
    # 保存post_list
    post_list_loader = PostListLoader(file_path=f"./record/{year}.json")
    post_list = post_list_loader()
    id_checker = IDChecker(post_list, id_list_path='./record/id_list_title.json')
    post_list = id_checker()
    session = aiohttp.ClientSession()  # 之后session要做成注入参数
    count = 0
    for post in tqdm(post_list):  # 这里后期要做并发
        deal = GameskyTitleDealer(post=post, session=session,)  # 这里后期post不能做成初始化参数
        post = await deal(raw=True, sleep_time=0)
        downloader = Downloader(post=post)
        flag = await downloader.download_game_name_json(path='./json_results_title')
        # 保存到本地后才写入post_id
        id_checker.save_each_post_id(post)
        count += 1
        if count == 1000:
            print("休息1分钟……")
            time.sleep(60)
            count = 0
    await session.close()


if __name__ == "__main__":
    year = 2023
    while year > 1996:
        if os.path.exists(f"./record/{year}.json"):
            asyncio.get_event_loop().run_until_complete(get_data_from_list(year))
            year -= 1
        else:
            year -= 1
