""" This is a crudely written class for parsing
    output from the electronic structure package "CFOUR".

    The idea behind this set of routines is to be able to
    quickly extract all of the useful information out of
    a CFOUR calculation. The information is stored as a Python
    dictionary, which has the syntax of JSON i.e. portable.

    The idea is to also be able to generate quick HTML
    reports so that I can file them into Jupyter notebooks.

    Some of the code is written pythonically, while
    others are not so much...

"""

import pandas as pd
import numpy as np
import os
from cfour_viewer import figure_settings
from cfour_viewer import html_template
import json
import time

class OutputFile:

    def __init__(self, File, print_orbitals=False, interact=False):
        self.InfoDict = {
            "filename": " ",
            "basis": " ",
            "success": False,
            "method": " ",
            "dipole moment": [0., 0., 0.],
            "rotational constants": [0., 0., 0.],
            "point group": " ",
            "orbitals": {
                "alpha": dict(),
                "beta": dict()
            },
            "energies": {
                "final_energy": 0.,
                "final_scf": 0.,
                "ccsd_energy": 0.,
                "ccsd(t)_energy": 0.,
                "scf_cycles": dict(),
                "cc_cycles": dict(),
            },
            "coordinates": [],
            "input zmat": [],
            "final zmat": [],
            "frequencies": [],
            "comment": "",
            "zpe": 0.,
            "natoms": 0,
            "nscf": 0.,
            "ncc": 0.,
            "avg_scf": 0.,
            "avg_cc": 0.,
            "gradient norm": [],
            "paths": {
                "root": " ",
                "json": " ",
                "figures": " ",
                "calcs": " ",
                "output": " ",
                "docs": " "
            },
            "timestamp": time.strftime("%d/%m/%Y") + "\t" + time.strftime("%H:%M:%S")
        }
        for key in self.InfoDict["paths"]:
            self.InfoDict["paths"][key] = os.path.abspath("./" + key) + "/"
        self.InfoDict["paths"]["full"] = self.InfoDict["filename"] = File
        self.InfoDict["filename"] = os.path.split(File)[1].split(".")[0]
        self.parse()
        self.analyse_results()
        if self.InfoDict["success"] is True:
            #self.plot_generation()
            self.save_json()
            html_template.html_report(self.InfoDict, print_orbitals, interact)
        else:
            print("Calculation has not completed, or is a fin.dif calculation!")

    def parse(self):
        scf_iter = 0
        scf_cycle = 0
        cc_cycle = 0
        geo_counter = 0
        skip_counter = 0
        CurrentCoords = []
        AltDipoleFlag = False
        DipoleFlag = False
        AlphaFlag = True
        RotFlag = False
        SCFFlag = False
        CCFlag = False
        OrbFlag = False
        FreqFlag = False
        IZMATFlag = False        # Initial ZMAT file
        FZMATFlag = False        # Final ZMAT file
        ReadCoords = False
        with open(self.InfoDict["paths"]["full"], "r") as ReadFile:
            for LineIndex, Line in enumerate(ReadFile):
                if ("The final electronic energy is") in Line:
                    ReadLine = Line.split()
                    self.InfoDict["energies"]["final_energy"] = float(ReadLine[5])
                    self.InfoDict["success"] = True
                if ("The full molecular point group ") in Line:
                    ReadLine = Line.split()
                    self.InfoDict["point group"] = ReadLine[6]
                if ("BASIS=") in Line:
                    ReadLine = Line.split("=")
                    self.InfoDict["basis"] = ReadLine[1].split()[0]
                if ("CALC_LEVEL") in Line:
                    ReadLine = Line.split("=")
                    self.InfoDict["method"] = ReadLine[1].split()[0]
                if ("EXCITE=") in Line:
                    ReadLine = Line.split("=")
                    self.InfoDict["method"] += "-" + ReadLine[1].split()[0]
                if RotFlag is True:            # if flagged to read the rotational constants
                    ReadLine = Line.split()
                    for index, value in enumerate(ReadLine):
                        self.InfoDict["rotational constants"][index] = value
                    RotFlag = False
                if ("Rotational constants (in MHz)") in Line:
                    RotFlag = True
                if SCFFlag is True:
                    ReadLine = Line.split()
                    if len(ReadLine) == 3:
                        ReadLine = [Item.replace("D", "E") for Item in ReadLine]
                        try:
                            CurrentSCF.append(float(ReadLine[1]))      # Take the energy
                            scf_iter += 1
                        except ValueError:
                            pass
                if ("Total Energy") in Line:
                    SCFFlag = True
                    scf_iter = 0
                    CurrentSCF = []
                if ("SCF has converged") in Line:
                    self.InfoDict["energies"]["scf_cycles"][scf_cycle] = CurrentSCF
                    self.InfoDict["energies"]["final_scf"] = min(CurrentSCF)
                    SCFFlag = False
                    scf_cycle += 1
                if FZMATFlag is True or IZMATFlag is True:
                    if ("********") in Line:
                        skip_counter += 1
                    elif skip_counter == 1:
                        temp_zmat.append(Line)
                    elif skip_counter == 2:
                        skip_counter = 0
                        if FZMATFlag is True:
                            print("saving final ZMAT")
                            self.InfoDict["final zmat"] = temp_zmat
                        if IZMATFlag is True:
                            self.InfoDict["input zmat"] = temp_zmat
                        FZMATFlag = False
                        IZMATFlag = False
                if ("Final ZMATnew file") in Line:
                    temp_zmat = list()
                    skip_counter = 0
                    FZMATFlag = True
                if ("Input from ZMAT") in Line:
                    temp_zmat = list()
                    skip_counter = 0
                    IZMATFlag = True
                if ReadCoords is True:
                    if ("----------") in Line:
                        skip_counter += 1
                    elif skip_counter == 1:
                        ReadLine = Line.split()
                        CurrentCoords.append([ReadLine[0],
                                              str(float(ReadLine[2]) * 0.5291),
                                              str(float(ReadLine[3]) * 0.5291),
                                              str(float(ReadLine[4]) * 0.5291)]
                                             )
                    elif skip_counter == 2:
                        self.InfoDict["coordinates"] = CurrentCoords
                        ReadCoords = False
                        CurrentCoords = []
                        skip_counter = 0
                if ("Coordinates (in bohr)") in Line:
                    skip_counter = 0
                    ReadCoords = True
                if ("Conversion factor used") in Line:
                    self.InfoDict["dipole moment"] = Dipole
                    AltDipoleFlag = False
                if AltDipoleFlag is True:
                    if skip_counter == 0:
                        skip_counter += 1
                    elif skip_counter == 1 and Line != "\n":
                        ReadLine = Line.split()
                        index_list = ["x", "y", "z"]
                        Dipole[index_list.index(ReadLine[0])] = float(ReadLine[2])
                if DipoleFlag is True:
                    ReadLine = Line.split()
                    #if len(ReadLine) == 3:
                    #    Index = ["x", "y", "z"].index(ReadLine[0])
                    #    Dipole[Index] = float(ReadLine[2])
                    Dipole = [float(ReadLine[2]),
                              float(ReadLine[5]),
                              float(ReadLine[8])
                              ]
                    Dipole = [value * 2.54174691 for value in Dipole]
                    self.InfoDict["dipole moment"] = Dipole
                    DipoleFlag = False
