import httpx
from nonebot import logger
from nonebot.internal.params import ArgPlainText
from nonebot.typing import T_State
from playwright.async_api import async_playwright
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, MessageSegment
from nonebot.plugin import PluginMetadata
from typing import Optional, Union

from .equipment import get_random_equipment, get_equipment_by_combination
from .utils import *
from nonebot.matcher import Matcher

__plugin_meta__ = PluginMetadata(
    name="绝地潜兵小助手",
    description="绝地潜兵小助手,提供一些小功能，让超级地球更加美好！",
    usage="简报：获取星系战争简要概况\n"
          "随机战备：让机器人帮你随机一套战备",
    type="application",
    homepage="https://github.com/sansenhoshi/nonebot_plugin_helldivers_tools"
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


async def download_url(url: str) -> bytes | None:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue
                return resp.content
            except Exception as e:
                print(f"Error downloading {url}, retry {i}/3: {str(e)}")
        return None


random_helldivers = on_command("随机战备", aliases={"随机战备"}, block=True)

# PROMPT = """     ***超级地球武装部***
#    请发送你需要的随机规则
#
# 1：纯随机（不推荐）
#
#    套路随机(按一定规则随机)
#
# 2：2红/1蓝/1绿
# 3：2绿/1红/1蓝
# 4：2蓝/1绿/1红
#
# 5：3红/1蓝
# 6：3绿/1蓝
#
# 7：2红/2蓝
# 8：2蓝/2绿
# 9：2绿/2红
#
# 10：4红
# 11：4绿"""

board_path = f"{img_path}/board.png"

PROMPT = MessageSegment.image(pic2b64(Image.open(board_path)))

error_count = 0


# 用户选择
@random_helldivers.got("pick_type", prompt=PROMPT)
async def got_random_helldivers(event: MessageEvent, pick_type: str = ArgPlainText()):
    global error_count
    if error_count >= 2:
        await random_helldivers.finish("已回归平民生活——")
        logger.info("持续输错退出随机战备")
        error_count = 0
        return
    logger.info(f"用户选择的战备类型: {pick_type}")
    if not is_number(pick_type):
        error_count += 1
        await random_helldivers.reject(f"您输入的 {pick_type} 非数字，请重新输入1到11，或者输入0退出")
    elif int(pick_type) not in range(12):
        error_count += 1
        await random_helldivers.reject(f"您输入的 {pick_type} 不在范围内，请重新输入1到11，或者输入0退出")
    elif int(pick_type) == 0:
        await random_helldivers.finish("已回归平民生活——")
        logger.info("用户选择退出随机战备")
        error_count = 0
        return

    mix_msg = (MessageSegment.reply(event.message_id),)

    type_combinations = {
        2: {'red': 2, 'blue': 1, 'green': 1},
        3: {'green': 2, 'red': 1, 'blue': 1},
        4: {'blue': 2, 'green': 1, 'red': 1},
        5: {'red': 3, 'blue': 1},
        6: {'green': 3, 'blue': 1},
        7: {'red': 2, 'blue': 2},
        8: {'blue': 2, 'green': 2},
        9: {'green': 2, 'red': 2},
        10: {'red': 4},
        11: {'green': 4}
    }

    if int(pick_type) == 1:
        logger.info("用户选择纯随机战备")
        result = await get_random_equipment(4)  # 4 random equipments
    else:
        combination = type_combinations.get(int(pick_type))
        logger.info(f"用户选择的战备组合: {combination}")
        result = await get_equipment_by_combination(combination)

    final_msg = MessageSegment.text("您的随机结果是：\n")
    img_base_str = pic2b64(Image.open(result))
    image_tuple = MessageSegment.image(img_base_str)
    mix_msg += (final_msg, image_tuple)

    await random_helldivers.finish(mix_msg)


def is_number(s):
    return bool(re.match(r'^[0-9]+$', s))
