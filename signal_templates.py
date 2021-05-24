import os
import re

import numpy as np

pjoin = os.path.join
import uproot
from hepdata_lib import Table, Uncertainty, Variable

from helpers import treat_overflow
from util import legacy_dataset_name


def interpretation_name(signal):
    if 'add' in signal:
        return "ADD"
    if 'axial' in signal:
        return "Axial"
    if 'vector' in signal:
        return "Vector"
    if 'scalar' in signal:
        return "Scalar"
    if 'scalar' in signal:
        return "Pseudo"
    if 'lq' in signal:
        return 'Leptoquark'
    if 'S3D' in signal:
        return "Fermion portal (S3D UR)"
    else:
        return ''

def load_signal_histograms(year,category):
    histograms = {}
    if year == 2016:
        top = "../2021-04-01_2016_templates/output/2021-04-01_2016_templates_v9_halfcorrfix/root/"
        if category=='monojet':
            f = uproot.open(os.path.join(top,"templates_for_2016_sr_j.root"))
        elif category=='monov':
            f = uproot.open(os.path.join(top,"templates_for_2016_sr_v.root"))
        else:
            return {}

        for name, histo in f.items():
            try:
                name = name.decode("utf-8")
            except:
                continue
            try:
                name = legacy_dataset_name(name)
            except RuntimeError:
                print(f"Skip {name}")
            histograms[name] = histo
    else:
        indir = "input/2021-05-03_master/"
        infile = pjoin(
                indir,
                f"legacy_limit_{category}_{year}.root"
        )
        if not os.path.exists(infile):
            return {}
        f = uproot.open(infile)
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
    if any([x in name for x in ('axial','vector','scalar','pseudo')]):
        rgx = re.compile("(.*)_(mono.*)_mmed([\d,p]+)_mdm([\d,p]+)_gq(1p0|0p25)_gdm1p0")
        m = rgx.match(name)
        
        try:
            coupling, channel, mmed, mdm, gq = m.groups()
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
        var.add_qualifier("Production mode", channel)
        var.add_qualifier("$m_{med}$", mmed)
        var.add_qualifier("$m_{DM}$", mdm)
        var.add_qualifier("$g_{q}$", gq.replace("p","."))
        var.add_qualifier("$g_{DM}$", 1.0)
    elif 'add' in name:
        rgx = re.compile("add_md(\d+)_d(\d+)")
        m = rgx.match(name)
        try:
            md, d = m.groups()
        except:
            print(f"Parsing of data set name failed: {name}")
            raise
        
        var.add_qualifier("d",d)
        var.add_qualifier("$M_{D}$",md, units="TeV")
    elif 'lq' in name:
        rgx = re.compile("lq_m(\d+)_d(\d+)")
        m = rgx.match(name)
        try:
            mlq, ylq = m.groups()
        except:
            print(f"Parsing of data set name failed: {name}")
            raise
        
        var.add_qualifier("$\lambda$",ylq)
        var.add_qualifier("$m_{LQ}$",mlq, units="GeV")
    elif 'S3D' in name:
        rgx = re.compile(f'S3D_UR_(cc|pp)_mphi(\d+)_mchi(\d+)_lam([\d,p]+)')
        try:
            channel, mphi, mchi, lam = m.groups()
        except:
            print(f"Parsing of data set name failed: {name}")
            raise
        lam = lam.replace("p",".")

        var.add_qualifier("$m_{\Phi}$",      mphi, units="GeV")
        var.add_qualifier("$m_\mathrm{DM}$", mchi, units="GeV")
        var.add_qualifier("$\lambda$",       lam)
        
    return var

def nice_category_name(category):
    if category=='monovloose':
        return "Mono-V (low-purity)"
    elif category=='monovtight':
        return "Mono-V (high-purity)"
    elif category=='monov':
        return r"Mono-V ($\tau_{21}$)"
    elif category=='monojet':
        return "Monojet"
def make_signal_template_tables(sub):
    
    # Map nice names to regular expressions
    # regex matches data set names in the limit input files
    signal_models = {
        "DMsimp, spin-1" : "(axial|vector).*",
        "DMsimp, spin-0" : "(scalar|pseudo).*",
        "ADD" : "add.*",
        "LQ" : "lq.*"
    }

    for category in ['monojet','monov','monovloose','monovtight']:
        for model, rgx in signal_models.items():
            table = Table(f"Signal templates, {model}, {nice_category_name(category)}")
            first = True
            for year in 2016,:
                histograms = load_signal_histograms(year, category)
                for name, histo in histograms.items():
                    if not re.match(rgx, name):
                        continue
                    model = interpretation_name(name)
                    if first:
                        xvar = Variable("Recoil (GeV)", is_independent=True, is_binned=True)
                        # xvar.values = histo.axis().intervals()
                        xvar.values = histo.bins
                        first = False
                        table.add_variable(xvar)

                    yvar = make_variable(name)
                    yvar.add_qualifier("Data set", year)
                    stat_unc = Uncertainty(
                        "Sample size",
                        is_symmetric=True
                    )
                    stat_unc.values = np.sqrt(treat_overflow(histo.allvariances[1:]))
                    yvar.values = treat_overflow(histo.allvalues[1:])
                    yvar.add_uncertainty(stat_unc)
                    table.add_variable(yvar)
            if first:
                continue
            table.location = 'Supplementary material'
            table.description = 'Differential signal yields for various signal hypotheses.'
            sub.add_table(table)
