

from string import Formatter
#from xhtml2pdf import pisa
import pandas as pd


table_css = '''<style>
table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    text-align: left;
    padding: 8px;
}

tr:nth-child(even){background-color: #b2df8a}

tr:hover {background-color: #a6cee3}

th {
    background-color: #33a02c;
    color: white;
}
</style>
'''


class YourFormatter(Formatter):
    def get_value(self, field_name, args, kwargs):
        return kwargs.get(field_name, '')

    def get_field(self, field_name, args, kwargs):
        first, rest = field_name._formatter_field_name_split()
        obj = self.get_value(first, args, kwargs)

        for is_attr, i in rest:
            if is_attr:
                obj = getattr(obj, i)
            else:
                obj = obj.get(i, '')
        return obj, first


def html_report(json_results, print_orbitals=False, interact=False):
    header = """
    <header>
        <h1>
            Report for: {filename}
        </h1>
        <p>
            This is a {method}/{basis} calculation.
            The calculation finished with success: {success}.
            The point group used was {point group}.
        </p>
        <p>
            Calculation finished at {timestamp}.
        </p>
    </header>
    """

    electronic = """
        <h3>
            Electronic energy
        </h3>
        <p>
            Final electronic energy: {energies[final_energy]} Ha
            Final SCF energy: {energies[final_scf]} Ha
        </p>
        <p>
            SCF took {nscf} cycles, averaging at {avg_scf} iterations per cycle.
        </p>
        <p>
            CC took {ncc} cycles, averaging at {avg_cc} iterations per cycle.
        </p>
    """

    structure = """
        <h3>
            Molecular structure
        </h3>
        <table style="width:100%">
            <caption> Rotational constants in MHz </caption>
            <tr>
                <th> A </th> <th> B </th> <th> C </th>
            </tr>
            <td> {rotational constants[2]} </td>
            <td> {rotational constants[1]} </td>
            <td> {rotational constants[0]} </td>
        </table>
        <table style="width:100%">
            <caption> Dipole moments in Debye </caption>
            <tr>
                <th> $x$ </th> <th> $y$ </th> <th> $z$ </th>
            </tr>
            <td> {dipole moment[0]} </td>
            <td> {dipole moment[1]} </td>
            <td> {dipole moment[2]} </td>
        </table>
    """

    fullstring = ""
    try:
        for part in [header, electronic, structure]:
            fullstring = fullstring + part.format_map(json_results)
    except IndexError:
        pass

    if interact is True:
        with open(json_results["paths"]["figures"] + json_results["filename"] + ".scf_report.html", "r") as ReadFile:
            fullstring = fullstring + ReadFile.read()

        if len(json_results["gradient norm"]) > 0:
            with open(json_results["paths"]["figures"] + json_results["filename"] + ".geo_report.html", "r") as ReadFile:
                fullstring = fullstring + ReadFile.read()

    if print_orbitals is True:
        orbital_df = pd.DataFrame(
            json_results["orbitals"],
            index=["Energy (Ha)", "Irreducible rep.", "Rep. #"]
            ).T
        orbital_html = orbital_df.to_html()
        fullstring = fullstring + "<h3> Occupied orbitals </h3>" + orbital_html

    if len(json_results["frequencies"]) > 1:
        freq_df = pd.DataFrame(
            json_results["frequencies"],
            columns=["Frequency (1/cm)"]
            )
        freq_html = freq_df.to_html()
        fullstring = fullstring + "<h3> Frequencies </h3>" + freq_html

    with open("./docs/" + json_results["filename"] + "_report.html", "w+") as WriteFile:
        WriteFile.write(fullstring)

def multi_report(filepath, json_reports, names):
    """ Takes a list of JSON reports, and basically formats an HTML table
        as a report.
    """
    pd.set_option("display.max_columns", 100)
    pd.set_option("precision", 15)
    pd.set_option("max_colwidth", 500)
    InfoDicts = dict()
    for name, report in zip(names, json_reports):
        InfoDicts[name] = {
        "Total electronic energy (Eh)": report["energies"]["final_energy"],
        "Reference electronic energy (Eh)": report["energies"]["final_scf"],
        "Frequencies (1/cm)": report["frequencies"],
        "Zero-point energy (kJ/mol)": report["zpe"],
        "Rotational constants (MHz)": report["rotational constants"],
        "Dipole moments (Debye)": report["dipole moment"],
        "Method": report["method"],
        "Basis": report["basis"],
        "Comment": str(report["comment"]),
        "CCSD correlation energy (Eh)": report["energies"]["ccsd_energy"],
        "CCSD(T) correlation energy (Eh)": report["energies"]["ccsd(t)_energy"]
        }
    full_dataframe = pd.DataFrame.from_dict(InfoDicts)
    html_table = full_dataframe.to_html(bold_rows=True)
    full_dataframe.to_csv(filepath + ".csv")
    fulltext = table_css + html_table
    with open(filepath + ".html", "w+") as WriteFile:
        WriteFile.write(fulltext)


# Utility function
#def convert_html_to_pdf(source_html_file, output_filename):
    # open output file for writing (truncated binary)
#    with open(source_html_file, "r") as source_file:
#        source_html = source_file.read()

#    with open(output_filename, "w+b") as result_file:
        # convert HTML to PDF
#        pisa_status = pisa.CreatePDF(
#            source_html,                # the HTML to convert
#            dest=result_file            # file handle to recieve result
#        )

    # return True on success and False on errors
#    return pisa_status.err
