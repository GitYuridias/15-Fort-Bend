import json
import os
from os.path import dirname, abspath


def countCharges(input_dict):

    count = 0
    for key, value in input_dict.items():
        if key.startswith("charge"):
            count += 1

    return count


def set_json(input_path, name, surname, input_dict):

    final_path = os.path.join(input_path, f"{surname}_{name}.json")

    with open(final_path, "w") as outfile:
        json.dump(input_dict, outfile, indent=4)

    print(f'The json file is set')