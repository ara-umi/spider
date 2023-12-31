import asyncio
import datetime
import json
import os
import time

import aiohttp
import mysql.connector
from mysql.connector import IntegrityError

from dealer import GameskyDealer
from generator import GameskyGenerator
from middleware.downloader import Downloader
from middleware.request import IDChecker
from save_list import main
from middleware.utils.import_sql import import_data_to_sql

async def main(start_datetime: datetime, end_datetime: datetime, start_page: int = 1, gl_class: int = 18,
               id_list_path: str = "./record/id_list.json"):
    generate = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime, start_page=start_page,
                                gl_class=gl_class, sources='gamersky')
    post_list = []
    async for post in generate():
        post_list.append(post)
        print(post)
    # 这里读取id_list想根据已经有的id去除post_list存在的id，并不写入新的post_id
    id_checker = IDChecker(post_list=post_list, id_list_path=id_list_path)
    post_list = id_checker()

    session = aiohttp.ClientSession()  # 之后session要做成注入参数
    for post in post_list:  # 这里后期要做并发
        deal = GameskyDealer(post=post, session=session)  # 这里后期post不能做成初始化参数
        post = await deal(raw=True, sleep_time=0.03)
        downloader = Downloader(post=post)
        await downloader.download_txt(path='./txt_results_new')
        flag = await downloader.download_json(path='./json_results_new')
        # 保存到本地后才写入post_id
        id_checker.save_each_post_id(post)
        # 导入数据库
        if flag:
            try:
                import_data_to_sql(post)
            except IntegrityError as e:
                print(f"攻略 {post.title} 已存在。")
                pass
    await session.close()


def get_data_select_page(start_time: int, end_time: int, start_page: int = 1):
    input_date = datetime.datetime.strptime(str(start_time), "%Y%m%d")
    end_date = datetime.datetime.strptime(str(end_time), "%Y%m%d")
    start_datetime = datetime.datetime(year=input_date.year, month=input_date.month, day=input_date.day)
    end_datetime = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day)
    asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime, start_page))


def get_data_auto_update(interval: int = 30):
    while True:
        start_datetime = datetime.datetime.combine(datetime.datetime.today().date(), datetime.time(0, 0, 0))
        end_datetime = datetime.datetime.today()
        asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime, gl_class=18,
                                                         id_list_path="./record/id_list_new.json"))
        asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime, gl_class=21114,
                                                         id_list_path="./record/id_list_new.json"))

        # 定时更新打印
        remaining_time = interval * 60

        while remaining_time > 0:
            minutes, seconds = divmod(remaining_time, 60)
            hours, minutes = divmod(minutes, 60)
            print(f"下一次更新将在 {hours:02d}:{minutes:02d}:{seconds:02d} 后进行")
            time.sleep(1)
            remaining_time -= 1


if __name__ == "__main__":
    get_data_auto_update(interval=1)
