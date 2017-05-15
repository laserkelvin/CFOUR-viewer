# from setuptools import setup
#
# setup(
#     name="cfour_viewer",
#     version="0.1",
#     description="A PyQt5 frontend to the electronic structure program, CFOUR.",
#     author="Kelvin Lee",
#     packages=["cfour_viewer"],
#     include_package_data=True,
#     author_email="kin.long.kelvin.lee@gmail.com",
#     install_requires=[
#             "numpy",
#             "plotly",
#             "pandas",
#             "scipy",
#             "colorlover",
#             "matplotlib"
#     ]
# )

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os
import sys

class PostInstallCommand(install):

    def run(self):

        python_path = sys.executable        # Path to python interpreter
        user_home = os.path.expanduser("~")      # User home directory
        with open("./cfour_viewer/runcfour_template.scr") as ReadFile:
            runcfour_template = ReadFile.read()
        with open(user_home + "/bin/runCFOUR", "w+") as WriteFile:
            WriteFile.write(
                runcfour_template.format(python_path)
            )
        with open("./cfour_viewer/parsecfour_template.scr") as ReadFile:
            parsecfour_template = ReadFile.read()
        with open(user_home + "/bin/parseCFOUR", "w+") as WriteFile:
            WriteFile.write(
                parsecfour_template.format(python_path)
            )
        with open("./cfour_viewer/copyzmat_template.scr") as ReadFile:
            copyzmat_template = ReadFile.read()
        with open(user_home + "/bin/copyZMAT", "w+") as WriteFile:
            WriteFile.write(
                copyzmat_template.format(python_path)
            )
        with open("./cfour_viewer/harmdiff_template.scr") as ReadFile:
            copyzmat_template = ReadFile.read()
        with open(user_home + "/bin/harmdiffCFOUR", "w+") as WriteFile:
            WriteFile.write(
                copyzmat_template.format(python_path)
            )
        with open("./cfour_viewer/analyseharmdiff_template.scr") as ReadFile:
            copyzmat_template = ReadFile.read()
        with open(user_home + "/bin/analysefreqoutput", "w+") as WriteFile:
            WriteFile.write(
                copyzmat_template.format(python_path)
            )
        with open("./cfour_viewer/analysevpt2_template.scr") as ReadFile:
            copyzmat_template = ReadFile.read()
        with open(user_home + "/bin/analyseVPT2", "w+") as WriteFile:
            WriteFile.write(
                copyzmat_template.format(python_path)
            )
        with open("./cfour_viewer/setupvpt2_template.scr") as ReadFile:
            copyzmat_template = ReadFile.read()
        with open(user_home + "/bin/setupVPT2", "w+") as WriteFile:
            WriteFile.write(
                copyzmat_template.format(python_path)
            )
        with open("./cfour_viewer/generatereports_template.scr") as ReadFile:
            copyzmat_template = ReadFile.read()
        with open(user_home + "/bin/generateReports", "w+") as WriteFile:
            WriteFile.write(
                copyzmat_template.format(python_path)
            )
        with open("./cfour_viewer/harmfreqisotopes_template.scr") as ReadFile:
            copyzmat_template = ReadFile.read()
        with open(user_home + "/bin/harmfreqisotopes", "w+") as WriteFile:
            WriteFile.write(
                copyzmat_template.format(python_path)
            )
        os.system("chmod a+x " + user_home + "/bin/parseCFOUR")
        os.system("chmod a+x " + user_home + "/bin/runCFOUR")
        os.system("chmod a+x " + user_home + "/bin/copyZMAT")
        os.system("chmod a+x " + user_home + "/bin/harmdiffCFOUR")
        os.system("chmod a+x " + user_home + "/bin/analysefreqoutput")
        os.system("chmod a+x " + user_home + "/bin/analyseVPT2")
        os.system("chmod a+x " + user_home + "/bin/setupVPT2")
        os.system("chmod a+x " + user_home + "/bin/generateReports")
        os.system("chmod a+x " + user_home + "/bin/harmfreqisotopes")
        install.run(self)

setup(
    name="cfour_viewer",
    version="0.4",
    description="A PyQt5 frontend to the electronic structure program, CFOUR.",
    author="Kelvin Lee",
    packages=["cfour_viewer"],
    include_package_data=True,
    author_email="kin.long.kelvin.lee@gmail.com",
    install_requires=[
            "numpy",
            "plotly",
            "pandas",
            "scipy",
            "colorlover",
            "matplotlib",
            "periodictable"
    ],
    cmdclass={
        "install": PostInstallCommand
    }
)
