import os
import subprocess
import json
import shutil
import sys
from glob import glob
from cfour_viewer import cfour_driver
from cfour_viewer import routines
from cfour_viewer import abinitio_directories as ad


def old_analyse_vpt2():
    """ This is to be run after the initial harmonic calculation has already
    finished, and the VPT2 displaced frequency calculations are done

    This function should be called when inside the freq folder.
    """
    harm_zmat_folders = glob("zmat*_temp")      # Each displaced harmonic calc
    top_dir = os.getcwd()
    if os.path.isdir("vpt2") is not True:
        os.mkdir("vpt2")
    try:
        for file in ["JOBARC", "JAINDX"]:
            shutil.copy2(file, "vpt2/" + file + ".0")
    except OSError:
        print(file + " doesn't exist.")
        sys.exit()
    for folder in harm_zmat_folders:            # Loop over each 2nd derivative
        os.chdir(folder)
        analyse_harmonic()
        os.system("rm FJOBARC")
        os.system("xja2fja")
        shutil.copy2("FJOBARC", "../vpt2/fja_all." + folder)
        os.chdir(top_dir)
    os.chdir("vpt2")
    for file in ["JOBARC.0", "JAINDEX.0"]:
        shutil.copy2(file, file.split(".")[0])  # get rid of the suffix
    for file in glob("fja_all.*"):
        shutil.copy2(file, "FJOBARC")
        for command in ["xja2fja", "xcubic"]:
            os.system(command + " >> VPT_OUTPUT")


def analyse_vpt2(baseID, displacedIDs):
    """ BaseID is given as an integer, while displacedIDs is a list of IDs
    that correspond to each displaced harmonic frequency calculation
    """
    base_path = routines.get_calc_path(baseID)
    for ID in displacedIDs:
        cfour_driver.analyse_freq_output(ID)
    script_path = os.path.dirname(os.path.realpath(__file__))
    cwd = os.getcwd()
    # read in the settings file which lives with the script
    with open(script_path + "/settings.json") as open_json:
        settings = json.load(open_json)
    os.chdir(settings["output_dir"])
    anharmID = ad.generate_folder()
    anharm_path = routines.get_calc_path(anharmID)
    os.chdir(anharm_path)
    ad.setup_folders()
    os.chdir("calcs")
    for file in ["JOBARC", "JAINDX", "ZMAT"]:
        shutil.copy2(base_path + "/calcs/freq/" + file, file)
    freq_paths = [routines.get_calc_path(ID) for ID in displacedIDs]
    for path in freq_paths:
        shutil.copy2(path + "/calcs/freq/FJOBARC", "FJOBARC")
        for command in ["xja2fja", "xcubic"]:
            os.system(command + " >> ../docs/VPT2_OUTPUT")


def analyse_harmonic():
    cwd = os.getcwd()
    zmat_folders = glob("zmat*_temp")           # get all the findif folders
    if os.path.isdir("freq") is True:
        shutil.rmtree("freq")
    os.mkdir("freq")                        # make a folder for analysis
    for file in ["ZMAT", "GENBAS"]:
        shutil.copy2(file, "freq/" + file)      # copy ZMAT and GENBAS
    os.chdir("freq")
    for command in ["xjoda", "xsymcor"]:        # Generate the coordinates
        os.system(command + " >> harmdiff.log")

    for folder in zmat_folders:                 # Combine gradients to
        path = cwd + "/" + folder               # calculate Hessian
        try:
            shutil.copy2(path + "/FJOBARC", "./FJOBARC")
        except FileNotFoundError:
            print("No FJOBARC found in " + folder + ", exiting.")
            sys.exit()
        for command in ["xja2fja", "xsymcor"]:
            os.system(command + " >> harmdiff.log")

    os.system("rm zmat*")
    os.system("xjoda >> FREQ_OUTPUT")           # Print frequency analysis
    os.system("rm FJOBARC")
    #os.system("xja2fja")

    # Parse the frequency output to a dictionary
    FreqFlag = False                            # Frequency flag
    RotationalFlag = False                      # Rotational constants flag
    ZPEFlag = False                             # ZPE flag
    QuadConstantsFlag = False                   # Centrifugal distortion flag
    Frequencies = list()
    ZPE = 0.
    with open("FREQ_OUTPUT", "r") as ReadFile:
        for LineIndex, Line in enumerate(ReadFile):
            # ZPE parsing
            if ("Zero-point energy") in Line:   # All in single line
                FreqFlag = False
                ZPE = float(Line.split()[5])
            # Harmonic frequency parsing
            if FreqFlag is True:
                Frequencies.append(Line.split()[1])
            if ("Cartesian force constants") in Line:
                FreqFlag = True
            # Rotational constants parsing
            if ("**********") in Line:         # stop state
                RotationalFlag = False
            if RotationalFlag is True:         # read state
                ReadLine = Line.split()
                RotationalConstants = [float(value) for value in ReadLine]
            if ("in MHz") in Line:             # start state
                RotationalFlag = True
            # Centrifugal distortion constants parsing
            if ("S-reduced in Line"):          # stop state
                QuadConstantsFlag = False
            if QuadConstantsFlag is True:      # read state
                ReadLine = Line.split()
                if len(ReadLine) > 0:
                    QuadConstants[ReadLine[0]] = float(ReadLine[1])
            if ("A-reduced") in Line:          # start state
                QuadConstantsFlag = True
                QuadConstants = dict()
    OutputDict = {
        "Type": "Harmonic Frequency",
        "Frequencies (1/cm)": Frequencies,
        "Rotational constants (MHz)": RotationalConstants,
        "Zero-point energy (kJ/mol)": ZPE,
    }
    OutputDict.update(QuadConstants)
    return OutputDict
