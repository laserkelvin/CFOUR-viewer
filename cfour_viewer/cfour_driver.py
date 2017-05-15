"""
cfour_driver.py

The main driver for cfour_viewer.

This should be set up so that cfour_driver.py can be
called and we can run the program in interactive mode.
"""

from cfour_viewer import abinitio_directories as ad
from cfour_viewer import cfour_run as cr
from cfour_viewer import cfour_parse as cp
from cfour_viewer.routines import read_json, get_calc_path, save_json, atoms_from_zmat
from cfour_viewer import isotopes
from cfour_viewer import cfour_freq as cf
from cfour_viewer import html_template as ht
import subprocess
import json
import pandas as pd
from pprint import pprint
from glob import glob
import os
import shutil
import sys

def setup_calc(mode="test"):
    """
    The workflow is as follows:
    1. Read in the global settings
    2. Generate the next calculation folder in the outputdir defined in settings
    3. Generate the file structure within the calcID folder
    """
    # this gets the path to where the script lives
    script_path = os.path.dirname(os.path.realpath(__file__))
    cwd = os.getcwd()
    # read in the settings file which lives with the script
    with open(script_path + "/settings.json") as open_json:
        settings = json.load(open_json)
    os.chdir(settings["output_dir"])
    # Generate the next in a chain of calculation IDs
    calcID = ad.generate_folder()
    # Set up where the folders will live
    settings["calc_dir"] = settings["output_dir"] + "/" + str(calcID) + "/calcs"
    settings["json_dir"] = settings["output_dir"] + "/" + str(calcID) + "/json"
    settings["figs_dir"] = settings["output_dir"] + "/" + str(calcID) + "/figures"
    settings["docs_dur"] = settings["output_dir"] + "/" + str(calcID) + "/docs"
    os.chdir(settings["output_dir"] + "/" + str(calcID))
    # Set up the file structure
    ad.setup_folders()
    shutil.copy2(cwd + "/ZMAT", settings["calc_dir"] + "/ZMAT")
    # Initialise an instance of CFOUR calculation
    calculation = cr.cfour_instance(
        calcID=calcID,
        settings=settings,
        mode=mode
    )
    calculation.run_calc()
    print("Calculation ID: " + str(calcID))

def parse_calc(calcID, print_dict=True):
    print("Parsing Calculation ID: " + str(calcID))
    script_path = os.path.dirname(os.path.realpath(__file__))
    cwd = os.getcwd()
    with open(script_path + "/settings.json") as open_json:
        settings = json.load(open_json)
    os.chdir(settings["output_dir"] + "/" + str(calcID))
    settings["calcID_dir"] = settings["output_dir"] + "/" + str(calcID)
    output_instance = cp.OutputFile(
        settings["calcID_dir"] + "/calcs/calc" + str(calcID) + ".log"
    )
    output_instance.export_xyz()
    if print_dict is True:
        pprint(output_instance.InfoDict)
    else:
        return output_instance.InfoDict

def copy_zmat(calcID):
    cwd = os.getcwd()
    calc_path = get_calc_path(calcID)
    results_json_path = calc_path + "/json/calc" + str(calcID) + \
    ".results.json"
    if os.path.isfile(results_json_path) is True:
        pass                                # do nothing
    else:                                        # parse the calc if it
        parse_calc(calcID)                       # hasn't been done yet
    results_dict = read_json(results_json_path)  # read in the results
    if len(results_dict["final zmat"]) < 2:
        print("Copying unoptimized ZMAT")
        target_zmat = "input zmat"               # if we don't optimise, we
    else:                                        # don't get a new ZMAT so we'll
        target_zmat = "final zmat"               # use the initial one
        print("Copying optimized ZMAT")
    if os.path.isfile("./ZMAT") is True:
        shutil.copy2("./ZMAT", "./ZMATold")
    with open("./ZMAT", "w+") as WriteFile:
        # Flatten the list holding the new ZMAT
        WriteFile.write(
        "".join(results_dict[target_zmat])
        )

def harm_findif():
    """
    The workflow is as follows:
    1. Read in the global settings
    2. Generate the next calculation folder in the outputdir defined in settings
    3. Generate the file structure within the calcID folder
    """
    # this gets the path to where the script lives
    script_path = os.path.dirname(os.path.realpath(__file__))
    cwd = os.getcwd()
    # read in the settings file which lives with the script
    with open(script_path + "/settings.json") as open_json:
        settings = json.load(open_json)
    os.chdir(settings["output_dir"])
    # Generate the next in a chain of calculation IDs
    calcID = ad.generate_folder()
    # Set up where the folders will live
    settings["calc_dir"] = settings["output_dir"] + "/" + str(calcID) + "/calcs"
    settings["json_dir"] = settings["output_dir"] + "/" + str(calcID) + "/json"
    settings["figs_dir"] = settings["output_dir"] + "/" + str(calcID) + "/figures"
    settings["docs_dur"] = settings["output_dir"] + "/" + str(calcID) + "/docs"
    os.chdir(settings["output_dir"] + "/" + str(calcID))
    # Set up the file structure
    ad.setup_folders()
    shutil.copy2(cwd + "/ZMAT", settings["calc_dir"] + "/ZMAT")
    # Initialise an instance of CFOUR calculation
    calculation = cr.cfour_instance(
        calcID=calcID,
        settings=settings,
        mode=None
    )
    calculation.findif_freq()
    print("Setup harmonic calculation by fin.diff. ID: " + str(calcID))

