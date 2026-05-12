import os
import cv2
import json
import numpy as np
from PIL import Image


def read_image_safe(path):
    """
    使用 Pillow 读取图片，保证兼容性
    返回 BGR 格式 numpy 数组（适配 OpenCV）
    """
    try:
        pil_img = Image.open(path).convert("RGB")
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"读取异常: {path} - {e}")
        return None


def get_dominant_color(img):
    """获取图片主色调（红/绿/蓝）"""
    if img is None or img.size == 0:
        return "unknown"

    avg_color = np.array(cv2.mean(img)[:3])
    b, g, r = avg_color

    color_values = {
        "blue": float(b),
        "green": float(g),
        "red": float(r)
    }

    return max(color_values, key=color_values.get)


# ===== 主处理流程 =====

image_data = []
supported_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']

base_dir = os.path.dirname(os.path.abspath(__file__))

print("当前目录:", base_dir)
print("开始处理图片...")
print("-" * 40)

for filename in os.listdir(base_dir):
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in supported_exts:
        continue

    file_path = os.path.join(base_dir, filename)

    if not os.path.isfile(file_path):
        continue

    img = read_image_safe(file_path)

    if img is None:
        print(f"× 读取失败: {filename}")
        continue

    main_color = get_dominant_color(img)

    entry = {
        "name": name,  # ✅ 去掉后缀
        "path": f"img/helldivers/{name}.png",
        "type": main_color,
        "alias": [""],
        "backpack": 0
    }

    image_data.append(entry)
    print(f"✓ 成功处理: {filename} → 主色调: {main_color}")

print("-" * 40)

output_file = os.path.join(base_dir, '../helldivers/a_all_image_metadata.json')

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(image_data, f, indent=2, ensure_ascii=False)

print(f"\n处理完成: 共 {len(image_data)} 张图片")
print(f"JSON 文件已生成: {output_file}")
