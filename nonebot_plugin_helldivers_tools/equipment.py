import json
import os
import random
from .image_builder import create_image


basic_path = os.path.dirname(__file__)
save_path = os.path.join(basic_path, "temp")
img_path = os.path.join(basic_path, "img")
data_path = os.path.join(basic_path, "data")

async def get_random_equipment(count):
    data_config = os.path.join(basic_path, "data")
    with open(data_config + "/equipment.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    indices = select_random_equipment(len(data), count)
    selected_equipment = [data[i] for i in indices]

    return create_image(selected_equipment)


async def get_equipment_by_combination(type_combination):
    data_config = os.path.join(basic_path, "data")
    with open(data_config + "/equipment.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    equipment_by_type = categorize_equipment_by_type(data)
    selected_equipment = select_equipment_by_type(equipment_by_type, type_combination)

    logger.debug(f"根据组合选择的装备: {selected_equipment}")
    return create_image(selected_equipment)


def categorize_equipment_by_type(data):
    equipment_by_type = {}
    for item in data:
        equip_type = item['type']
        if equip_type not in equipment_by_type:
            equipment_by_type[equip_type] = []
        equipment_by_type[equip_type].append(item)
    return equipment_by_type


def select_equipment_by_type(equipment_by_type, type_combination):
    selected_equipment = []
    backpack_count = 0

    for equip_type, count in type_combination.items():
        if equip_type in equipment_by_type:
            available_items = equipment_by_type[equip_type]
            random.shuffle(available_items)
            selected = 0
            for item in available_items:
                if selected < count:
                    if item['backpack'] == 1 and backpack_count >= 1:
                        continue
                    selected_equipment.append(item)
                    selected += 1
                    if item['backpack'] == 1:
                        backpack_count += 1
                else:
                    break

    return selected_equipment


def select_random_equipment(max_equipment, count):
    return random.sample(range(max_equipment), count)



