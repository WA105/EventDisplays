import os
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import ROOT
import root_numpy
from datetime import datetime
from dateutil import tz
import mpl_toolkits.mplot3d as mp3d
from scipy.optimize import curve_fit
import warnings
import collections

run_path="/eos/experiment/wa105/offline/LArSoft/MC/MCA/MCA1/Pions/ROOT/recofull/"

def file_exists(filename): #returns True if file exists, False if it does not
    return bool(glob(filename))

def read_one_event(run=6, subrun=0, event=0):
    filename = run_path + str(subrun) + '-RecoFull-Parser.root'
    root_file_entries_list = root_numpy.list_branches(filename, 'analysistree/anatree')
    reco_file_values = root_numpy.root2array(filename, 'analysistree/anatree', start=event, stop=event+1, step=1)
    
    dictionary_reco_file_values = {}
    
    for root_file_index in range(len(root_file_entries_list)):
        dictionary_reco_file_values[root_file_entries_list[root_file_index]] = reco_file_values[0][root_file_index]
    
    all_channel_waveform_adc = []
    count = 0
    for i in range(1280):
        if i in dictionary_reco_file_values['RecoWaveform_Channel']:
            all_channel_waveform_adc.append(dictionary_reco_file_values['RecoWaveform_ADC'][count*1667:(count+1)*1667])
            count += 1
        else:
            all_channel_waveform_adc.append(np.zeros(1667))
    
    return np.array(all_channel_waveform_adc).reshape((1280, 1667))

def subtract_pedestal(ADC_values, method='median'): # subtracts the base level of the readout, setting the true 0:
    ADC_values_minped = np.zeros((1280, 1667))
    if method == 'median':
        for i in range(1280):
            ADC_values_minped[i] = ADC_values[i] - np.median(ADC_values[i])
    elif method == 'mean':
        for i in range(1280):
            ADC_values_minped[i] = ADC_values[i] - np.mean(ADC_values[i])
    else:
        print 'Method not recognized. Fucking implement it yourself or check what you typed!'
    return ADC_values_minped

def event_display(run, subrun, event, clim, savefig=False):
    ADC_values_minped = read_one_event(run=run, subrun=subrun, event=event)
    print "----------------"
#    ADC_values_minped = subtract_pedestal(ADC_values)
    fig = plt.figure()
    fig.set_figheight(7)
    fig.set_figwidth(18)
    fig.suptitle('Run ' + str(run) + ', SubRun ' + str(subrun) + ', Event ' + str(event))
    gs = gridspec.GridSpec(nrows=1, ncols=2, width_ratios=[1, 3])
    
    plt.subplot(gs[0])
    plt.title('View 0')
    ax0 = plt.gca()
    ax0.set_xlabel('channel number')
    ax0.set_ylabel('tick')
#    plt.xticks(np.arange(0, 321, 160))
    img0 = ax0.imshow(np.rot90(ADC_values_minped[:320]), extent=(0, 320, 0, 1667), interpolation='nearest', cmap=plt.cm.jet, origin='upper', clim=clim, aspect=320.0/1667.0)
    ax0.invert_yaxis()
    
    plt.subplot(gs[1])
    plt.title('View 1')
    ax1 = plt.gca()
    ax1.set_xlabel('channel number')
    ax1.set_ylabel('tick')
#    plt.xticks(np.arange(0, 961, 160))
    img1 = ax1.imshow(np.rot90(ADC_values_minped[320:]), extent=(0, 960, 0, 1667), interpolation='nearest', cmap=plt.cm.jet, origin='upper', clim=clim, aspect=960.0/1667.0/3.0)
    ax1.invert_yaxis()
    
    p0 = ax0.get_position().get_points().flatten()
    p1 = ax1.get_position().get_points().flatten()
    ax_cbar = fig.add_axes([p0[0], 0.45 * p0[2], p1[2]-p0[0], 0.02])
    fig.colorbar(img0, cax=ax_cbar, orientation='horizontal', label='ADC counts')
    
    if savefig:
        plt.savefig('eventdisplay_mc6_subrun' + str(subrun) + '_event' + str(event) + '.png', dpi=600)
    else:
        plt.show()

def plot_waveform(run, subrun, event, channel, view=None):
    ADC_values_minped = read_one_event(run=run, subrun=subrun, event=event)
#    ADC_values_minped = subtract_pedestal(ADC_values)
    if view == 0:
        ADC_values_one_channel = ADC_values_minped[channel]
        title = 'Run ' + str(run) + ', SubRun ' + str(subrun) + ', Event ' + str(event) + ', Channel ' + str(channel)
    elif view == 1:
        ADC_values_one_channel = ADC_values_minped[320 + channel]
        title = 'Run ' + str(run) + ', SubRun ' + str(subrun) + ', Event ' + str(event) + ', Channel ' + str(320 + channel)
    else:
        ADC_values_one_channel = ADC_values_minped[channel]
        title = 'Run ' + str(run) + ', SubRun ' + str(subrun) + ', Event ' + str(event) + ', Channel ' + str(channel)
    
    fig = plt.figure()
    plt.title(title)
    ax = plt.gca()
    ax.grid(True)
    ax.set_xlabel('tick')
    ax.set_ylabel('ADC')
    ax.plot(np.arange(0.0, 1667.0, 1.0), ADC_values_one_channel, color='navy')
    plt.show()

def get_reconstruction_variables(run=6, subrun=0, event=0):
    root_file_entries_list = root_numpy.list_branches(run_path + str(subrun) + '-RecoFast-Parser.root', 'analysistree/anatree')
    reco_file_values = root_numpy.root2array(run_path + str(subrun) + '-RecoFast-Parser.root', 'analysistree/anatree', start=event, stop=event+1, step=1)
    dictionary_reco_file_values = {}
    
    for root_file_index in range(len(root_file_entries_list)):
        dictionary_reco_file_values[root_file_entries_list[root_file_index]] = reco_file_values[0][root_file_index]
    
    if dictionary_reco_file_values['NumberOfTracks'] >= 1:
        track_number_of_hits_index_position = [dictionary_reco_file_values['Track_NumberOfHits'][0]]
        for i in range(1, dictionary_reco_file_values['NumberOfTracks']):
            track_number_of_hits_index_position.append(track_number_of_hits_index_position[i-1] + dictionary_reco_file_values['Track_NumberOfHits'][i])
    
        for key in dictionary_reco_file_values.keys():
            if key[:10] == 'Track_Hit_':
                dictionary_reco_file_values[key] = np.split(dictionary_reco_file_values[key], track_number_of_hits_index_position)
    return dictionary_reco_file_values

