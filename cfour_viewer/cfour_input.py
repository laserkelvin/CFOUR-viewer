
import os
import subprocess
import json
import time

class cfour_handler:
    """
        Parent class that handles a CFOUR calculation ID. This can involve one
        or multiple calculations that may or may not depend on each other.
        For example, geometry optimization with multiple basis, either parallel
        or sequential, or a HEAT calculation.

        Calculation schemes will be stored in the dot folder in the $HOME direc-
        tory, so that you can add more schemes without having to hard-code.
    """
    class cfour_calc(cfour_handler):
        """
            Class for handling a single CFOUR calculation. This handles generation
            of an input file, copying files to scratch, running the calculation
            using subprocess, and then preserving the results.

            The more advanced methods, such as handling multiple chained calculations
            will be performed in the parent class.
        """
        def __init__(self, )




class cfour_zmat:

    zmat_template = """{comment}
{zmat}
*CFOUR(CALC_LEVEL={method}
BASIS={basis}
SCF_CONV={scf_conv}
CC_PROGRAM={cc_program}
CC_CONV={cc_conv}
GEO_CONV={geo_conv}
LINEQ_CONV={lineq_conv}
MEM_UNIT=GB
MEMORY_SIZE={memory}
CHARGE={charge}
ABCDTYPE=AOBASIS
EXCITE={excite}
DBOC={dboc}
RELATIVISTIC={relativistic}
VIB={vib}
FREQ_ALGORITHM={freq_algorithm}
REFERENCE={reference}
MULTIPLICITY={multiplicity}
SCF_DAMPING={scf_damping}
FROZEN_CORE={frozen_core})
{footer}
"""

    pbs_template = """#/bin/bash
# ----------- Parameters --------- #
#$ -S /bin/bash
#$ -l {memory}
#$ -q {queue}
#$ -cwd
#$ -j y
#$ -N {pbsname}
#
# -------- User Variables -------- #
scrtop={scrtop}
scrdir=$scrtop/$JOB_ID
cwd=`pwd`
cfourdir={cfourdir}
export PATH=$cfourdir:$PATH
# ----------- Modules ------------ #
#
module load intel
#
# ------------- Job -------------- #
#
export OMP_NUM_THREADS=1
mkdir $scrdir
cp FCM* $scrdir
cp ZMAT $scrdir
echo `date` job $JOB_NAME started in $QUEUE with jobID=$JOB_ID on $HOSTNAME
cd $scrdir
xcfour > $cwd/$JOB_ID.log
echo `date` calculation finished.
echo Space used `du -sh`
cp FCM* $cwd
cp JOB* $cwd
cp JAIN* $cwd
cp ZMATnew $cwd
cp ZMATtemp $cwd
xclean
rmdir $scrdir
"""

    def __init__(self, json_input, mode="cluster"):
        self.settings = {
            "basis": "ANO0",
            "method": "CCSD",
            "cc_program": "ECC",
            "memory": "1",
            "scf_conv": "7",
            "cc_conv": "7",
            "geo_conv": "6",
            "lineq_conv": "7",
            "reference": "RHF",
            "charge": "0",
            "multiplicity": "1",
            "excite": "NONE",
            "scf_damping": "0",
            "dboc": "OFF",
            "relativistic": "OFF",
            "vib": "NO",
            "freq_algorithm": "ANALYTIC",
            "zmat": """
            """,
            "frozen_core": "OFF",
            "comment": "Generated CFOUR ZMAT",
            "footer": "",
            "timestamp": time.strftime("%d/%m/%Y") + "\t" + time.strftime("%H:%M:%S")
        }

        self.settings.update(json_dict)

        self.settings["root_path"] = os.path.abspath(os.curdir)
        self.settings["file_path"] = self.settings["root_path"] + "/calcs/" + filename + "/"
        self.output = self.settings["file_path"] + filename + ".out"

    def write_zmat(self):
        if (os.path.exists(self.settings["file_path"])) is True:
            pass
        else:
            os.mkdir(self.settings["file_path"])
        if os.path.isfile(self.settings["file_path"] + "ZMAT"):
            cont = input("Folder already exists, continue? Y/N\t")
            if cont == "Y" or "y":
                with open(self.settings["file_path"] + "ZMAT", "w+") as WriteFile:
                    WriteFile.write(self.input)
            elif cont == "N" or "n":
                pass
        else:
            with open(self.settings["file_path"] + "ZMAT", "w+") as WriteFile:
                WriteFile.write(self.input)

    def build_zmat(self, extra=None):
        """ Method that will construct the ZMAT file.
            Extra arguments should be provided as a list of strings;
            ["VIB=EXACT", "EXCITE=EOMIP"]
        """
        self.input = self.zmat_template.format_map(self.settings)
        if extra is not None:
            for item in extra:
                self.input = self.input + item + "\n"
        print(self.input)

    def run_calc(self):
        command = self.settings["cfour_path"] + "xcfour"
        os.chdir(self.settings["file_path"])
        if self.settings["mode"] == "cluster":


    def restart_calc(self):
        self.clean()
        os.system("cp ZMATtemp ZMAT")
        self.run_calc()

    def clean(self):
        os.chdir(self.settings["file_path"])
        subprocess.run(["xclean"])
        files = [
        "FCM*", "MOL", "OLDMOS",
        "THETA", "OPTARC", "VPOUT",
        "dens.dat", "basinfo.dat",
        "EFG",
        ]
        for file in files:
            os.system("rm " + file)
        os.chdir(self.settings["root_path"])
