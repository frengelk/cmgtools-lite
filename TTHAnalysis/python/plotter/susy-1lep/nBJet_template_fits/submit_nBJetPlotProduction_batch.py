import os
from optparse import OptionParser

def submit_condor_jobs(year, delete_submit_files = True, variations = "All"):
    if year not in ['2016_EXT', '2017', '2018']:
        print 'Please enter a valid year to run! (2016_EXT, 2017 or 2018)'
        return 0
    
    nominal = ['nominal', 'dilep-corr']
    systs = ['DLConst', 'DLSlope', 'JEC', 'PU', 'TTVxsec', 'TTxsec', 'Wpol', 'Wxsec', 'btagHF', 'btagLF', 'lepSF']
    systs_up = [syst+'_up' for syst in systs]
    systs_down = [syst+'_down' for syst in systs]
    
    if year == '2016_EXT':
        systs_up.append('nISR_up')
        systs_down.append('nISR_down')
    
    run_variations = nominal + systs_up + systs_down

    if variations != "All":
        if variations not in run_variations:
            print 'Please enter a valid variation to run! The options are:'
            print run_variations
        else:
            run_variations = [variations]

    if not os.path.exists('batch_logs'):
        os.makedirs('batch_logs')
        if not os.path.exists('batch_logs/log'):
            os.makedirs('batch_logs/log')
        if not os.path.exists('batch_logs/err'):
            os.makedirs('batch_logs/err')
        if not os.path.exists('batch_logs/out'):
            os.makedirs('batch_logs/out')

    mca_file = ''
    lumi = ''
    
    for var in run_variations:
        if year == '2016_EXT':
            mca_file = 'mca-Summer16_'+var+'.txt'
            lumi = '35.9'
        elif year == '2017':
            mca_file = 'mca-Fall17_'+var+'.txt'
            lumi = '41.5'
        elif year == '2018':
            mca_file = 'mca-Autumn18_'+var+'.txt'
            lumi = '59.7'

        job_tag = year+'_'+var
        
        file_name = 'nBJet_job_' + job_tag + '.submit'
        
        with open(file_name, 'w') as f:
            f.write('executable = make_nBJet_plots\n')
            f.write('arguments = -s '+var+' -c $(selection) -y '+year+' -m '+mca_file+' -l '+lumi+' \n')
            f.write('should_transfer_files = YES\n')
            f.write('log = batch_logs/log/nBJet_job_' + job_tag + '_$(selection)_$(ClusterId).log\n')
            f.write('output = batch_logs/out/nBJet_job_' + job_tag + '_$(selection)_$(ClusterId).out\n')
            f.write('error = batch_logs/err/nBJet_job_' + job_tag + '_$(selection)_$(ClusterId).err\n')
            f.write('getenv = True\n')
            f.write('request_cpus = 4\n')
            f.write('request_memory = 1GB\n')
            f.write('request_disk = 300MB\n')
            f.write('+RequestRuntime = 60*60*11\n')
            f.write('queue selection in (inclusive antiselected)\n')
        
        os.system('condor_submit '+file_name)
        if delete_submit_files:
            os.system('rm '+file_name)


if __name__ == "__main__":
    opt_parser = OptionParser()
    opt_parser.add_option("-y", "--year", dest="year", default="2016_EXT")
    opt_parser.add_option("-d", "--delete", dest="delete", default=True)
    opt_parser.add_option("-v", "--variations", dest="variations", default="All")
    (options, args) = opt_parser.parse_args()

    year = options.year
    delete = options.delete
    variations = options.variations
    
    submit_condor_jobs(year, delete, variations)
