# CFOUR Viewer

## Version 0.1

This is the initial version of CFOUR viewer - a PyQt5 frontend to the electronic structure program "CFOUR".

The goal of this program is to simpify the process of setting up and running calculations in CFOUR. As it stands of this version, it is merely two main Python functions: a way to set up calculations on a cluster, and a way to parse the output in a very rudimentary way.

The philosophy behind the calculation set up is to reproducibly create a file directory system that will let anyone (hopefully) view the original and condensed outputs of a calculation.

## Planned features:

1. PyQt5 frontend to setting up a calculation and parsing.
2. Related to the above is a bonafide ZMAT editor
3. Automated harmonic frequencies by finite differences

## Setup

The code was written in Python 3.6, and while it should be backwards compatible with Python 2.7 (or even 2.6, God forbid) I strongly recommend moving to Python 3 (as the general movement of the rest of the Python world is moving towards...). The environment I built this in is a stock Anaconda installation without any real additional packages.

1. Install Python, which I highly recommend the Anaconda distribution of Python 3.
2. Clone this git.
3. Make sure that you check, in the `cfour_viewer/settings.json` file that the directories are indeed correct for what you want to do.


## Troubleshooting

### `libgcc`

I have found that the newer versions of PyQt5 (5.8) seem to be compiled with a different version of `libgcc` which the cluster I work with does not appear to be happy about. In the case of accidentally upgrading PyQt to 5.8, I would strongly recommend using the stock Anaconda 3 installation again. I've tried installing a specific version of PyQt5 (5.7), and I guess linking issues arise.
