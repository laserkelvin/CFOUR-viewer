
from qchem_pytools import cfour_input
from qchem_pytools import abinitio_directories
from qchem_pytools import cfour_parse
import os
import shutil
import json

schemes = ["HEAT345(Q)", "CBS",]

definitions = {
    "HEAT345(Q)": {
        "correlation": {
            "method": ["CCSD(T)"] * 3,
            "basis": ["AUG-PCVTZ", "AUG-PCVQZ", "AUG-PCV5Z"],
        },
        "dboc": {
            "method":[ "HF"],
            "basis": ["AUG-PVTZ"],
            "special": {"dboc": "ON"}
        },
        "relativity": {
            "method": ["CCSD(T)"],
            "basis": ["AUG-PCVTZ"],
            "special": {"relativistic": "MVD2"}
        },
        "hlc": {
            "method": ["CCSD(T)", "CCSDT"] * 2,
            "basis": ["PVTZ", "PVTZ", "PVQZ", "PVQZ"],
            "special": {"frozen_core": "ON"}
        },
        "zpe": {
            "method": ["CCSD(T)"],
            "basis": ["PVQZ"],
            "special": {"vib": "EXACT"}
        }
    },
    "CBS": {
        "correlation": {
            "method": ["CCSD(T)"] * 3,
            "basis": ["AUG-PCVTZ", "AUG-PCVQZ", "AUG-PCV5Z"]
        }
    },
    "mHEAT345": {
        "correlation": {
            "method": ["CCSD(T)"] * 3,
            "basis": ["PVTZ", "PVQZ", "PV5Z"]
        },
        "dboc": {
            "method": ["HF"],
            "basis": ["aug-PVTZ"],
            "special": {"dboc": "ON"}
        },
        "relativity": {
            "method": ["MP2"],
            "basis": ["AUG-PCVTZ"],
            "special": {"relativistic": "MVD2"}
        },
        "hlc": {
            "method": ["CCSD(T)", "CCSDT"],
            "basis": ["PVTZ", "PVTZ"],
            "special": {"frozen_core": "ON"}
        },
        "zpe": {
            "method": ["CCSD(T)"],
            "basis": ["ANO1"],
            "special": {"vib": "EXACT"}
        }
    },
    "custom": {
        "blank": {
            "method": list(),
            "basis": list()
        }
    }
}

""" For a given optimised ZMAT, this will set up all of the input
    files for high accuracy calculations, defined in the list
    `schemes`
"""

class composite_methods:
    def __init__(self, identifier, scheme=None):
        self.InfoDict = {
        "id": identifier,
        "rootdir": os.path.abspath(os.path.curdir) + "/" + identifier,
        "origin": os.path.abspath(os.path.curdir),
        "scheme": None,
        "calculations": dict(),
        "global settings": {
            "zmat": "",
            "memory": "2",
            "charge": "0",
            "multiplicity": "1",
            "reference": "RHF",
            "comment": ""
            },
        "output": list()
        }
        if scheme is None:
            self.InfoDict["scheme"] = "CBS"
        else:
            if scheme not in definitions.keys():
                print("Incorrect scheme, defaulting to CC/CBS.")
                self.InfoDict["scheme"] = "CBS"
            else:
                self.InfoDict["scheme"] = scheme
        self.InfoDict["calculations"] = definitions[self.InfoDict["scheme"]]
        print("Please supply InfoDict with the following information:")
        print("ZMAT, charge, multplicity, and reference wavefunction.")
        print("Please call setup method.")

    def setup(self):
        if (os.path.exists(self.InfoDict["id"])) is True:
            clean_bool = input("Folder exists, remove? Y/N")
            if clean_bool == "Y" or clean_bool == "y":
                shutil.rmtree(self.InfoDict["id"])
                os.mkdir(self.InfoDict["id"])
            else:
                raise Exception("Folder already exists!")
        else:
            os.mkdir(self.InfoDict["id"])
        for contribution in self.InfoDict["calculations"]:
            requiredcalcs = zip(
                self.InfoDict["calculations"][contribution]["method"],
                self.InfoDict["calculations"][contribution]["basis"]
            )
            os.chdir(self.InfoDict["rootdir"])
            os.mkdir(contribution)
            os.chdir(contribution)
            abinitio_directories.setup_folders()
            for method, basis in requiredcalcs:
                name = method + "-" + basis
                comment = contribution + " calculation at " + name
                calcsettings = self.InfoDict["global settings"].copy()
                calcsettings["method"] = method
                calcsettings["basis"] = basis
                calcsettings["comment"] = comment
                if "special" in self.InfoDict["calculations"][contribution]:
                    calcsettings.update(
                        self.InfoDict["calculations"][contribution]["special"]
                    )
                input_instance = cfour_input.cfour_zmat(
                    comment=comment,
                    zmat=self.InfoDict["global settings"]["zmat"],
                    filename=name
                )
                input_instance.settings.update(calcsettings)
                input_instance.build_zmat()
                input_instance.write_zmat()
                input_instance.save_json()
                self.InfoDict["output"].append(input_instance.output)
        os.chdir(self.InfoDict["rootdir"])
        with open(self.InfoDict["id"] + ".json", "w+") as WriteFile:
            json.dump(self.InfoDict, WriteFile)
        os.chdir(self.InfoDict["origin"])

    def parse_output(self):
        output_instances = dict()
        for output in self.InfoDict["output"]:
            name = output.split("/")[-1]
            output_instances[name] = cfour_parse.OutputFile(output)
        self.parsed_output = output_instances
