import uproot
from hepdata_lib import Table, Variable

def ak8_tag(sub):
    nice_process = {
        "WQQ" : "W(qq)",
        "ZQQ" : "Z(qq)",
        "Zvv" : "QCD jets"
    }

    f = uproot.open("input/ak8/ak8eff_converted.root")
    table = Table("DeepAK8 tagging efficiencies")
    table.description = "Tagging efficiency for AK8 jets. The efficiency includes the effect of the machine-learning based DeepAK8 tagger, as well as the application of the mass window requirement on the jet. The efficiency is split depending on the matching generator-level object. For reinterpretation purposes, this efficiency can directly be applied to any AK8 jet that is matched to a given type of generator-level object, with no prior selection on the jet mass. Other acceptance requirements on jet $\pt$ and $\eta$ should still be applied."
    table.location = "Supplementary material."
    x = None
    for year in 2017, 2018:
        for wp in "loose", "tight":
            for proc in 'WQQ','ZQQ','Zvv':
                h = f[f'ak8eff_mc_{proc}_{wp}_{year}']
                if x is None:
                    x = Variable("AK8 jet p_{T}", units="GeV")
                    x.values = h.bins
                    table.add_variable(x)
                y = Variable("Efficiency", is_binned=False, is_independent=False)
                y.values = h.values
                y.add_qualifier("Process", nice_process[proc])
                y.add_qualifier("Data-taking period", year)
                y.add_qualifier("Working point", wp)
                table.add_variable(y)

    sub.add_table(table)