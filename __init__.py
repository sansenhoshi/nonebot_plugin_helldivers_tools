import random
import time

import httpx
import asyncio
import io
import json
import os
import re
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw, ImageFont
from nonebot.internal.params import ArgPlainText
from nonebot.typing import T_State
from playwright.async_api import async_playwright
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, MessageSegment
from nonebot.plugin import PluginMetadata
from typing import Optional, Union
from .utils import *
from nonebot.matcher import Matcher

__plugin_meta__ = PluginMetadata(
    name="绝地潜兵小助手",
    description="绝地潜兵小助手,提供一些小功能，让超级地球更加美好！",
    usage="简报：获取星系战争简要概况\n"
          "随机战备：让机器人帮你随机一套战备",
    type="application",
    extra={

    }
)

basic_path = os.path.dirname(__file__)
save_path = os.path.join(basic_path, "temp")
img_path = os.path.join(basic_path, "img")
data_path = os.path.join(basic_path, "data")

war_situation = on_command("简报", aliases={"简报"})


@war_situation.handle()
async def get_war_info(ev: MessageEvent):
    await war_situation.send("正在获取前线战况……\n本地化需要30s左右，请民主的等待")
    url1 = r"https://hd2galaxy.com/"
    url2 = r"https://helldivers.io/"
    time_present1 = get_present_time()
    result = await screen_shot(url1, time_present1)
    if result != "success":
        await war_situation.finish(MessageSegment.reply(ev.message_id) + result)
    img_path1 = os.path.join(save_path, f"{time_present1}.png")
    logger.info(img_path1)
    images = gen_ms_img(Image.open(img_path1))
    mes = (MessageSegment.reply(ev.message_id), images)
    await war_situation.send(mes)
    os.remove(img_path1)


async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue
                return resp.content
            except Exception as e:
                print(f"Error downloading {url}, retry {i}/3: {str(e)}")


random_helldivers = on_command("随机战备", aliases={"随机战备"})


@random_helldivers.got("pick_type", prompt="请发送你需要的随机规则\n1：纯随机\n2：套路随机(按一定规则随机)")
async def got_random_helldivers(ev: MessageEvent, pick_type: str = ArgPlainText()):
    if not is_number(pick_type):
        await random_helldivers.reject(f"您输入的 {pick_type} 非数字，请重新输入1或者2，或者输入0退出")
    elif int(pick_type) not in [0, 1, 2]:
        await random_helldivers.reject(f"您输入的 {pick_type} 不在范围内，请重新输入1或者2，或者输入0退出")
    elif int(pick_type) == 0:
        return
    elif int(pick_type) == 1:
        result = await get_random_equipment()
        MessageSegment.text("您的随机结果是是：\n")
        final_msg = (MessageSegment.text("您的随机结果是是：\n"),)
        img_base_str = pic2b64(Image.open(result))
        image_turple = MessageSegment.image(img_base_str)
        final_msg += image_turple
        mix_msg = (MessageSegment.reply(ev.message_id),)
        mix_msg += final_msg
        await random_helldivers.finish(mix_msg)
    elif int(pick_type) == 2:
        mix_msg = (MessageSegment.reply(ev.message_id), "开发中，请民主的等待",)
        await random_helldivers.finish(mix_msg)


async def get_random_equipment():
    data_config = os.path.join(basic_path, "data")
    with open(data_config + "/equipment.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    max_equipment = len(data)
    need_equipment = set()  # 初始化一个集合来存储已经生成的数字
    anchor_point = 114514

    for i in range(4):
        while True:  # 循环直到生成不重复的随机数
            index = random.randint(0, max_equipment - 1)
            if index != anchor_point and index not in need_equipment:
                break  # 当生成的随机数不重复时，退出循环
        need_equipment.add(index)  # 将新生成的随机数添加到集合中
        anchor_point = index
    # 1.创建板块
    new_img = Image.new('RGBA', (800, 500), (0, 0, 0, 1000))
    logo_path = img_path + "/super earth.png"
    logo = Image.open(logo_path)
    new_img = image_paste(logo, new_img, (682, 20))
    draw = ImageDraw.Draw(new_img)
    # 2.装载字体
    ch_text_font = ImageFont.truetype(data_path + '/font/msyh.ttc', 36)
    pos_horizon = 20
    for equipment in need_equipment:
        name = data[equipment]['name']
        path = basic_path + "/" + data[equipment]['path'].replace("\\", "/")
        icon = Image.open(path)
        icon = icon.resize((100, 100))
        new_img = image_paste(icon, new_img, (20, pos_horizon))
        draw.text((140, pos_horizon + 5), '战备名称：', fill='white', font=ch_text_font)
        draw.text((140, pos_horizon + 50), f'{name}', fill='white', font=ch_text_font)
        pos_horizon += 120
    b_io = BytesIO()
    new_img = ImageOps.expand(new_img, border=10, fill="white")
    new_img.save(b_io, format="PNG")
    return b_io


# 图片粘贴
def image_paste(paste_image, under_image, pos):
    """
    :param paste_image: 需要粘贴的图片
    :param under_image: 底图
    :param pos: 位置（x,y）坐标
    :return: 返回图片
    """
    if paste_image.mode == 'RGBA':
        # 如果有 alpha 通道，则使用 paste() 方法进行粘贴，并将 alpha 通道作为 mask 参数传递
        under_image.paste(paste_image, pos, mask=paste_image.split()[3])
    else:
        # 如果没有 alpha 通道，则直接进行粘贴
        under_image.paste(paste_image, pos)
    return under_image


def is_number(s):
    return bool(re.match(r'^[0-9]+$', s))