def analyse_freq_output(calcID):
    cwd = os.getcwd()
    calc_path = get_calc_path(calcID)
    os.chdir(calc_path + "/calcs")
    freq_dict = cf.analyse_harmonic()
    freq_dict = cp.external_parse(calc_path + "/calcs/freq/FREQ_OUTPUT")
    save_json(calc_path + "/json/calc" + str(calcID) + ".results.json",
              freq_dict
              )
    pprint(freq_dict)

def harmfreq_isotopes(calcID):
    """ Generates all isotopologues, and produces their spectroscopic constants.
        The threshold for "relevance" is set as a percentage in abundance,
        although some atoms (e.g. deuterium, 18-oxygen) are commonly used in
        substitution studies and are included.
    """
    calc_path = get_calc_path(calcID)
    json_path = calc_path + "/json/calc" + str(calcID) + ".results.json"

    # Pre-flight check: see if the harmonic frequency output has been analysed
    if os.path.isfile(json_path) is False:
        raise FileNotFoundError("Frequency JSON file does not exist. Run analysis scripts!")

    freq_path = calc_path + "/calcs/freq/"
    # Get list of all the output files from the frequency analysis
    freq_filelist = glob(freq_path + "*")
    freq_filelist = [files for files in freq_filelist if os.path.isfile(files) is True]
    analysis_dict = dict()

    # Generate list of atoms from the ZMAT file - this preserves the ordering of atoms
    atom_list = atoms_from_zmat(freq_path + "ZMAT")
    atom_list = [atom for atom in atom_list if atom != "X"]
    print("Atoms in ZMAT: " + str(atom_list))
    os.chdir(freq_path)
    # Call function to generate all isotopologues and their masses
    isotopologue_dict = isotopes.isotope_combinations(atom_list)
    for isotopologue in isotopologue_dict:
        # Molecular formula for the isotopologue
        name = "".join(isotopologue)
        if os.path.isdir(name) is True:
            # Clean up previous analysis
            shutil.rmtree(name)
        # Make a directory for the isotopologue
        os.mkdir(name)
        os.chdir(freq_path + name)
        for files in freq_filelist:
            shutil.copy2(files, os.getcwd(), follow_symlinks=False)
        # Write the non-standard masses to file for CFOUR to work on
        with open("ISOMASS", "w+") as write_file:
            for mass in isotopologue_dict[isotopologue]:
                write_file.write(str(mass) + "\n")
        with open(calc_path + "/docs/" + name + ".freq", "w+") as write_file:
            # Run xjoda to process the frequency information
            process = subprocess.Popen("xjoda", stdout=write_file, stderr=write_file)
            process.wait()
        # Parse the output of the analysis
        freq_output = cp.external_parse(calc_path + "/docs/" + name + ".freq")
        analysis_dict[name] = dict()
        analysis_dict[name]["rotational constants"] = freq_output["rotational constants"]
        analysis_dict[name]["frequencies"] = freq_output["frequencies"]
        analysis_dict[name]["A-reduction CD"] = freq_output["centrifugal distortion"]["A"]
        analysis_dict[name]["S-reduction CD"] = freq_output["centrifugal distortion"]["S"]
        print("Completed analysis for " + name)
        os.chdir(freq_path)
    dataframe = pd.DataFrame.from_dict(analysis_dict)
    dataframe.to_csv(calc_path + "/docs/isotope_data.csv")

def vpt2_findif(calcID):
    """ The calcID here points to a frequency calculation that has already
    completed. The script will then set up the calculations required for the
    cubic force fields.

    I.e. piggy back this script on a finished harmonic frequency job, where
    the ZMAT already has the following keywords:

    ANH_ALGORITHM=PARALLEL
    FREQ_ALGORITHM=PARALLEL
    FD_PROJECT=OFF
    VIB=FINDIF
    ANHARM=VPT2
    """
    top_dir = os.getcwd()
    calc_path = get_calc_path(calcID)
    os.chdir(calc_path + "/calcs")
    if os.path.isdir("freq") is not True:
        print("Harmonic frequency analysis not done yet. Attempting.")
        analyse_freq_output(calcID)
    os.chdir(calc_path + "/calcs/freq")
    os.system("rm zmat*")
    os.system("xcubic")
    for freq_calc_zmat in glob("zmat*"):
        shutil.copy2(freq_calc_zmat, "ZMAT")
        harm_findif()

def generate_reports(calcIDs):
    """ Give a list of calcIDs, and batch generate an HTML report """
    cwd = os.getcwd()
    json_reports = list()
    for ID in calcIDs:
        json_reports.append(parse_calc(ID, print_dict=False))
    ht.multi_report(cwd + "/multi_report", json_reports, calcIDs)
