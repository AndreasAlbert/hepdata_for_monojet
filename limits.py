from hepdata_lib import Variable, Table
import pandas as pd
import numpy as np
import os
pjoin = os.path.join

tag = "2021-05-03_master_default_default"

nice_quantile = {
    "exp" : "Median Expected",
    "obs" : "Observed",
    "p1s" : "Expected plus 1 s.d.",
    "m1s" : "Expected minus 1 s.d.",
    "p2s" : "Expected plus 2 s.d.",
    "m2s" : "Expected minus 2 s.d.",
}

def limits_dmsimp_2d(sub):
    top = f"/home/albert/repos/monojet/limitplot/dmsimp/output/{tag}/spin1/"
    for coupling in ['axial','vector']:
        for quantile in ["exp","obs","p1s","m1s"]:
            table = Table(f"2D exclusion contour, {coupling}, {nice_quantile[quantile]}")
            table.description = f"{nice_quantile[quantile]} exclusion contour in the $m_{{med}}$-$m_{{\chi}} plane in the simplified model with {coupling} couplings."
            data = np.loadtxt(pjoin(top, f"contour_{coupling}_{quantile}.txt"))
            mmed = Variable("$m_{med}$", is_independent=True, is_binned=False)
            mmed.values = data[:,0]
            mdm = Variable("$m_{\chi}$", is_independent=False, is_binned=False)
            mdm.values = data[:,1]
            table.add_variable(mmed)
            table.add_variable(mdm)
            sub.add_table(table)

nice_coupling_type = {
    "gq" : "$g_{q}$",
    "gchi" : "$g_{\chi}$",
}
def limits_dmsimp_coupling(sub):
    top = f"/home/albert/repos/monojet/limitplot/dmsimp/output/{tag}/spin1/"
    df = pd.read_pickle(pjoin(top, "coupling_limit_df.pkl"))
    df = df[df.mdm!=1]
    for (coupling, coupling_type), idf in df.groupby(["coupling","coupling_type"]):
        table = Table(f"coupling limits on {nice_coupling_type[coupling_type]}, {coupling} mediator")
        table.description = "Upper limits on the coupling {nice_coupling_type[coupling_type]} in the simplified model with a {coupling} mediator."
        x = Variable("$m_{med}$", is_independent=True, is_binned=False, units="GeV")
        x.values = idf.mmed
        table.add_variable(x)

        y = Variable("Coupling limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Observed")
        y.values = idf.obs
        table.add_variable(y)
        y = Variable("Coupling limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Median expected")
        y.values = idf.exp
        table.add_variable(y)
        y = Variable("Coupling limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Expected plus 1 s.d.")
        y.values = idf.p1s
        table.add_variable(y)
        y = Variable("Coupling limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Expected plus 2 s.d.")
        y.values = idf.p2s
        table.add_variable(y)
        y = Variable("Coupling limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Expected minus 1 s.d.")
        y.values = idf.m1s
        table.add_variable(y)
        y = Variable("Coupling limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Expected minus 2 s.d.")
        y.values = idf.m2s
        table.add_variable(y)


        for var in table.variables:
            if var.is_independent:
                continue
            var.add_qualifier("Mediator",coupling)
            if coupling=='gq':
                var.add_qualifier("$g_{\chi}$",1.0)
            else:
                var.add_qualifier("$g_{q}$",1.0)
            var.add_qualifier("$m_{DM}$","$m_{med}/3$")


        sub.add_table(table)

