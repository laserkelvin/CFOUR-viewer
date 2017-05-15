
from cfour_viewer.routines import read_json, get_calc_path, save_json
import os
import shutil
import subprocess
from glob import glob

class automated_calculation:
    def __init__(self, settings_json, pbs_id):
        self.settings = {
            "zmat": "",
            "id": int(pbs_id),
            "name": "Molecule",
            "comment": "Generated CFOUR ZMAT",
            "basis": list(),
            "methods": list(),
            "scr": "/scratch/sao/klee",
            "todo": list(),
            "atoms": list()        # input as a list of atoms
            "type": "opt",
            "keywords": {
                "MEMORY_SIZE": 4,
                "MEM_UNIT": "GB",
                "ABCD": "AOBASIS",
                "CC_CONV": 9,
                "SCF_CONV": 9,
                "LINEQ_CONV": 9,
                "SCF_MAXCYC": 500,
                "SCF_DAMPING": 0,
                "MULTIPLICITY": 1,
                "REFERENCE": "RHF",
                "CC_PROGRAM": "ECC",
            }
        }

    self.settings.update(settings_json)

    self.settings["work_dir"] = self.settings["scr"] + "/" + str(pbs_id)

    def determine_calctype(self):
        options = ["opt", "composite"]
        if self.settings["type"] not in options:
            raise ValueError("Specified calculation scheme not implemented.")
        else:
            if self.settings["type"] == "opt":
                # Set up calculations that will progressively increase
                # basis and methods

    def combinations(self):
        # Work out the combinations of method/basis we need to set up
        calculations = list()
        for method in self.settings["methods"]:
            calculations.append([[method, basis] for basis in self.settings["basis"]])
        return calculations

    def format_zmat(self, method, basis):
        write_string = ""
        write_string += self.settings["comment"] + "\n"
        write_string += self.settings["zmat"] + "\n"
        write_string += "*CFOUR(CALC_LEVEL=" + method + "\n"
        for keyword in self.settings["keyword"]:
            write_string += keyword + "=" + str(self.settings["keyword"][keyword]) + "\n"

        # Determine the way the basis is specified
        if len(self.settings["atoms"]) != 0:
            write_string += "BASIS=SPECIAL)\n \n"
            for atom in self.settings["atoms"]:
                write_string += atom + ":" + basis + "\n"
        else:
            write_string += "BASIS=" + basis + ")\n"
        return zmat_string

    def run_cfour(self, mode="serial"):
        if os.path.isdir(self.settings["work_dir"]) is False:
            os.mkdir(self.settings["work_dir"])
        else:
            # Clean up the directory before we use it
            for files in glob(self.settings["work_dir"] + "/*"):
                os.rm(files)
        shutil.copy2("ZMAT", self.settings["work_dir"] + "/ZMAT")
