import asyncio
import io
import json
import os
import re
from datetime import datetime
from typing import Optional, Union
import base64

from PIL import Image
from playwright.async_api import async_playwright
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot import logger

basic_path = os.path.dirname(__file__)
save_path = os.path.join(basic_path, "temp")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-cn"
}


def gen_ms_img(image: Union[bytes, Image.Image]) -> MessageSegment:
    if isinstance(image, bytes):
        return MessageSegment.image(
            pic2b64(Image.open(io.BytesIO(image)))
        )
    else:
        return MessageSegment.image(
            pic2b64(image)
        )


def get_present_time() -> int:
    return int(datetime.timestamp(datetime.now()))


async def screen_shot(url: str, time_present: int) -> Optional[str or bool]:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            # 设置视口大小
            await page.set_viewport_size({"width": 2800, "height": 2800})
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            with open(f'{basic_path}/data/plantes_mix.json', 'r', encoding='utf-8') as file:
                replacements = json.load(file)
            # 遍历字典，构建替换脚本
            replacement_script = ""
            for keyword, replacement in replacements.items():
                escaped_keyword = json.dumps(keyword)
                escaped_replacement = json.dumps(replacement)
                replacement_script += f"""
                        document.body.outerHTML = document.body.outerHTML.replace(new RegExp({escaped_keyword}, 'g'), {escaped_replacement});
                    """

            # 在页面上执行替换脚本
            await page.evaluate(replacement_script)

        except Exception as e:
            return f"访问网站异常{type(e)}`{e}`"
        await asyncio.sleep(1)
        logger.info("正在保存图片...")
        img_path = os.path.join(save_path, f'{time_present}.png')
        await page.screenshot(
            path=img_path,
            full_page=True
        )
        logger.info("正在压缩图片...")
        img_convert = Image.open(img_path)
        img_convert.save(img_path, quality=80)
        logger.info("图片保存成功！")
        await browser.close()
        return "success"


def pic2b64(pic: Image) -> str:
    buf = io.BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str