def limits_dmsimp_spin0_1d(sub):
    df = pd.read_pickle(f"/home/albert/repos/monojet/limitplot/input/{tag}/limit_df.pkl")
    df = df[(df.cl==0.95)& (~np.isnan(df.mmed)) &  (~np.isnan(df.mdm))]
    df.sort_values(by='mmed', inplace=True)

    df = df[df.mdm==1]
    for mediator in ['scalar','pseudoscalar']:
        table = Table(f"Signal strength limits, {mediator} mediator")
        table.description = f"Exclusion limits on the signal strength in the simplified model with {mediator} couplings."
        idf = df[df.coupling==mediator]
        idf = idf[idf.mmed>20]

        x = Variable("$m_{med}$", is_independent=True, is_binned=False, units="GeV")
        x.values = idf.mmed
        table.add_variable(x)

        y = Variable("Signal strength limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Observed")
        y.values = idf.obs
        table.add_variable(y)
        y = Variable("Signal strength limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Median expected")
        y.values = idf.exp
        table.add_variable(y)
        y = Variable("Signal strength limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Expected plus 1 s.d.")
        y.values = idf.p1s
        table.add_variable(y)
        y = Variable("Signal strength limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Expected plus 2 s.d.")
        y.values = idf.p2s
        table.add_variable(y)
        y = Variable("Signal strength limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Expected minus 1 s.d.")
        y.values = idf.m1s
        table.add_variable(y)
        y = Variable("Signal strength limit", is_independent=False, is_binned=False)
        y.add_qualifier("Quantile", "Expected minus 2 s.d.")
        y.values = idf.m2s
        table.add_variable(y)

        for var in table.variables:
            if var.is_independent:
                continue
            var.add_qualifier("Mediator",mediator)
            var.add_qualifier("$g_{q}$",1.0)
            var.add_qualifier("$g_{\chi}$",1.0)
            var.add_qualifier("$m_{DM}$",1.0, units="GeV")

        sub.add_table(table)

def limits_add_md(sub):
    limits = pd.read_pickle(f"/home/albert/repos/monojet/limitplot/add/output/{tag}/mdlimits.pkl")
    x = []
    values = {}
    for quant in limits[2].keys():
        values[quant] = []

    for d in limits.keys():
        x.append(d)
        for quant in limits[d].keys():
            values[quant].append(limits[d][quant])
    
    table = Table("ADD $M_{D}$ limits")
    table.description = "Exclusion limits on the fundamental Planck scale $M_{D}$ as a function of the number of extra dimensions $d$."

    var_x = Variable("d", is_independent=True, is_binned=False, units="")
    var_x.values = x
    table.add_variable(var_x)
    
    for quant, lims in values.items():
        var = Variable("Lower limit on $M_{D}", is_independent=False, is_binned=False, units="TeV")
        var.values = lims
        var.add_qualifier("Quantile", nice_quantile[quant])
        table.add_variable(var)
    
    sub.add_table(table)


def limits_lq(sub):
    with open(f"/home/albert/repos/monojet/limitplot/lq/output/{tag}/coupling/lq_limit.pkl","wb") as f:
        lims = pickle.load(f)
    
    
    table = Table("Leptoquark couplings limits")
    table.description = "Exclusion limits on the leptoquark coupling $\lambda$."

    var_x = Variable("$m_{LQ}$", is_independent=True, is_binned=False, units="GeV")
    var_x.values = lims['mlq']
    table.add_variable(var_x)
    
    for quant in ['exp','obs','p1s','p2s','m1s','m2s']:
        var = Variable("Lower limit on $\lambda", is_independent=False, is_binned=False)
        var.values = lims[f'ylq_{quant}']
        var.add_qualifier("Quantile", nice_quantile[quant])
        table.add_variable(var)
    
    sub.add_table(table)

def limits_tchan(sub):
    top = f"/home/albert/repos/monojet/limitplot/tchan/output/{tag}/"
    for quantile in ["exp","obs","p1s","m1s"]:
        table = Table(f"2D exclusion contour, fermion portal, {nice_quantile[quantile]}")
        table.description = f"{nice_quantile[quantile]} exclusion contour in the $m_{{med}}$-$m_{{\chi}} plane in the fermion portal model."
        fname = pjoin(top, f"contour_tchan_{quantile}.txt")
        assert(os.path.exists(fname))
        data = np.loadtxt(fname)
        mmed = Variable("$m_{\Phi}$", is_independent=True, is_binned=False)
        mmed.values = data[:,0]
        mdm = Variable("$m_{\chi}$", is_independent=False, is_binned=False)
        mdm.values = data[:,1]
        table.add_variable(mmed)
        table.add_variable(mdm)
        sub.add_table(table)



def limits(sub):
    # limits_dmsimp_2d(sub)
    # limits_dmsimp_coupling(sub)
    # limits_dmsimp_spin0_1d(sub)
    # limits_add_md(sub)
    limits_tchan(sub)