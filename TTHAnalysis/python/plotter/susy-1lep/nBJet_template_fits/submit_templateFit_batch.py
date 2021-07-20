import os

if not os.path.exists('batch_logs'):
        os.makedirs('batch_logs')
        if not os.path.exists('batch_logs/log'):
            os.makedirs('batch_logs/log')
        if not os.path.exists('batch_logs/err'):
            os.makedirs('batch_logs/err')
        if not os.path.exists('batch_logs/out'):
            os.makedirs('batch_logs/out')

fratio_file = 'Lp_LTbins_0b_MERGED_YEARS_f-ratios_MC.txt'

years = ['2016_EXT', '2017', '2018']
systs = ['nominal', 'dilep-corr']
variations = ['DLConst', 'DLSlope', 'JEC', 'PU', 'TTxsec', 'TTVxsec', 'Wpol', 'Wxsec', 'btagHF', 'btagLF', 'lepSF']
variations_up = [var+'_up' for var in variations]
variations_down = [var+'_down' for var in variations] 
variations = variations_up + variations_down

variations_2016 = [var+'_2016_EXT' for var in (variations + ['nISR_up','nISR_down'])] 
variations_2017 = [var+'_2017' for var in variations]
variations_2018 = [var+'_2018' for var in variations]

systs = systs + variations_2016 + variations_2017 + variations_2018
print 'Submitting', len(systs), 'jobs in total.'
for syst in systs:
    file_name = 'templateFit_job_'+syst+'.submit'
    out_dir = 'merged_'+syst

    with open(file_name, 'w') as f:
        f.write('executable = make_template_fits_fratio_merged\n')
        f.write('arguments = -s '+syst+' -f '+fratio_file+' -o '+out_dir+' \n')
        f.write('should_transfer_files = YES\n')
        f.write('log = batch_logs/log/tempFit_job_'+syst+'_$(ClusterId).log\n')
        f.write('output = batch_logs/out/tempFit_job_'+syst+'_$(ClusterId).out\n')
        f.write('error = batch_logs/err/tempFit_job_'+syst+'_$(ClusterId).Err\n')
        f.write('getenv = True\n')
        f.write('request_cpus = 4\n')
        f.write('request_memory = 1GB\n')
        f.write('request_disk = 300MB\n')
        f.write('+RequestRuntime = 60*60*6\n')
        f.write('queue 1\n')
        
    os.system('condor_submit '+file_name)
    os.system('rm '+file_name)
