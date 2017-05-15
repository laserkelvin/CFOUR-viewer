""" In the spirit of reproducibility, these routines will automatically
	generate a file directory tree for performing calculations on a given
	molecule.

	The idea will be to have one notebook per "experiments", which will
	collate all of the results and produce some interpretation based on
	whatever has been done.

"""

import os
from glob import glob

top_level = [
	"figures",        # from the notebook outputs
	"suppinfo",       # whatever extra data required
	"calcs",          # store the calculation data
	"json",        # collated information from calculations
	"docs"            # possibly reports of the analysis
]

navigation = {
	"top": os.path.abspath("./")
}


def setup_folders():
	""" set up the file structure as defined above
	"""
	for folder in top_level:
		try:
			os.mkdir(folder)
		except FileExistsError:
			print(folder + " already exists.")
			pass

def generate_folder():
	""" Generates the folder for the next calculation
	and returns the next calculation number
	"""
	folderlist = glob("*")      # get every file/folder in directory
	if len(folderlist) == 0:
		lastcalc = 0
	else:
		# filter out any non-folders that happen to be here
		folderlist = [int(fd) for fd in folderlist if os.path.isdir(fd) is True]
		lastcalc = len(folderlist)
	os.mkdir(str(lastcalc + 1))
	return lastcalc + 1