#                if ("au             Debye") in Line:
                if ("Components of electric dipole moment") in Line:
                    Dipole = [0., 0., 0.]
                    DipoleFlag = True
                if ("au             Debye") in Line:
                    Dipole = [0., 0., 0.]
                    skip_counter = 0
                    AltDipoleFlag = True
                if ("Molecular gradient norm") in Line:
                    ReadLine = Line.split()
                    self.InfoDict["gradient norm"].append(float(ReadLine[3]))
                    geo_counter += 1
                if CCFlag is True:
                    if skip_counter == 2:
                        self.InfoDict["energies"]["cc_cycles"][cc_cycle] = CurrentCC
                        CCFlag = False
                        cc_cycle += 1
                    elif ("-------") in Line:
                        skip_counter += 1
                    else:
                        ReadLine = Line.split()[:3]
                        CurrentCC.append([float(ReadLine[1]), float(ReadLine[2])])
                if ("Iteration        Energy              Energy") in Line:
                    skip_counter = 0
                    CurrentCC = []
                    CCFlag = True
                if OrbFlag is True:
                    """ Read in orbital information """
                    if ("++++++") in Line:
                        OrbFlag = False
                        AlphaFlag = not AlphaFlag
                        skip_counter = 0
                    if skip_counter == 1:
                        ReadLine = Line.split()
                        OrbitalNo = int(ReadLine[0])
                        Orbital = []
                        Orbital.append(float(ReadLine[2]))
                        Orbital.append(ReadLine[5])
                        Orbital.append(ReadLine[6])
                        if AlphaFlag is True:
                            self.InfoDict["orbitals"]["alpha"][OrbitalNo] = Orbital
                        else:
                            self.InfoDict["orbitals"]["beta"][OrbitalNo] = Orbital
                    if ("----") in Line:
                        skip_counter += 1
                if ("MO #        E(hartree)") in Line:
                    OrbFlag = True
                    skip_counter = 0
                # Harmonic frequency parsing
                if FreqFlag is True:
                    self.InfoDict["frequencies"].append(Line.split()[1])
                if ("Cartesian force constants") in Line:
                    FreqFlag = True
                # ZPE parsing
                if ("Zero-point energy") in Line:   # All in single line
                    FreqFlag = False
                    self.InfoDict["zpe"] = float(Line.split()[5])
                """ The following energy parsing is when the CC program used
                    is the ECC routines.
                """
                if ("CCSD correlation energy") in Line:
                    self.InfoDict["energies"]["ccsd_energy"] = float(Line.split()[3])
                if ("CCSD(T) correlation energy") in Line:
                    self.InfoDict["energies"]["ccsd(t)_energy"] = float(Line.split()[3])
                if ("HF-SCF") in Line:
                    self.InfoDict["energies"]["final_scf"] = float(Line.split()[2])
                """ The following parsers will work for the VCC routines """
                if ("The reference energy") in Line:
                    self.InfoDict["energies"]["final_scf"] = float(Line.split()[4])
                if ("The correlation energy is") in Line:
                    self.InfoDict["energies"]["ccsd(t)_energy"] = float(Line.split()[4])
                if ("E(CCSD)") in Line:
                    self.InfoDict["energies"]["ccsd_energy"] = float(Line.split()[2])
        self.InfoDict["comment"] = self.InfoDict["input zmat"][0]

    def analyse_results(self):
        try:
            self.InfoDict["natoms"] = len(self.InfoDict["coordinates"])
            self.InfoDict["nscf"] = len(self.InfoDict["energies"]["scf_cycles"])
            self.InfoDict["ncc"] = len(self.InfoDict["energies"]["cc_cycles"])

            scf_iteration_data = [len(self.InfoDict["energies"]["scf_cycles"][cycle]) for cycle in self.InfoDict["energies"]["scf_cycles"]]
            cc_iteration_data = [len(self.InfoDict["energies"]["cc_cycles"][cycle]) for cycle in self.InfoDict["energies"]["cc_cycles"]]

            #self.InfoDict["final_scf"] = min(self.InfoDict["energies"]["scf_cycles"][self.InfoDict["nscf"] - 1])
            if self.InfoDict["nscf"] != 0.:
                self.InfoDict["avg_scf"] = np.average(scf_iteration_data)
            if self.InfoDict["ncc"] != 0.:
                self.InfoDict["avg_cc"] = np.average(cc_iteration_data)
        except KeyError:
            pass
            print("Calculation not finished, results incomplete.")

    def print_results(self):
        print(self.InfoDict)

    def plot_generation(self, save_png=True):
        """ Method that will generate a summary of energy convergence """
        first_scf = pd.DataFrame(
            data=self.InfoDict["energies"]["scf_cycles"][0],
            columns=["SCF energy"]
        )
        last_scf = pd.DataFrame(
            data=self.InfoDict["energies"]["scf_cycles"][self.InfoDict["nscf"]-1],
            columns=["SCF energy"]
        )
        scf_figure = figure_settings.GenerateSubPlotObject(
            ["First SCF cycle", "Final SCF cycle"],
            1,
            2,
            "Landscape",
        )
        for index, plot in enumerate([first_scf, last_scf]):
            plot_object = figure_settings.DefaultScatterObject(
                plot.index,
                plot["SCF energy"]
            )
            scf_figure.append_trace(plot_object, 1, index + 1)
            scf_figure["layout"]["xaxis" + str(index + 1)].update(
                {
                    "title": "Iterations"
                }
            )
        scf_figure["layout"].update(
            width=900.,
            height=(900. / 1.6),
            showlegend=False
        )
        scf_figure["layout"]["yaxis"].update(
            {
                "title": "Energy (Ha)"
            }
        )
        if save_png is True:
            figure_settings.save_plotly_png(
                scf_figure,
                self.InfoDict["paths"]["figures"] + self.InfoDict["filename"] + ".scf_report.jpg"
            )
        with open(self.InfoDict["paths"]["figures"] + self.InfoDict["filename"] + ".scf_report.html", "w+") as WriteFile:
            WriteFile.write(
                figure_settings.plot(
                    scf_figure,
                    output_type="div",
                    auto_open=False
                )
            )
        if len(self.InfoDict["gradient norm"]) > 0:
            geometry_opt = pd.DataFrame(
                data=self.InfoDict["gradient norm"]
            )
            geometry_plot = [
                figure_settings.DefaultScatterObject(
                    X=geometry_opt.index,
                    Y=geometry_opt[0],
                    Name="Molecular gradient",
                )
            ]
            geometry_layout = figure_settings.DefaultLayoutSettings()
            geometry_layout["title"] = "Geometry optimisation progress"
            geometry_layout["xaxis"]["title"] = "Iteration"
            geometry_layout["yaxis"]["title"] = "Molecular gradient norm"

            geometry_figure = figure_settings.Figure(
                data=geometry_plot,
                layout=geometry_layout
            )

            if save_png is True:
                figure_settings.save_plotly_png(
                    geometry_figure,
                    self.InfoDict["paths"]["figures"] + self.InfoDict["filename"] + ".geo_report.jpg"
                )
            with open(self.InfoDict["paths"]["figures"] + self.InfoDict["filename"] + ".geo_report.html", "w+") as WriteFile:
                WriteFile.write(
                    figure_settings.plot(
                        {"data": geometry_plot, "layout": geometry_layout},
                        output_type="div",
                        auto_open=False
                    )
                )

    def export_xyz(self, Filename=None):
        if Filename is None:
            Filename = self.InfoDict["filename"] + ".xyz"
        Filename = self.InfoDict["paths"]["docs"] + "/" + Filename
        with open(Filename, "w+") as WriteFile:
            WriteFile.write(str(self.InfoDict["natoms"]) + "\n")
            WriteFile.write("Output geometry for " + self.InfoDict["filename"] + " in Angstroms\n")
            for Line in self.InfoDict["coordinates"]:
                for Piece in Line:
                    WriteFile.write(Piece)
                    WriteFile.write(" ")
                WriteFile.write("\n")

    def print_xyz(self):
        for Line in self.InfoDict["coordinates"]:
            print(Line)

    def save_json(self, Filename=None):
        if Filename is None:
            Filename = self.InfoDict["filename"] + ".results.json"
        Filename = self.InfoDict["paths"]["json"] + Filename
        with open(Filename, "w+") as WriteFile:
            json.dump(self.InfoDict, WriteFile)

