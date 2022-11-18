import subprocess, os
import fitdecode
import numpy as np
from matplotlib import pyplot as plt
import glob

def main():
    # Parameters
    #----------------
    # duration of test, [s]
    duration = 1200
    # moving average window, [s]
    moving = 60
    # FTP, [W]
    ftp = 305
    # W'bal, [kJ]
    wbal = 26
    # path and file
    filename = 'd:\Rolle.fit'
    # output directory
    os.chdir('d:')
    #----------------

    # Extract data from fit
    powers = []
    hrs = []
    with fitdecode.FitReader(filename) as fit_file:
        for frame in fit_file:
            if isinstance(frame, fitdecode.records.FitDataMessage):
                if frame.name == 'record':
                    powers.append(frame.get_value('power'))
                    hrs.append(frame.get_value('heart_rate'))

    # Extract start time
    starttime = detect_interval(powers, duration)
    # Cut data
    powers=powers[starttime:starttime+duration]
    hrs=hrs[starttime:starttime+duration]
    effs=np.array(powers)/np.array(hrs)*60

    # Export data
    export_series_csv(powers, 0, 'power_data')
    export_series_csv(moving_average(powers, moving), moving, 'power_smoothed_data')
    export_series_csv(hrs, 0, 'heart_data')
    export_series_csv(moving_average(hrs, moving), moving, 'heart_smoothed_data')
    export_series_csv(effs, 0, 'eff_data')
    export_series_csv(moving_average(effs, moving), moving, 'eff_smoothed_data')

    # Write tabular data for latex
    with open('tables.tex', 'w') as f:
        f.write('Average Power & \SI{' + str(np.round(np.average(powers),1)) + '}{W}' + str('\\\\')  )
        f.write('Standard deviation & \SI{' + str(np.round(np.std(powers),2)) + '}{W}' + str('\\\\') )
        f.write('Standard dev. (relative) & ' + str(np.round(np.std(powers)/np.average(powers)*100,2)) + ' \% ' + str('\\\\') )
        f.write('W\'bal min. (const) & ' + str(np.round(wbal*1000-duration*(np.average(powers)-ftp),0)) + ' J ' + str('\\\\'))
        f.write('Average HR & \SI{' + str(np.round(np.average(hrs),1)) + '}{1/min}' + str('\\\\') )
        f.write('Average work per beat & \SI{' + str(np.round(np.average(powers)*60/np.average(hrs),1)) + '}{J}' + str('\\\\') + str('\\\\') )

    # Compile pdf
    os.system("pdflatex d:\main.tex")

    # Remove all auxiliary data
    clean_up()

def moving_average(a, n=10) :
    # Calculate moving average. Shortens data!

    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def detect_interval(powers, duration) :
    # Detect starting time of max power interval for duration [s] from power data

    max=1
    i=0
    while i < len(powers)-duration:
        if np.average(powers[i:i+duration-1])>max:
            starttime=i
            max = np.average(powers[i:i+duration-1])
        i += 1
    return starttime

def export_series_csv(to_export, offset, title):
    # Export array as csv for latex plot with tikz
    # offset if exporting averaged data which is shorter for synchron

    counter = 1
    with open( title + '.csv', 'w') as f:
        f.write( 'x;y \n' )
        for record in to_export:
            f.write( str((counter+offset-1)/60) +';' + str(record) +'\n')
            counter += 1

def clean_up():
    # remove auxiliary files

    os.remove('main.out')
    os.remove('main.log')
    os.remove('main.aux')
    os.remove('tables.tex')
    # Remove all *_data.csv used for plotting
    fileList = glob.glob('*_data.csv')
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)
    # Remove all *_settings.tex used for plotting
    fileList = glob.glob('*_settings.tex')
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)
main()
