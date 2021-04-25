from typing import List


def split_groups(input_data: List, group_size: int):
    return [
        input_data[i * group_size:(i + 1) * group_size]
        for i in range((len(input_data) + group_size - 1) // group_size)
    ]