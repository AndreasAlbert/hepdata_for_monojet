import re


import re
def legacy_dataset_name(dataset):
    m = re.match(f"DMSimp_(monojet|monow|monoz)_NLO_FXFX_(Axial|Vector)_GQ([0-9,p]*)_GDM([0-9,p]*)_MY1[_,-]([0-9,p]*)_MXd[_,-]([0-9,p]*).*", dataset)
    if m:
        channel, coupling, gq, gdm, mmed, mdm = m.groups()
        return f"{coupling.lower()}_{channel}_mmed{mmed}_mdm{mdm}_gq{gq}_gdm{gdm}"

    m = re.match('(Pseudoscalar|Scalar)_Mono(J|V)_LO_Mphi-([0-9,p]*)_Mchi-([0-9,p]*)_gSM-([0-9,p]*)_gDM-([0-9,p]*)-mg_201(\d)', dataset)
    if m:
        coupling, channel, mmed, mdm, gq, gdm, _ = m.groups()
        if channel=='J':
            channel = 'monojet'
        elif channel=='V':
            channel = 'monov'
        return f"{coupling.lower()}_{channel}_mmed{mmed}_mdm{mdm}_gq{gq}_gdm{gdm}"


    m = re.match('DMsimp_t-(S3D_uR)_(JChiChi|PhiPhiToJJChiChi)_Mphi-(\d+)_Mchi-(\d+)_Lambda-(1p0)-mg_pythia8_201(\d)', dataset)
    if m:
        model, channel, mphi, mchi, lam, _ = m.groups()
        if channel=='JChiChi':
            channel = 'cc'
        elif channel=='PhiPhiToJJChiChi':
            channel = 'pp'
        return f'{model}_{channel}_mphi{mphi}_mchi{mchi}_lam{lam}'

    m = re.match(f"ADDMonoJet_MD(_|-)(\d+)(_|-)d(_|-)(\d+)(_pythia8)?_.*", dataset)
    if m:         
        _, md, _,_,d,_ = m.groups()
        return f"add_md{md}_d{d}"

    m = re.match(f"ScalarFirstGenLeptoquarkToQNu_Mlq-(\d+)_Ylq-([0-9,p]*)_mg_.*", dataset)
    if m:
        mlq, ylq = m.groups()
        return f"lq_m{mlq}_d{ylq}"


    m = re.match("VBF_HToInvisible_M(\d+)(_PSweights)?_pow_pythia8_201[0-9]", dataset)
    if m:
        mh = m.groups()[0]
        if mh=="125":
            return "vbf"
        else:
            return f"vbf{mh}"

    m = re.match("ZH_ZToQQ_HToInvisible_M(\d+)_pow_pythia8_201[0-9]", dataset)
    if m:
        mh = m.groups()[0]
        if mh=="125":
            return "zh"
        else:
            return f"zh{mh}"

    m = re.match("WH_WToQQ_Hinv_M(\d+)_201[0-9]", dataset)
    if m:
        mh = m.groups()[0]
        if mh=="125":
            return "wh"
        else:
            return f"wh{mh}"

    m = re.match("GluGlu_HToInvisible_M(\d+)_HiggspTgt190_pow_pythia8_201[0-9]", dataset)
    if m:
        mh = m.groups()[0]
        if mh=="125":
            return "ggh"
        else:
            return f"ggh{mh}"
    
    m = re.match("ggZH_HToInvisible_ZToQQ_M(\d+)_pow_pythia8_201[0-9]", dataset)
    if m:
        mh = m.groups()[0]
        if mh=="125":
            return "ggzh"
        else:
            return f"ggzh{mh}"

    m = re.match("WH_HToInv_JHU_ptH150_201[0-9]", dataset)
    if m:
        return "wh_jhu"
    m = re.match("ZH_HToInv_JHU_ptH150_201[0-9]", dataset)
    if m:
        return "zh_jhu"

    patterns = {
        '.*DY.*' : 'zll',
        'QCD.*' : 'qcd',
        '(Top).*' : 'top',
        'Diboson.*' : 'diboson',
        'WZ.*' : 'wz',
        'WW.*' : 'ww',
        'ZZ.*' : 'zz',
        '(MET|EGamma).*' : 'data',
        'WN?JetsToLNu.*' : 'wjets',
        'ZN?JetsToNuNu.*' : 'zjets',
        'GJets_DR-0p4.*HT.*' : 'gjets',
        'GJets.*NLO.*' : 'gjets',
        'VQQGamma.*' : 'vgamma',
        'WQQGamma.*' : 'wgamma',
        'ZQQGamma.*' : 'zgamma'
    }

    for pat, ret in patterns.items():
        if re.match(pat, dataset):
            return ret

    raise RuntimeError(f'Cannot find legacy region name for dataset :"{dataset}"')
