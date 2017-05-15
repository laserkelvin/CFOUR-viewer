import json
import os
import shutil
from glob import glob

calc_modes = ["local", "cluster", "test"]

class cfour_instance:
    def __init__(self, calcID, settings, mode="cluster", type=None):
        self.InfoDict = {
            "calcID": str(calcID),
            "calctype": type,
            "mode": mode
        }
        self.InfoDict.update(settings)

    def generate_pbs(self, path=None, name=None):
        """ Generates a PBS script for the calculation,
        which involves telling it where to find the relevant folders.
        """
        with open(self.InfoDict["model_pbs"]) as model_pbs:
            pbs = model_pbs.read()        # read in the exemplar PBS script

        self.InfoDict["name"] = self.InfoDict["calcID"]
        if name is not None:
            self.InfoDict["name"] += "." + name

        if path is None:
            pbs_path = self.InfoDict["calc_dir"] + "/pbs.sh"
        else:
            pbs_path = path

        with open(pbs_path, "w+") as write_pbs:
            write_pbs.write(
                pbs.format(                     # write in the unique parts
                    self.InfoDict["name"],      # for our calculation
                    self.InfoDict["scr_dir"],
                    self.InfoDict["calc_dir"],
                    self.InfoDict["cfour_dir"]
                )
            )
        self.InfoDict["output_file"] = self.InfoDict["calc_dir"] + "/" + \
                                        self.InfoDict["calcID"] + ".log"

    def dump_settings(self):
        """ Dump the settings (directories, etc) we used into a json file """
        with open(self.InfoDict["json_dir"] + "/settings.json", "w+") as WriteFile:
            json.dump(self.InfoDict, WriteFile)

    def run_calc(self):
        """ Function to start the calculation.
            Depending on whether you are running the calculation on a cluster,
            or on a local workstation interactively, the script will either
            use a PBS script or run xcfour in no hangup mode.

            There is also a test case where everything is set up without
            submitting the PBS script to a batch scheduler.
        """
        if self.InfoDict["mode"] == "cluster":
            self.generate_pbs()
            self.dump_settings()
            os.chdir(self.InfoDict["calc_dir"])
            os.system("qsub pbs.sh")
        elif self.InfoDict["mode"] == "local":
            os.system(
                "nohup xcfour > " + self.InfoDict["calc_dir"] + \
                "/" + self.InfoDict["calcID"] + ".log"
            )
        elif self.InfoDict["mode"] == "test":
            self.generate_pbs()
            self.dump_settings()

    def findif_freq(self):
        os.chdir(self.InfoDict["calc_dir"])
        os.system("xjoda")
        os.system("xsymcor")
        self.InfoDict["original_calc_dir"] = self.InfoDict["calc_dir"]
        for zmat in glob("zmat*"):
            self.InfoDict["calc_dir"] = self.InfoDict["original_calc_dir"] + \
            "/" + zmat + "_temp"
            os.mkdir(self.InfoDict["calc_dir"])
            shutil.copy2(zmat, self.InfoDict["calc_dir"] + "/ZMAT")
            os.chdir(self.InfoDict["calc_dir"])
            self.generate_pbs(
                path=self.InfoDict["calc_dir"] + "/pbs.sh",
                name=zmat
            )
            os.system("qsub pbs.sh")
            os.chdir(self.InfoDict["original_calc_dir"])
