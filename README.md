# CFOUR Viewer

This is the initial version of CFOUR viewer - a PyQt5 frontend to the electronic structure program "CFOUR".

The goal of this program is to simpify the process of setting up and running calculations in CFOUR. As it stands of this version, it is merely two main Python functions: a way to set up calculations on a cluster, and a way to parse the output in a very rudimentary way.

The philosophy behind the calculation set up is to reproducibly create a file directory system that will let anyone (hopefully) view the original and condensed outputs of a calculation.

## Planned features:

1. PyQt5 frontend to setting up a calculation and parsing.
2. Related to the above is a bonafide ZMAT editor

## Setup

The code was written in Python 3.6, and while it should be backwards compatible with Python 2.7, I strongly recommend moving to Python 3 (as the general movement of the rest of the Python world is moving towards...). The environment I built this in is a stock Anaconda installation without any real additional packages.

1. Install Python, which I highly recommend the Anaconda distribution of Python 3.
2. Clone this git.
3. Make sure that you check, in the `cfour_viewer/settings.json` file that the directories are indeed correct for what you want to do.

## Version history

### Planned features/updates

- Documentation (as in, write everything up)
- Code commenting
- A `PyQt5` frontend to all of these scripts
- Set up for calculation "schemes", such as HEAT
- Clean up the script generation templates, and relocate the settings file to home directory.

### Current: 0.3.0

- Automatic isotopologue analysis on harmonic frequency calculations by finite differences
    - Incorporates a new python library `periodictable` for the masses of each isotope along with their natural abundance.
    - The scripts will automatically detect the atoms in your ZMAT file, and generate an `ISOMASS` file that is read in by CFOUR, and taking a previous harmonic frequency calculation, perform the frequency analysis with the every naturally abundant and spectroscopically relevant isotoplogue.
    - The work flow is simply start a finite differences calculation (`harmdiffCFOUR`), followed by analysis (`analysefreqoutput`), and the isotoplogue script (`harmfreqisotopes`).

    ## Troubleshooting

    ### `libgcc`

    I have found that the newer versions of PyQt5 (5.8) seem to be compiled with a different version of `libgcc` which the cluster I work with does not appear to be happy about. In the case of accidentally upgrading PyQt to 5.8, I would strongly recommend using the stock Anaconda 3 installation again. I've tried installing a specific version of PyQt5 (5.7), and I guess linking issues arise.
