# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/7 下午10:28
import json
import pathlib
import re
from typing import Any

import aiohttp
from lxml import etree

from model import GameskyPost
from text_processor import GameskyTextProcessor
from .interface import IDealer


class GameskyDealer(IDealer):
    encoding = "utf-8"

    def __init__(self, post: GameskyPost, session: aiohttp.ClientSession):
        """
        这里还是硬性要求传入一个session，因为是一定要并发的
        只能说传入session会在post较少的情况下，代码量多一点
        其实还要考虑generator是否也需要传入session，并且把session的维护放到generator外
        """

        self.post = post
        self.session = session

    async def process_response(self, response: aiohttp.ClientResponse) -> Any:
        text = await response.text(encoding=self.encoding)
        html = etree.HTML(text=text)
        # 正文目前来看是在Mid2L_con里面
        mid2l_con = html.xpath("//div[@class='Mid2L_con']")[0]
        # 内容都在下面的p标签里面
        p_list = mid2l_con.xpath("./p")
        content_list: list[str] = []
        for p in p_list:
            res = self.process_p(p=p)
            content_list.append(res)

        content: str = "\n".join(content for content in content_list if content)
        return content

    async def process_response_all_tag(self, response: aiohttp.ClientResponse, raw: bool) -> Any:
        """
        保留所有有用tag里的内容，添加多页处理逻辑
        """
        text = await response.text(encoding=self.encoding, errors="ignore")  # 忽略非法字符，默认“strict”会抛出异常
        html = etree.HTML(text=text)
        # 获取网页的原始内容和过滤后的内容
        processor = GameskyTextProcessor(html)
        content_list = processor.get_clean_content()
        raw_content = processor.get_raw_content() if raw else ""
        content: str = "\n".join(content.strip() for content in content_list if content)

        # 获取下一页的链接
        next_page_link = processor.get_next_page_link()
        return raw_content, content, next_page_link

    async def process_localize(self, post: GameskyPost, save_type: str, path: str = "") -> GameskyPost:
        """
        根据指定的方式存储到指定路径
        """
        # 默认路径根据存储类型改变
        if path == "":
            path = pathlib.Path(f"./{save_type}_results")
        else:
            path = pathlib.Path(path)

        if save_type == 'txt':
            self.save_as_txt(post, path=path)
            print(f'Saved as .txt: {post.title}')
        elif save_type == 'json':
            self.save_as_json(post, path=path)
            print(f'Saved as .json: {post.title}')
        return post

    async def __call__(self, raw: bool = False):
        """
        不会存在post不存在url的情况下吧，我规定了一定要传入url的
        但是url是可能不合理的
        保留所有有用tag里的内容，添加多页处理逻辑
        """
        # 缓存
        url = self.post.url
        all_pages_content = ""
        all_pages_raw_content = ""
        while url:
            # url不断迭代，筛选的是text为下一页的url，最后一页的url为None，跳出循环
            async with self.session.get(url=url) as response:
                # content = await self.process_response(response=response)
                raw_content, content, next_page_link = await self.process_response_all_tag(response=response, raw=raw)
                all_pages_content += content
                if raw:
                    all_pages_raw_content += raw_content
                url = next_page_link
        self.post.content = all_pages_content
        self.post.raw = all_pages_raw_content
        return self.post


if __name__ == "__main__":
    pass
