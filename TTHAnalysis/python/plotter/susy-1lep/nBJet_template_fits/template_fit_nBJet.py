import os
import math
import ROOT
import pandas as pd

from optparse import OptionParser
from ROOT import RooFit as rf


def read_fratios(fratios_file):
    fDict = {}

    with open(fratios_file) as f:
        lines = f.readlines()

        for line in lines:
            if line[0] != '#':
                (bin, ratio, error) = line.split()
                bin = bin.replace('_NJ34', '')
                if 'LT' in bin:
                    fDict[bin] = (float(ratio), float(error))
    return fDict

def set_new_qcd_hist_errors(qcd_hist, fratio, fratio_error, nbins):
    # Propagate f-ratio uncertainty to QCD yield uncertainties
    for i in range(1, nbins+1):
        bin_yield = qcd_hist.GetBinContent(i)
        bin_error = qcd_hist.GetBinError(i)
        if (bin_yield > 0) and (bin_error < bin_yield):
            new_bin_error = bin_yield * math.sqrt((bin_error/bin_yield)**2 + (fratio_error/fratio)**2)
            # Check that the new uncertainty doesn't exceed 100%
            if new_bin_error < bin_yield:
                qcd_hist.SetBinError(i, new_bin_error)
            else:
                qcd_hist.SetBinError(i, bin_yield)

def calculate_fraction_uncertainty(numerator, numerator_error, denominator, denominator_error):
    if (numerator <= 0) or (denominator <= 0):
        return 0
    fraction = numerator/denominator
    a = (numerator_error/numerator)**2 + (denominator_error/denominator)**2
    error = fraction*math.sqrt(a)

    # Check that the uncertainty doesn't exceed 100%
    if error < fraction:
        return error
    else:
        return fraction

