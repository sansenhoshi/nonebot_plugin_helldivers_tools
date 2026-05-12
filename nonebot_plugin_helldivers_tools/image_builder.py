import os
import random
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw, ImageFont
from image_utils import image_paste

basic_path = os.path.dirname(__file__)
save_path = os.path.join(basic_path, "temp")
img_path = os.path.join(basic_path, "img")
data_path = os.path.join(basic_path, "data")


def create_image(selected_equipment):
    new_img = Image.new('RGBA', (800, 500), (0, 0, 0, 1000))
    logo_path = img_path + "/super earth.png"
    logo = Image.open(logo_path)
    new_img = image_paste(logo, new_img, (682, 20))
    draw = ImageDraw.Draw(new_img)
    ch_text_font = ImageFont.truetype(data_path + '/font/msyh.ttc', 36)
    pos_horizon = 20

    for equipment in selected_equipment:
        name = equipment['name']
        alias = random.choice(equipment['alias']) if equipment['alias'] else None

        path = basic_path + "/" + equipment['path'].replace("\\", "/")
        icon = Image.open(path)
        icon = icon.resize((100, 100))
        new_img = image_paste(icon, new_img, (20, pos_horizon))
        draw.text((140, pos_horizon + 5), '战备名称：', fill='white', font=ch_text_font)
        draw.text((140, pos_horizon + 50), f'{name} - ({alias})', fill='white', font=ch_text_font)
        pos_horizon += 120

    b_io = BytesIO()
    new_img = ImageOps.expand(new_img, border=10, fill="white")
    new_img.save(b_io, format="PNG")
    return b_io