def external_parse(filepath):
    InfoDict = {
        "filename": " ",
        "basis": " ",
        "success": False,
        "method": " ",
        "dipole moment": [0., 0., 0.],
        "rotational constants": [0., 0., 0.],
        "point group": " ",
        "orbitals": {
            "alpha": dict(),
            "beta": dict()
        },
        "energies": {
            "final_energy": 0.,
            "final_scf": 0.,
            "ccsd_energy": 0.,
            "ccsd(t)_energy": 0.,
            "scf_cycles": dict(),
            "cc_cycles": dict(),
        },
        "coordinates": [],
        "input zmat": [],
        "final zmat": [],
        "frequencies": [],
        "centrifugal distortion": dict(),
        "zpe": 0.,
        "natoms": 0,
        "nscf": 0.,
        "ncc": 0.,
        "avg_scf": 0.,
        "avg_cc": 0.,
        "gradient norm": [],
        "paths": {
            "root": " ",
            "json": " ",
            "figures": " ",
            "calcs": " ",
            "output": " ",
            "docs": " "
        },
        "timestamp": time.strftime("%d/%m/%Y") + "\t" + time.strftime("%H:%M:%S")
    }
    scf_iter = 0
    scf_cycle = 0
    cc_cycle = 0
    geo_counter = 0
    skip_counter = 0
    CurrentCoords = []
    DipoleFlag = False
    AlphaFlag = True
    RotFlag = False
    SCFFlag = False
    CCFlag = False
    OrbFlag = False
    FreqFlag = False
    IZMATFlag = False        # Initial ZMAT file
    FZMATFlag = False        # Final ZMAT file
    ReadCoords = False
    CDFlag = False           # Centrifugal distortion terms
    with open(filepath, "r") as ReadFile:
        for LineIndex, Line in enumerate(ReadFile):
            if ("The final electronic energy is") in Line:
                ReadLine = Line.split()
                InfoDict["energies"]["final_energy"] = float(ReadLine[5])
                InfoDict["success"] = True
            if ("The full molecular point group ") in Line:
                ReadLine = Line.split()
                InfoDict["point group"] = ReadLine[6]
            if ("BASIS=") in Line:
                ReadLine = Line.split("=")
                InfoDict["basis"] = ReadLine[1].split()[0]
            if ("CALC_LEVEL") in Line:
                ReadLine = Line.split("=")
                InfoDict["method"] = ReadLine[1].split()[0]
            if ("EXCITE=") in Line:
                ReadLine = Line.split("=")
                InfoDict["method"] += "-" + ReadLine[1].split()[0]
            if RotFlag is True:            # if flagged to read the rotational constants
                ReadLine = Line.split()
                for index, value in enumerate(ReadLine):
                    InfoDict["rotational constants"][index] = value
                RotFlag = False
            if ("Rotational constants (in MHz)") in Line:
                RotFlag = True
            if SCFFlag is True:
                ReadLine = Line.split()
                if len(ReadLine) == 3:
                    ReadLine = [Item.replace("D", "E") for Item in ReadLine]
                    try:
                        CurrentSCF.append(float(ReadLine[1]))      # Take the energy
                        scf_iter += 1
                    except ValueError:
                        pass
            if ("Total Energy") in Line:
                SCFFlag = True
                scf_iter = 0
                CurrentSCF = []
            if ("SCF has converged") in Line:
                InfoDict["energies"]["scf_cycles"][scf_cycle] = CurrentSCF
                InfoDict["energies"]["final_scf"] = min(CurrentSCF)
                SCFFlag = False
                scf_cycle += 1
            if FZMATFlag is True or IZMATFlag is True:
                if ("********") in Line:
                    skip_counter += 1
                elif skip_counter == 1:
                    temp_zmat.append(Line)
                elif skip_counter == 2:
                    skip_counter = 0
                    if FZMATFlag is True:
                        print("saving final ZMAT")
                        InfoDict["final zmat"] = temp_zmat
                    if IZMATFlag is True:
                        InfoDict["input zmat"] = temp_zmat
                    FZMATFlag = False
                    IZMATFlag = False
            if ("Final ZMATnew file") in Line:
                temp_zmat = list()
                skip_counter = 0
                FZMATFlag = True
            if ("Input from ZMAT") in Line:
                temp_zmat = list()
                skip_counter = 0
                IZMATFlag = True
            if ReadCoords is True:
                if ("----------") in Line:
                    skip_counter += 1
                elif skip_counter == 1:
                    ReadLine = Line.split()
                    CurrentCoords.append([ReadLine[0],
                                          float(ReadLine[2]) * 0.5291,
                                          float(ReadLine[3]) * 0.5291,
                                          float(ReadLine[4]) * 0.5291]
                                         )
                elif skip_counter == 2:
                    InfoDict["coordinates"] = CurrentCoords
                    ReadCoords = False
                    CurrentCoords = []
                    skip_counter = 0
            if ("Coordinates (in bohr)") in Line:
                skip_counter = 0
                ReadCoords = True
