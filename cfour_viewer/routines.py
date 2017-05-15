
import json
import os

def get_calc_path(calcID):
    script_path = os.path.dirname(os.path.realpath(__file__))
    with open(script_path + "/" + "settings.json") as read_json:
        settings = json.load(read_json)
    return settings["output_dir"] + "/" + str(calcID)

def save_json(filepath, content):
    with open(filepath, "w+") as WriteFile:
        json.dump(content, WriteFile, indent=4, sort_keys=True)

def read_json(filepath):
    with open(filepath) as ReadFile:
        json_dict = json.load(ReadFile)
    return json_dict

def atoms_from_zmat(zmat_path):
    atom_list = list()
    with open(zmat_path, "r") as read_file:
        file_contents = read_file.readlines()
    file_contents = file_contents[1:]        # First line is comment
    for line in file_contents:
        split_line = line.split()
        if len(split_line) != 0:
            atom_list.append(line.split()[0])
        else:
            return atom_list
