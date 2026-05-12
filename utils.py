import math

def kg_to_box_package(total_kg, per_bag_kg=3, bag_per_box=8):
    # 向上取整：算总包数
    total_bag = math.ceil(total_kg / per_bag_kg)
    # 拆成 箱 + 剩余包
    box_num = total_bag // bag_per_box
    bag_remain = total_bag % bag_per_box
    return box_num, bag_remain, total_bag
