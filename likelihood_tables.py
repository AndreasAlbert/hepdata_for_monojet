import re
from hepdata_lib import RootFileReader, Table, Variable

def bin_name(name):
    
    m = re.match("ch1_ch(1|2)_ch1_(\d+)", name)
    if m:
        year = 2016
        channel = "monojet" if m.groups()[0]==1 else "monovtau21"
        bin_id = m.groups()[1]

    m = re.match("ch2_([a-z]*)_(\d+)_signal_(\d+)", name)
    if m:
        channel, year, bin_id = m.groups()

    return f"{channel}_{year}_bin{bin_id}"


def make_likelihood_table_single(sub, infile, tag):
    reader = RootFileReader(infile)
    covar = reader.read_hist_2d("shapes_fit_b/total_covar")

    table = Table(name=f"Likelihood: covariance matrix ({tag})")
    table.description = "Matrix of covariance coefficients between signal region bins. The coefficients are obtained from the background-only fit to the corresponding control regions, and serve as input to the simplified likelihood reinterpretation scheme."
    table.location='Supplementary material'


    x = Variable("First Bin", is_independent=True, is_binned=False)
    x.values = [bin_name(x) for x in covar["x_labels"]]

    y = Variable("Second Bin", is_independent=True, is_binned=False)
    y.values = [bin_name(x) for x in covar["y_labels"]]

    correlation = Variable("Correlation coefficient", is_independent=False, is_binned=False)
    correlation.values = covar["z"]

    table.add_variable(x)
    table.add_variable(y)
    table.add_variable(correlation)
    sub.add_table(table)

    bg = reader.read_hist_1d("shapes_fit_b/total_background")
    data = reader.read_hist_1d("shapes_fit_b/total_background")

    table = Table(name=f"Likelihood: Background and data yields ({tag})")
    table.description = "Background prediction and observed data yields in the signal region bins. The background yields are obtained from the background-only fit to the corresponding control regions, and serve as input to the simplified likelihood reinterpretation scheme."
    table.location='Supplementary material'

    x = Variable("Bin", is_independent=True, is_binned=False)
    y1 = Variable("Background yield", is_independent=False, is_binned=False)
    y2 = Variable("Data yield", is_independent=False, is_binned=False)

    x.values = [bin_name(x) for x in bg["x_labels"]]
    y1.values = bg['y']
    y2.values = data['y']
    table.add_variable(x)
    table.add_variable(y1)
    table.add_variable(y2)
    sub.add_table(table)

def make_likelihood_tables(sub):
    tag = "Monojet + mono-V"
    infile = "input/likelihood/SLinput_from_scalar_mmed100_mdm1_gg1p0_ggdm1p0.root"
    make_likelihood_table_single(sub, infile, tag)
    

