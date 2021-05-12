import os
import re

import numpy as np

pjoin = os.path.join
import uproot
from hepdata_lib import Table, Uncertainty, Variable

from helpers import treat_overflow


def interpretation_name(signal):
    if 'add' in signal:
        return "ADD"
    if 'axial' in signal:
        return "Axial"
    if 'vector' in signal:
        return "Vector"
    else:
        return ''

def load_signal_histograms(year):
    indir = "input/2021-05-03_master/"
    category = 'monojet'
    infile = pjoin(
            indir,
            f"legacy_limit_{category}_{year}.root"
    )
    f = uproot.open(infile)
    histograms = {}
    for name, histo in f.items():
        name = re.sub(";.*", "",name)
        if not name.startswith("signal"):
            continue
        name = re.sub("^signal_","", name)
        if 'data' in name:
            continue
        if re.match("(ggh|vbf|wh|zh|ggzh)\d+", name):
            continue
        histograms[name] = histo
    
    return histograms


def make_variable(name):
    var = Variable("Signal yield", is_independent=False, is_binned=False)
    rgx = re.compile("(.*)_(mono.*)_mmed([\d,p]+)_mdm([\d,p]+)_gq(1p0|0p25)_gdm1p0")
    if any([x in name for x in ('axial','vector','scalar','pseudo')]):
        m = rgx.match(name)
        
        try:
            coupling, channel, mmed, mdm, _ = m.groups()
        except:
            print(f"Parsing of data set name failed: {name}")
            raise

        if channel == 'monojet':
            channel = 'DM + QCD jets'
        elif channel == 'monow':
            channel = 'DM + W(qq)'
        elif channel == 'monoz':
            channel = 'DM + Z(qq)'
        mmed = float(mmed.replace('p','.'))
        mdm = float(mdm.replace('p','.'))
        var.add_qualifier("Coupling type", coupling.capitalize())
        var.add_qualifier("Production mode", channel.capitalize())
        var.add_qualifier("$m_{med}$", mmed)
        var.add_qualifier("$m_{DM}$", mdm)
        var.add_qualifier("$g_{q}$", 0.25)
        var.add_qualifier("$g_{DM}$", 1.0)
    return var

def make_signal_template_tables(sub):
    
    # Map nice names to regular expressions
    # regex matches data set names in the limit input files
    signal_models = {
        "DMsimp, spin-1" : "(axial|vector).*",
        "DMsimp, spin-0" : "(scalar|pseudo).*",
        "ADD" : "add.*",
    }

    for category in ['monojet','monovloose','monovtight']:
        for model, rgx in signal_models.items():
            table = Table(f"Signal templates, {model}, {category}")
            first = True
            for year in 2017, 2018:
                histograms = load_signal_histograms(year)
                for name, histo in histograms.items():
                    if not re.match(rgx, name):
                        continue
                    model = interpretation_name(name)
                    if first:
                        xvar = Variable("Recoil (GeV)", is_independent=True, is_binned=True)
                        xvar.values = histo.axis().intervals()
                        first = False
                        table.add_variable(xvar)

                    yvar = make_variable(name)
                    yvar.add_qualifier("Data set", year)
                    stat_unc = Uncertainty(
                        "Sample size",
                        is_symmetric=True
                    )
                    stat_unc.values = np.sqrt(treat_overflow(histo.variances(flow=True)[1:]))
                    yvar.values = treat_overflow(histo.values(flow=True)[1:])
                    yvar.add_uncertainty(stat_unc)
                    table.add_variable(yvar)
            table.location = 'Supplementary material'
            table.description = 'Differential signal yields for various signal hypotheses.'
            sub.add_table(table)
