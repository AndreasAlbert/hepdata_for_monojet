import numpy as np
from hepdata_lib import Table, Variable, Uncertainty
import os
from hepdata_lib.root_utils import get_hist_1d_points, get_graph_points
import yaml

yaml.add_representer(
                    np.float64, lambda dumper, data: dumper.represent_float(data)
                    )
pjoin = os.path.join
import ROOT as r
def load_histograms(category, year, region, fit):
    indir = "input/2021-05-03_master/"
    category = 'monojet'
    infile = pjoin(
            indir,
            f"fitDiagnostics_monojet_monov_combined_unblind.root"
    )
    
    f = r.TFile(infile)
    tdir = f.Get(f"shapes_{fit}/{category}_{year}_{region}")
    histograms = {}
    for key in tdir.GetListOfKeys():
        name = key.GetName()
        obj = key.ReadObj()
        if type(obj) == r.TGraphAsymmErrors:
            histograms[name] = get_graph_points(obj)
        else:
            histograms[name] = get_hist_1d_points(obj)
    
    return histograms


def make_yield_tables(sub):
    
    # f = uproot.open("input/2021-05-03_master/fitDiagnostics_monojet_monov_combined_unblind.root")
    categories = {
        'Mono-V (high purity)' : 'monovtight',
        'Mono-V (low purity)' : 'monovloose',
        'Monojet' : 'monojet',
    }

    regions = [
        'singlemu',
        'singleel',
        'dimuon',
        'dielec',
        'photon',
        'signal'
    ]
    for nice_name, category in categories.items():
        table = Table(f"Process yields ({nice_name})")
        first = True
        for year in [2017, 2018]:
            for region in regions:
                for fit in ['fit_b','prefit']:
                    print(category, year, region, fit)
                    histos = load_histograms(category, year, region, fit)

                    for proc, h in histos.items():
                        if proc=='total':
                            continue
                        if proc=='total_covar':
                            continue
                        if proc=='total_signal':
                            continue
                        is_data = 'data' in proc
                        if first and not is_data:
                            xvar = Variable("Recoil", units="GeV", is_independent=True, is_binned=True)
                            xvar.values = h['x_edges']
                            first = False
                            table.add_variable(xvar)
                            
                        def make_var():
                            yvar = Variable("Yield", is_independent=False, is_binned=False)
                            yvar.add_qualifier("Data set year", year)
                            yvar.add_qualifier("Category", category)
                            yvar.add_qualifier("Region", region)
                            yvar.add_qualifier("Fit", fit)
                            yvar.add_qualifier("Process", proc)
                            return yvar

                        yvar = make_var()
                        yvar.values = h['y']

                        if not is_data:
                            unc = Uncertainty(
                                "Total",
                                is_symmetric=True
                            )
                            unc.values = h['dy']
                            yvar.add_uncertainty(unc)
                        table.add_variable(yvar)
            
            # Bin width normalization
            bin_widths = np.array([x[1] - x[0] for x in xvar.values])
            for variable in table.variables:
                if variable.is_independent:
                    continue
                variable.values = np.array(variable.values) * bin_widths
                for unc in variable.uncertainties:
                    unc.values = np.array(unc.values) * bin_widths
            # Sanity check
            lengths = set([len(x.values) for x in table.variables])
            try:
                assert(len(lengths)==1)
            except AssertionError:
                print("Found length mismatch: ", lengths)
                for var in table.variables:
                    print(var.name, len(var.values))
        sub.add_table(table)




