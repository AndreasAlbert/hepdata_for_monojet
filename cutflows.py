import re
from hepdata_lib import Variable, Table
from bucoffea.plot.util import klepto_load
from util import legacy_dataset_name
cut_names = {
 'all'            : 'Full sample',
 'trig_met'       : 'Trigger emulation',
 'hemveto_metphi' : 'HCAL mitigation ($\phi^{miss}$',
 'recoil'         : '$p_{T}^{miss} > 250$ GeV',
 'filt_met'       : '$p_{T}^{miss}$ quality filters',
 'veto_ele'       : 'Electron veto',
 'veto_muo'       : 'Muon veto',
 'veto_tau'       : 'Tau veto',
 'veto_b'         : 'B jet vato',
 'veto_photon'    : 'Photon veto',
 'mindphijr'      : '$\Delta\phi(jet,p_{T}^{miss}) > 0.5$',
 'dpfcalo'        : '$\Delta p_{T}^{miss} (\text{PF--Calorimeter}) < 0.5$',
 'hemveto'        : 'HCAL mitigation (jets)',
 'leadak4_pt'     : 'Leading AK4 jet $p_{T} > 100$ GeV',
 'leadak4_eta'    : 'Leading AK4 jet $\eta < 2.4$',
 'leadak4_id'     : 'Leading AK4 energy fractions',
 'veto_vtag'      : 'Mono-V overlap removal',
 'dphipftkveto'   : '$\Delta\phi(\mathrm{PF},\mathrm{Charged})$',
}
def make_variable(dataset):
    # m = re.match(f"DMSimp_(monojet|monow|monoz)_NLO_FXFX_(Axial|Vector)_GQ([0-9,p]*)_GDM([0-9,p]*)_MY1[_,-]([0-9,p]*)_MXd[_,-]([0-9,p]*).*", dataset)
    # if m:
    #     channel, coupling, gq, gdm, mmed, mdm = m.groups()
    #     return f"{coupling.lower()}_{channel}_mmed{mmed}_mdm{mdm}_gq{gq}_gdm{gdm}"
    qualifiers = None
    m = re.match('(Pseudoscalar|Scalar)_Mono(J|V)_LO_Mphi-([0-9,p]*)_Mchi-([0-9,p]*)_gSM-([0-9,p]*)_gDM-([0-9,p]*)-mg_201(\d)', dataset)
    if m:
        coupling, channel, mmed, mdm, gq, gdm, _ = m.groups()
        if channel=='J':
            channel = "\chi\chi+j"
        elif channel=='V':
            channel = "\chi\chi+V(qq)"
        qualifiers = [
            ("Coupling", coupling, ""),
            ("Mode", channel, ""),
            ("$m_{med}$", mmed, ""),
            ("$m_{DM}$", mdm, ""),
            ("$g_{\chi}$", gdm, ""),
            ("$g_{q}$", gq, ""),
        ]


    m = re.match('DMsimp_t-(S3D_uR)_(JChiChi|PhiPhiToJJChiChi)_Mphi-(\d+)_Mchi-(\d+)_Lambda-(1p0)-mg_pythia8_(ext\d_)?(\d+)', dataset)
    if m:
        model, channel, mphi, mchi, lam, _,year = m.groups()
        if channel=='JChiChi':
            channel = '$\Phi\Phi\rightarrow \chi\chi j j'
        elif channel=='PhiPhiToJJChiChi':
            channel = '$\chi\chi+j$'
        qualifiers = [
            ('$m_{\Phi}$', mphi, "GeV"),
            ('$m_{\chi}$', mchi, "GeV"),
            ('$\lambda$', lam, ""),
            ('Mode', channel, ""),
        ]    
    variable = Variable(name="Fraction of passing events", is_independent=False, is_binned=False)
    m = re.match(f"ADDMonoJet_MD(_|-)(\d+)(_|-)d(_|-)(\d+)(_pythia8)?_(\d)+", dataset)
    if m:         
        _, md, _,_,d,_, year = m.groups()
        qualifiers = [
            ("$M_{D}$", md, "TeV"),
            ("$d$", d, ""),
            ("Data set", year, "")
        ]

    m = re.match(f"ScalarFirstGenLeptoquarkToQNu_Mlq-(\d+)_Ylq-([0-9,p]*)_mg_.*(\d+)", dataset)
    if m:
        mlq, ylq, year = m.groups()
        qualifiers = [
            ("$M_{LQ}$", mlq, "GeV"),
            ("$\lambda$", ylq, ""),
            ("Data set", year, "")
        ]

    # m = re.match("VBF_HToInvisible_M(\d+)(_PSweights)?_pow_pythia8_(\d+)", dataset)
    # if m:
    #     mh = m.groups()[0]
    #     qualifiers = [
    #         ("Data set", year, "")
    #     ]
    # m = re.match("ZH_ZToQQ_HToInvisible_M(\d+)_pow_pythia8_201[0-9]", dataset)
    # if m:
    #     mh = m.groups()[0]
    #     if mh=="125":
    #         return "zh"
    #     else:
    #         return f"zh{mh}"

    # m = re.match("WH_WToQQ_Hinv_M(\d+)_201[0-9]", dataset)
    # if m:
    #     mh = m.groups()[0]
    #     if mh=="125":
    #         return "wh"
    #     else:
    #         return f"wh{mh}"

    # m = re.match("GluGlu_HToInvisible_M(\d+)_HiggspTgt190_pow_pythia8_201[0-9]", dataset)
    # if m:
    #     mh = m.groups()[0]
    #     if mh=="125":
    #         return "ggh"
    #     else:
    #         return f"ggh{mh}"
    
    # m = re.match("ggZH_HToInvisible_ZToQQ_M(\d+)_pow_pythia8_201[0-9]", dataset)
    # if m:
    #     mh = m.groups()[0]
    #     if mh=="125":
    #         return "ggzh"
    #     else:
    #         return f"ggzh{mh}"

    # m = re.match("WH_HToInv_JHU_ptH150_201[0-9]", dataset)
    # if m:
    #     return "wh_jhu"
    # m = re.match("ZH_HToInv_JHU_ptH150_201[0-9]", dataset)
    # if m:
    #     return "zh_jhu"
    if qualifiers is None:
        raise RuntimeError(f"Could not parse dataset: {dataset}")
    for name, value, units in qualifiers:
        variable.add_qualifier(name=name, value=value, units=units)
    return variable
    # raise RuntimeError(f'Cannot find legacy region name for dataset :"{dataset}"')

    


def cutflow(submission):
    interpretations = {
        'tchan' : re.compile("DMsimp_t.*"),
        'add' : re.compile("ADD.*")
    } 
    acc = klepto_load("input/cutflow/2021-05-19_cutflow")

    region = 'sr_j'
    name = f"cutflow_{region}"
    acc.load(name)
    cf = acc[name]


    x = Variable("Cut stage", is_independent=True, is_binned=False)

    x.values = [cut_names[tmp] for tmp in list(cf.values())[0].keys()]

    for interpretation, rgx in interpretations.items():
        datasets = filter(lambda x : rgx.match(x), cf.keys())
        table = Table(f"Cut flow for {interpretation}")
        table.description = "Unweighted signal acceptance times efficiency at every cut stage. The requirements called \"HCAL migitaion\" refer to the requirements imposed in the 2018 data set in order to mitigate the localized failure of the HCAL detector."
        table.add_variable(x)
        for dataset in datasets:
            y = make_variable(dataset)
            y.add_qualifier("dataset", dataset)
            y.values = cf[dataset].values()
            y.scale_values(1/y.values[0])
            table.add_variable(y)

    submission.add_table(table)