def template_fit(inclusive_file, antisel_file, fratios_file, out_path, out_filename, ratio_plots=False, verbose=False):
    # Define verbose print 
    if verbose:
        def vprint(*args):
            for arg in args:
                print arg,
            print
    else:
        vprint = lambda *args: None

    # Define the dataframe for the output .csv file
    template_df = pd.DataFrame(columns = ['bin', 'Data_yield', 'Data_yield_err',
                                          'TTJets_yield', 'TTJets_yield_err',
                                          'WJets_yield', 'WJets_yield_err',
                                          'QCD_yield', 'QCD_yield_err',
                                          'Other_yield', 'Other_yield_err',
                                          'TotalFit_yield', 'TotalFit_yield_err',
                                          'TTJets_fraction', 'TTJets_fraction_err', 
                                          'WJets_fraction', 'WJets_fraction_err'])

    inclusive = ROOT.TFile(inclusive_file)
    antisel = ROOT.TFile(antisel_file)
    fratios = read_fratios(fratios_file)

    # Extract the bins
    bin_list = set()
    keylist = inclusive.GetListOfKeys()
    keylist_iterator = keylist.MakeIterator()
    for i in range(len(keylist)):
        object_name = keylist_iterator.Next().ReadObj().GetName()
        split_name = object_name.split("_") 
        bin_name = "%s_%s_%s_%s_%s" % (split_name[1], split_name[2], split_name[3], split_name[4], split_name[5])
        bin_list.add(bin_name) 
    
    # Loop over the extracted bins 
    for bin_name in bin_list:
        vprint("PROCESSING BIN:", bin_name, "\n")

        template_TTJets = inclusive.Get('nBJet_'+bin_name+'_TTJets')
        template_WJets = inclusive.Get('nBJet_'+bin_name+'_WJets')
        template_Other = inclusive.Get('nBJet_'+bin_name+'_Other')

        hData = inclusive.Get('nBJet_'+bin_name+'_data')
        hData_antisel = antisel.Get('nBJet_'+bin_name+'_data')
        
        template_TTJets.GetXaxis().SetRangeUser(0., 4.)
        template_WJets.GetXaxis().SetRangeUser(0., 4.)
        template_Other.GetXaxis().SetRangeUser(0., 4.)
        hData.GetXaxis().SetRangeUser(0., 4.)
        hData_antisel.GetXaxis().SetRangeUser(0., 4.)
        
        hQCD_pred = hData_antisel.Clone()

        LT_bin = bin_name.split("_")[0]
        fratio = fratios[LT_bin][0]
        fratio_err = fratios[LT_bin][1]

        hQCD_pred.Scale(fratio)
        set_new_qcd_hist_errors(hQCD_pred, fratio, fratio_err, nbins=4)

        vprint("PRE-FIT YIELDS:")
        vprint("Data -", hData.Integral())
        vprint("WJets -", template_WJets.Integral())
        vprint("TTJets -", template_TTJets.Integral())
        vprint("Other -", template_Other.Integral())
        vprint("QCD -", hQCD_pred.Integral())
        vprint("")
        
        # Normalize the histograms
        y_data = hData.Integral()
        y_WJets = template_WJets.Integral()
        y_TTJets = template_TTJets.Integral()
        y_Other = template_Other.Integral()
        y_QCD = hQCD_pred.Integral()

        template_TTJets.Scale(1./y_TTJets)
        template_WJets.Scale(1./y_WJets)
        template_Other.Scale(1./y_Other)
        if y_QCD > 0:
            hQCD_pred.Scale(1./y_QCD) 

        # Observable
        nBTagVar = "nBJets"
        x=ROOT.RooRealVar(nBTagVar,nBTagVar,0.,4.)
        
        # Convert the histograms into RooDataHist objects
        dh_data = ROOT.RooDataHist("data", "data", ROOT.RooArgList(x), hData)
        dh_TTJets = ROOT.RooDataHist("mcTTJets", "mcTTJets", ROOT.RooArgList(x), template_TTJets)
        dh_WJets = ROOT.RooDataHist("mcWJets", "mcWJets", ROOT.RooArgList(x), template_WJets)
        dh_Other = ROOT.RooDataHist("mcOther", "mcOther", ROOT.RooArgList(x), template_Other)
        if y_QCD > 0:
            dh_QCDpred = ROOT.RooDataHist("predQCD", "predQCD", ROOT.RooArgList(x), hQCD_pred)

        if y_QCD > 0:
            rooDataHist_arr = [dh_data, dh_WJets, dh_TTJets, dh_Other, dh_QCDpred]
        else: 
            rooDataHist_arr = [dh_data, dh_WJets, dh_TTJets, dh_Other]
        
        # Define the yields as variables, and set Other+QCD as constants
        yield_TTJets = ROOT.RooRealVar("TTJets_yield","TTJets_yield",0.1,0,10**5)
        yield_WJets = ROOT.RooRealVar("WJets_yield","WJets_yield",0.1,0,10**5)
        yield_Other = ROOT.RooRealVar("Other_yield","Other_yield",y_Other,y_Other,y_Other)
        yield_Other.setConstant()
        if y_QCD > 0:
          yield_QCD = ROOT.RooRealVar("QCD_yield","QCD_yield",y_QCD,y_QCD,y_QCD)
          yield_QCD.setConstant()

        # Define histograms as PDFs
        model_TTJets = ROOT.RooHistPdf("model_TTJets","model_TTJets",ROOT.RooArgSet(x),dh_TTJets)
        model_WJets = ROOT.RooHistPdf("model_WJets","model_WJets",ROOT.RooArgSet(x),dh_WJets)
        model_Other = ROOT.RooHistPdf("model_Other","model_Other",ROOT.RooArgSet(x),dh_Other)
        if y_QCD > 0:
            model_QCD = ROOT.RooHistPdf("model_QCD","model_QCD",ROOT.RooArgSet(x),dh_QCDpred)
        
        # Combine the PDFs
        if y_QCD > 0:
            model_combined = ROOT.RooAddPdf("model_combined","model_combined",ROOT.RooArgList(model_WJets, model_TTJets, model_Other, model_QCD),ROOT.RooArgList(yield_WJets, yield_TTJets, yield_Other, yield_QCD))
        else:
            model_combined = ROOT.RooAddPdf("model_combined","model_combined",ROOT.RooArgList(model_WJets, model_TTJets, model_Other),ROOT.RooArgList(yield_WJets, yield_TTJets, yield_Other))

        # Do the fit
        ### model_combined.fitTo(dh_data) also works
        nllComponents = ROOT.RooArgList("nllComponents")
        nll_model = model_combined.createNLL(dh_data,rf.NumCPU(1))
        nllComponents.add(nll_model)
        sumNLL = ROOT.RooAddition("sumNLL","sumNLL", nllComponents)
        ROOT.RooMinuit(sumNLL).migrad()
        ROOT.RooMinuit(sumNLL).hesse()
        ROOT.RooMinuit(sumNLL).minos() # optional
        
        vprint("POST-FIT YIELDS:")
        vprint("WJets -", yield_WJets.getVal())
        vprint("TTJets -", yield_TTJets.getVal())
        vprint("Other -", yield_Other.getVal())
        if y_QCD > 0: vprint("QCD -", yield_QCD.getVal())
        vprint("")

        # Scale the templates back up to the correct yields
        template_TTJets.Scale(yield_TTJets.getVal())
        template_WJets.Scale(yield_WJets.getVal())
        template_Other.Scale(yield_Other.getVal())
        hQCD_pred.Scale(yield_QCD.getVal())

        # Plot the resulting template fit 
        fitFrame = x.frame(rf.Bins(50),rf.Title("FitModel"))
        fitFrame_ratio = x.frame(rf.Bins(50),rf.Title("FitModel"))

        x.setConstant() # Set x as constant so that it doesn't show up in the plot legend
        model_combined.paramOn(fitFrame, rf.Layout(0.42,0.9,0.9))

        dh_data.plotOn(fitFrame,rf.LineColor(ROOT.kRed))
        model_combined.plotOn(fitFrame,rf.LineStyle(ROOT.kDashed))
        model_combined.plotOn(fitFrame,rf.Components("model_WJets"),rf.LineColor(ROOT.kGreen))
        model_combined.plotOn(fitFrame,rf.Components("model_TTJets"),rf.LineColor(ROOT.kBlue))
        model_combined.plotOn(fitFrame,rf.Components("model_Other"),rf.LineColor(ROOT.kOrange+7))
        if y_QCD > 0: model_combined.plotOn(fitFrame,rf.Components("model_QCD"),rf.LineColor(ROOT.kCyan+1))

        plot_width = 650
        plot_height = 600
        if ratio_plots:
            plot_height = 700

        c1 = ROOT.TCanvas("c1","FitModel",plot_width,plot_height)
        ROOT.gROOT.SetStyle("Plain")

        c1.cd()
        if ratio_plots:
            pad1 = ROOT.TPad("pad1","pad1",0,0.25,1,1)
            pad1.Draw()
            pad1.cd()
            pad1.SetBottomMargin(0.08)
            pad1.SetLeftMargin(0.15)
        else:
            ROOT.gPad.SetLeftMargin(0.15)
        fitFrame.GetYaxis().SetTitleOffset(1.4)
        fitFrame.GetXaxis().SetTitle(nBTagVar + " (" + bin_name.replace("NB0_","") + ")")
        fitFrame.Draw()

        if ratio_plots:
            c1.cd()
            pad2 = ROOT.TPad("pad2","pad2",0,0.05,1,0.25)
            pad2.Draw()
            pad2.cd()
            pad2.SetLeftMargin(0.15)
            fit_sum = template_TTJets.Clone()
            fit_sum.Add(template_WJets, 1)
            fit_sum.Add(template_Other, 1)
            fit_sum.Add(hQCD_pred, 1)

            ratio = hData.Clone()
            ratio.Divide(fit_sum)
            ratio.SetLineColor(ROOT.kRed)
            ratio.SetLineWidth(2)
            ratio.SetMarkerStyle(0)
            ratio.SetMinimum(0.)
            ratio.SetMaximum(2.) 
            ratio.SetTitle("")
            ratio.SetXTitle("")
            ratio.SetYTitle("Data / Fit")
            ratio.GetXaxis().SetLabelSize (0.07)
            ratio.GetYaxis().SetTitleOffset(0.38)
            ratio.GetYaxis().SetLabelSize (0.07)
            ratio.GetYaxis().SetTitleSize (0.13)

            line = ROOT.TLine(0,1,4,1)
            line.SetLineStyle(2)
            line.SetLineColor(ROOT.kGray+3)

            ratio.Draw()
            line.Draw("SAME")

        c1.Print(out_path+'/nBJetsTemplateFit_'+bin_name+'.png')
        c1.Print(out_path+'/nBJetsTemplateFit_'+bin_name+'.pdf')
        c1.Print(out_path+'/nBJetsTemplateFit_'+bin_name+'.root')

        # Get and save all the yields from the 0b bin 
        dh_TTJets.get(0)
        TTJets_0b_yield = dh_TTJets.weight()*yield_TTJets.getVal()
        TTJets_0b_err = math.sqrt(dh_TTJets.weight())*yield_TTJets.getError()

        dh_WJets.get(0)
        WJets_0b_yield = dh_WJets.weight()*yield_WJets.getVal()
        WJets_0b_err = math.sqrt(dh_WJets.weight())*yield_WJets.getError()
        
        Other_0b_yield = template_Other.GetBinContent(1)
        Other_0b_err = template_Other.GetBinError(1)

        if y_QCD > 0:
            QCD_0b_yield = hQCD_pred.GetBinContent(1)
            QCD_0b_err = hQCD_pred.GetBinError(1)
        else:
            QCD_0b_yield = 0
            QCD_0b_err = 0

        Data_0b_yield = hData.GetBinContent(1)
        Data_0b_err = hData.GetBinError(1)

        TotalFit_0b_yield = TTJets_0b_yield + WJets_0b_yield + Other_0b_yield + QCD_0b_yield
        TotalFit_0b_err = math.sqrt(TTJets_0b_err**2 + WJets_0b_err**2 + Other_0b_err**2 + QCD_0b_err**2)

        vprint('\nYields in the 0b bin:')
        vprint('Data -', Data_0b_yield)
        vprint('Total fit -', TotalFit_0b_yield)
        vprint('WJets -', WJets_0b_yield)
        vprint('TTJets -', TTJets_0b_yield)
        vprint('Other -', Other_0b_yield)
        vprint('QCD -', QCD_0b_yield)

        vprint('\nYield uncertainties in the 0b bin:')
        vprint('Data -', Data_0b_err)
        vprint('Total fit -', TotalFit_0b_err)
        vprint('WJets -', WJets_0b_err)
        vprint('TTJets -', TTJets_0b_err)
        vprint('Other -', Other_0b_err)
        vprint('QCD -', QCD_0b_err)

        TTJets_0b_fraction = TTJets_0b_yield / TotalFit_0b_yield
        WJets_0b_fraction = WJets_0b_yield / TotalFit_0b_yield

        TTJets_0b_fraction_err = calculate_fraction_uncertainty(TTJets_0b_yield, TTJets_0b_err, TotalFit_0b_yield, TotalFit_0b_err)
        WJets_0b_fraction_err = calculate_fraction_uncertainty(WJets_0b_yield, WJets_0b_err, TotalFit_0b_yield, TotalFit_0b_err)

        vprint('\nFractions in the 0b bin:')
        vprint('WJets -', WJets_0b_fraction)
        vprint('TTJets -', TTJets_0b_fraction)

        vprint('\nFraction uncertainties in the 0b bin:')
        vprint('WJets -', WJets_0b_fraction_err)
        vprint('TTJets -', TTJets_0b_fraction_err)

        template_dict = {'bin' : bin_name, 'Data_yield' : Data_0b_yield, 'Data_yield_err' : math.sqrt(Data_0b_yield),
                'TTJets_yield' : TTJets_0b_yield, 'TTJets_yield_err' : TTJets_0b_err,
                'WJets_yield' : WJets_0b_yield, 'WJets_yield_err' : WJets_0b_err,
                'QCD_yield' : QCD_0b_yield, 'QCD_yield_err' : QCD_0b_err,
                'Other_yield' : Other_0b_yield, 'Other_yield_err' : Other_0b_err,
                'TotalFit_yield' : TotalFit_0b_yield, 'TotalFit_yield_err' : TotalFit_0b_err,
                'TTJets_fraction' : TTJets_0b_fraction, 'TTJets_fraction_err' : TTJets_0b_fraction_err, 
                'WJets_fraction' : WJets_0b_fraction, 'WJets_fraction_err' : WJets_0b_fraction_err}
        template_df = template_df.append(template_dict, ignore_index=True)

    template_df = template_df.sort_values(by=['bin'])
    template_df = template_df.reset_index(drop=True)
    template_df.to_csv(out_path+'/'+out_filename, sep=',')

if __name__ == "__main__":
    opt_parser = OptionParser()
    opt_parser.add_option("--syst", dest="systematic")
    opt_parser.add_option("--out", dest="out")
    opt_parser.add_option("--inclusive", dest="inclusive_file")
    opt_parser.add_option("--antiselected", dest="antiselected_file")
    opt_parser.add_option("--f-ratios", dest="fratios")
    opt_parser.add_option("--ratio-plots", action="store_true", dest="ratio_plots", default=False)
    opt_parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
    (options, args) = opt_parser.parse_args()

    systematic = options.systematic
    out_path = options.out
    inc_hists = options.inclusive_file
    antisel_hists = options.antiselected_file
    fratios = options.fratios
    ratio_plots = options.ratio_plots
    verbose = options.verbose

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    out_filename = 'templateFits_0b_merged_'+systematic+'.csv'

    template_fit(inc_hists, antisel_hists, fratios, out_path, out_filename, ratio_plots, verbose)
