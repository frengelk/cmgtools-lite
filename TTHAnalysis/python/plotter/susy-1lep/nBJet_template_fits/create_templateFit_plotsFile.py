from searchBins_0b_with_NW import *

file_path = 'nBJet_distributions/nBJet_plots_0b_templateFit.txt'

cond_LT = {}
cond_LT['LT1'] = '250 < LT && LT < 350'
cond_LT['LT2'] = '350 < LT && LT < 450'
cond_LT['LT3'] = '450 < LT && LT < 650'
cond_LT['LT3i'] = '450 <= LT'
cond_LT['LT4i'] = '650 <= LT'

cond_HT = {}
cond_HT['HT0'] = '500 < HT && HT < 750'
cond_HT['HT02'] = '500 < HT && HT < 1000'
cond_HT['HT03'] = '500 < HT && HT < 1250'
cond_HT['HT1'] = '750 < HT && HT < 1250'
cond_HT['HT1i'] = '750 < HT'
cond_HT['HT2i'] = '1000 < HT'
cond_HT['HT3i'] = '1250 < HT'

cond_NJ = {}
cond_NJ['NJ34'] = '3 <= nJets30Clean && nJets30Clean <= 4'
cond_NJ['NJ45'] = '4 <= nJets30Clean && nJets30Clean <= 5'
cond_NJ['NJ5'] = 'nJets30Clean == 5'
cond_NJ['NJ67'] = '6 <= nJets30Clean && nJets30Clean <= 7'
cond_NJ['NJ8i'] = '8 <= nJets30Clean'

dPhi_cut = {}
dPhi_cut['LT1'] = 'dPhi < 1.0'
dPhi_cut['LT2'] = 'dPhi < 1.0'
dPhi_cut['LT3'] = 'dPhi < 0.75'
dPhi_cut['LT3i'] = 'dPhi < 0.75'
dPhi_cut['LT4i'] = 'dPhi < 0.5'

cond_NW = {}
cond_NW['NW0'] = 'nWTight == 0'
cond_NW['NW0i'] = 'nWTight >= 0'
cond_NW['NW1i'] = 'nWTight >= 1'


def get_output_string(lt_bin, ht_bin, nj_bin, nw_bin):

    bin_name = (lt_bin + '_' 
              + ht_bin + '_'
              + 'NB0_'
              + nj_bin + '_'
              + nw_bin)
    
    conditions_string = (cond_LT[lt_bin] + ' && '
                       + cond_HT[ht_bin] + ' && '
                       + cond_NJ[nj_bin] + ' && '
                       + dPhi_cut[lt_bin] + ' && '
                       + cond_NW[nw_bin])

    if nj_bin == 'NJ34':
        conditions_string += ' && nMu == 1'
    
    plot_name = 'nBJet_' + bin_name
    binning = '4, 0, 4'
    x_label = '''XTitle="b-jet multiplicity (''' + bin_name.replace('NB0_','') + ''')"''' 

    output_string = (plot_name 
                   + ': if3('
                   + conditions_string
                   + ', nBJet, -99) : '
                   + binning + ' ; '
                   + x_label
                   + ', IncludeOverflows=False')

    return (output_string + '\n')

with open(file_path, 'w') as f:
    for bin in (sorted(cutDictf34.keys())):
        lt_bin, ht_bin, nb_bin, nj_bin, nw_bin = bin.split('_')
        f.write(get_output_string(lt_bin, ht_bin, nj_bin, nw_bin))

    # Special treatment for nJet45 because of potential differences in NB0 and NB1i bins
    bins_45 = []
    for bin in (sorted(cutDictf45.keys())):
        lt_bin, ht_bin, nb_bin, nj_bin, nw_bin = bin.split('_')
        if lt_bin+'_'+ht_bin+'_'+nj_bin+'_'+nw_bin not in bins_45:
            bins_45.append(lt_bin+'_'+ht_bin+'_'+nj_bin+'_'+nw_bin)
            f.write(get_output_string(lt_bin, ht_bin, nj_bin, nw_bin))

    for bin in (sorted(cutDictf5.keys())):
        lt_bin, ht_bin, nb_bin, nj_bin, nw_bin = bin.split('_')
        f.write(get_output_string(lt_bin, ht_bin, nj_bin, nw_bin))

    for bin in (sorted(cutDictf67.keys())):
        lt_bin, ht_bin, nb_bin, nj_bin, nw_bin = bin.split('_')
        f.write(get_output_string(lt_bin, ht_bin, nj_bin, nw_bin))

    for bin in (sorted(cutDictf8.keys())):
        lt_bin, ht_bin, nb_bin, nj_bin, nw_bin = bin.split('_')
        f.write(get_output_string(lt_bin, ht_bin, nj_bin, nw_bin))
