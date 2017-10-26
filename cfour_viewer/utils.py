
"""
    Contains all of the auxillary functions for CFOURviewer; i.e. file I/O,
    storage to HDF5, copying and pasting, etc.

    The scope of HDF5 will be to store the parsed data, as well as the full
    output file as a string.

    Settings will be stored in a dot folder in the user's home directory;
    this includes templates for the PBS script as well as CFOURviewer settings.
"""

import os
import shutil
import h5py
import datetime
import yaml
from glob import glob


def generate_folder():
    # Function to generate the next folder in the ID chain.
    # Returns the next ID number in the chain as an integer.
    settings = read_settings()
    dir_list = glob(settings["calc_dir"] + "/*")
    filtered = list()
    for dir in dir_list:
        # This takes only folder names that are numeric
        try:
            filtered.append(int(dir))
        except TypeError:
            pass
    next_ID = max(filtered) + 1
    os.mkdir(settings["calc_dir"] + str(next_ID))
    return next_ID


def read_settings():
    # Wrapper for the read_yaml function, specifically to call up the
    # settings file.
    location = os.path.expanduser("~") + "/.cfourviewer/settings.yml"
    return read_yaml(location)

"""
    File I/O

    Includes YAML and HDF5 functions

    HDF5 system is organized into IDs - an ID can contain one or several
    calculations, and the attributes of an ID group are metadata regarding
    the calculation batch, i.e. a SMILES code to identify the molecule.

    Each calculation is then stored as datasets within this group, and the
    parsed results of the calculation.
"""

def write_yaml(yaml_path, contents):
    # Function for writing dictionary to YAML file
    with open(yaml_path, "w+") as write_file:
        yaml.dump(contents, write_file, default_flow_style=False)


def read_yaml(yaml_path):
    # Function for reading in a YAML file
    with open(yaml_path) as read_file:
        return yaml.load(read_file)


def create_db(filepath):
    # Initializes an H5Py database
    with h5py.File(db_path, "w+") as h5file:
        h5file["created"] = datetime.datetime.now()
        h5file["creator"] = os.uname()[1]
        h5file["modified"] = datetime.datetime.now()


def add_db_entry(db_path, metadata, results):
    # Takes a dictionary of parsed results and adds an entry to the HDF5 db
    with h5py.File(db_path, "a") as h5file:
        if metadata["ID"] not in h5py.keys():
            # If the ID group hasn't been created yet, make it and also
            # add the metadata in
            id_entry = h5file.create_group(metadata["ID"])
        for key in metadata:
            id_entry.attrs[key] = metadata[key]
        else:
            print("Entry " + results_dict["ID"] + " already exists.")
        # Storing the parsed results
        for calc in results:
            calc_entry = id_entry.create_group(calc)
            for key in results[calc]:
                if type(results[calc][key]) is not dict:
                    calc_entry.create_dataset(
                    key,
                    data=results[calc][key]
                    )
                else:
                    if key == "quadrupole":
                        for atom in results[calc][key]:
                            


def retrieve_db_entry(db_obj, ID):
    # Function for returning a dictionary of all attributes contained in a
    # HDF5 dataset
    # The database object and ID are given as arguments - the idea is to perform
    # loops in whatever function you are calling so you don't have to reopen
    # the HDF5 database
    return {key: db_obj[str(ID)].attrs[key] for key in db_obj[str(ID)].attrs.keys()}


def export_db_entry(db_path, ID, location=None):
    # Function for retrieving a database entry, and exporting it in YAML format
    with h5py.File(db_path, "r") as h5file:
        if str(ID) not in h5file.keys():
            raise EntryError("Entry " + str(ID) + " does not exist.")
        else:
            id_entry = retrieve_db_entry(h5file, ID)
            if location is None:
                location = os.getcwd() + str(ID) + "_out.yml"
            write_yaml(location, id_entry)
