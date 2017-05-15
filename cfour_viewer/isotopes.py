
import periodictable as pt
from collections import OrderedDict
from itertools import product

def find_element(symbol):
    """ Find elements in periodic table based on atomic symbol """
    for element in pt.elements:
        if element.symbol == symbol:
            return element
        else:
            pass

def isotope_masses(element, threshold=0.5):
    """ Returns a sorted dictionary of each isotope of an element, sorted by
        their relative natural abundance.
    """
    mass_dict = dict()
    # Special case for hydrogen
    if element.symbol == "H":
        mass_dict["H"] = {"mass": pt.H.mass, "abundance": 1.}
        mass_dict["D"] = {"mass": pt.D.mass, "abundance": 1.}
    else:
        # For all other elements, there's this case
        for isotope in element.isotopes:
            # Threshold isotopes with experimentally relevant abundance
            if element[isotope].abundance >= threshold:
                mass_dict[str(isotope) + element.symbol] = {
                    "mass": element[isotope].mass,
                    "abundance": element[isotope].abundance / 100.
                }
            # Special cases for commonly used isotopes in structural determination
            elif element.symbol is "O":
                mass_dict[str(18) + "O"] = {
                    "mass": pt.O[18].mass,
                    "abundance": pt.O[18].abundance
                }
            elif element.symbol is "N":
                mass_dict[str(15) + "N"] = {
                    "mass": pt.N[15].mass,
                    "abundance": pt.N[15].abundance
                }
    # Make an ordered dictionary with isotopes sorted by natural abundance
    sorted_dict = OrderedDict(
        sorted(mass_dict.items(), key=lambda t: t[1]["abundance"], reverse=True)
    )
    return sorted_dict

def isotope_combinations(atoms_list, threshold=0.5):
    """ Generates all combinations of isotopes to return a dictionary of
        isotopolgues with lists of masses
    """
    atom_masses = list()      # List of ordered dictionaries containing isotopes
    isotope_dict = dict()     # A flat dictionary holding mass for each unit isotope
    return_dict = dict()      # Dictionary of lists of masses; keys are isotopologues
    for atom in atoms_list:
        # Find isotopic information for each atom
        element = find_element(atom)
        atom_masses.append(isotope_masses(element, threshold))
    for atom in atom_masses:
        # Generate a flat dictionary of unique isotopes and their mass
        for isotope in atom:
            isotope_dict[isotope] = atom[isotope]["mass"]
    # Generate combinations of each isotopologue
    isotope_combos = list(product(*[element.keys() for element in atom_masses]))
    print("A total of " + str(len(isotope_combos)) + " combinations generated.")
    for combination in isotope_combos:
        # For each isotopologue, give produce the corresponding masses
        masses = list()
        for isotope in combination:
            masses.append(isotope_dict[isotope])
        return_dict[combination] = masses
    return return_dict