#                if ("Conversion factor used") in Line:
#                    self.InfoDict["dipole moment"] = Dipole
#                    DipoleFlag = False
            if DipoleFlag is True:
                ReadLine = Line.split()
                #if len(ReadLine) == 3:
                #    Index = ["x", "y", "z"].index(ReadLine[0])
                #    Dipole[Index] = float(ReadLine[2])
                Dipole = [float(ReadLine[2]),
                          float(ReadLine[5]),
                          float(ReadLine[8])
                          ]
                Dipole = [value * 2.54174691 for value in Dipole]
                InfoDict["dipole moment"] = Dipole
                DipoleFlag = False
#                if ("au             Debye") in Line:
            if ("Components of electric dipole moment") in Line:
                Dipole = [0., 0., 0.]
                DipoleFlag = True
            if ("Molecular gradient norm") in Line:
                ReadLine = Line.split()
                InfoDict["gradient norm"].append(float(ReadLine[3]))
                geo_counter += 1
            if CCFlag is True:
                if skip_counter == 2:
                    InfoDict["energies"]["cc_cycles"][cc_cycle] = CurrentCC
                    CCFlag = False
                    cc_cycle += 1
                elif ("-------") in Line:
                    skip_counter += 1
                else:
                    ReadLine = Line.split()[:3]
                    CurrentCC.append([float(ReadLine[1]), float(ReadLine[2])])
            if ("Iteration        Energy              Energy") in Line:
                skip_counter = 0
                CurrentCC = []
                CCFlag = True
            if OrbFlag is True:
                """ Read in orbital information """
                if ("++++++") in Line:
                    OrbFlag = False
                    AlphaFlag = not AlphaFlag
                    skip_counter = 0
                if skip_counter == 1:
                    ReadLine = Line.split()
                    OrbitalNo = int(ReadLine[0])
                    Orbital = []
                    Orbital.append(float(ReadLine[2]))
                    Orbital.append(ReadLine[5])
                    Orbital.append(ReadLine[6])
                    if AlphaFlag is True:
                        InfoDict["orbitals"]["alpha"][OrbitalNo] = Orbital
                    else:
                        InfoDict["orbitals"]["beta"][OrbitalNo] = Orbital
                if ("----") in Line:
                    skip_counter += 1
            if ("MO #        E(hartree)") in Line:
                OrbFlag = True
                skip_counter = 0
            if ("Zero-point energy") in Line:   # All in single line
                FreqFlag = False
                ZPE = float(Line.split()[5])
            # Harmonic frequency parsing
            if FreqFlag is True:
                InfoDict["frequencies"].append(Line.split()[1])
            if ("Cartesian force constants") in Line:
                FreqFlag = True
            # ZPE parsing
            if ("Zero-point energy") in Line:   # All in single line
                FreqFlag = False
                InfoDict["zpe"] = float(Line.split()[5])
            """ The following energy parsing is when the CC program used
                is the ECC routines.
            """
            if ("CCSD correlation energy") in Line:
                InfoDict["energies"]["ccsd_energy"] = float(Line.split()[3])
            if ("CCSD(T) correlation energy") in Line:
                InfoDict["energies"]["ccsd(t)_energy"] = float(Line.split()[3])
            if ("HF-SCF") in Line:
                InfoDict["energies"]["final_scf"] = float(Line.split()[2])
            """ The following parsers will work for the VCC routines """
            if ("The reference energy") in Line:
                InfoDict["energies"]["final_scf"] = float(Line.split()[4])
            if ("The correlation energy is") in Line:
                InfoDict["energies"]["ccsd(t)_energy"] = float(Line.split()[4])
            if ("E(CCSD)") in Line:
                InfoDict["energies"]["ccsd_energy"] = float(Line.split()[2])
            if CDFlag is True:
                if skip_counter == 2:
                    CDFlag = False
                else:
                    split_line = Line.split()
                    if len(split_line) <= 2:
                        skip_counter += 1
                    else:
                        InfoDict["centrifugal distortion"][reduction][split_line[0]] = float(split_line[1])
            if "A-reduced centrifugal" in Line or "S-reduced centrifugal" in Line:
                if "A-reduced centrifugal" in Line:
                    reduction = "A"
                elif "S-reduced centrifugal" in Line:
                    reduction = "S"
                skip_counter = 0
                InfoDict["centrifugal distortion"][reduction] = dict()
                CDFlag = True
        #InfoDict["comment"] = InfoDict["input zmat"][0]
    return InfoDict

if __name__ == "__main__":
    import sys
    output_instance = OutputFile(str(sys.argv[1]))
    output_instance.export_xyz()
    output_instance.save_json()
