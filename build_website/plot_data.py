# -*- coding: utf-8 -*-
"""
Plotting website data
"""

# standard python packages
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

# third party packages
from brokenaxes import brokenaxes

# local packages
import build_website.process_data as proc
from build_website.build_website import mergered_trusts

# define plotting style
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rc('font', size=14)

# TODO: save data so I don't need these
str2num = np.vectorize(float)
intvec = np.vectorize(int)

# TODO: get plotting colours as arguments
NHSblue = "#0072CE"

def make_label(name):
    ''' 
    Reduces NHS trust name to key part
        i.e Removes words like "NHS", "Trust", "Of", "Foundation" etc...

    Parameters
    ----------
    name : string
        NHS trust full name.

    Returns
    -------
    label : string
        Shortened NHS trust name.
    '''
    
    remove = ["Trust", "Foundation", "NHS","University", "Hospital",
              "Hospitals", "Of"]
    
    def check(word):
        if word in remove:
            return False
        else:
            return True
    
    words = np.asarray(name.split(" "))
    
    filtered_words = filter(check, words)
    
    label = ' '.join(filtered_words)
    
    return label
    
def fix_xticks(ax, xdata):
    '''
    Makes x-ticks into integers

    Parameters
    ----------
    ax : matplotlib axes
        
    xdata : list
        list of graphs x data

    Returns
    -------
    ax : matplotlib axes
        axes with the xticks as integers

    '''
    
    # make x ticks integers only
    xup = int(np.ceil(max(xdata)))+1
    xdown = int(np.floor(min(xdata)))
    
    # if xdata range is greater than 5 then only include every other
    # integer in the range
    xint = range(xdown, xup, 2*(xup-xdown > 5) + 1*(xup-xdown <= 5))
    
    ax.set_xticks(xint)
    
    return ax

def makeAnEgraph(name, 
                 waiting_data, 
                 plot_points = True,
                 plot_average = True):
    '''
    Parameters
    ----------
    name : string
        Trust name.
    data : list
        All NHS A&E waiting data with the format
            [names, dates, attendance, waiting]
    plot_points : bool
        All data points should be included on the graph
    plot_average : bool
        Three month moving average should be included on the graph

    Returns
    -------
    fig : matplotlib figure
        Figure showing number of people waiting four hours over time.

    '''
    
    # unpack data
    names, dates, _, waiting = waiting_data
    dates = proc.dates2num(dates)
    
    
    if name in mergered_trusts.keys():
    
        waiting, mask = proc.combineAnEData(waiting, 
                                       names, 
                                       name, 
                                       mergered_trusts)
       
    else:
        waiting = waiting[names == name][0]
        mask = waiting != "-"
    
    assert sum(mask) >= 10, "Error: Less than 10 data points for trust:{}".format(name)
    
    fig  = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(111)
        
    # Plot in millions
    if max(waiting[mask]) > 1e5:
        ax.set_ylabel("People waiting over 4 hours\n(millions)")
        norm = 1e-6
    elif max(waiting[mask]) > 1e3:
        ax.set_ylabel("People waiting over 4 hours\n(thousands)")
        norm = 1e-3
    else:
        ax.set_ylabel("People waiting over 4 hours")
        norm = 1
      
    # If numbers are all very small *and* they are being plotted, then
    # don't include the moving average
    if max(waiting[mask]) < 10 and plot_points == True:
        plot_average == False
        
    # Add data points
    if plot_points == True:
        ax.plot(dates[mask], 
                waiting[mask]*norm,
                'b.', 
                alpha = 0.2,
                ms = 10)
        
    # Add moving average
    #    - Only include label if data points aren't included
    if plot_average == True:
        ax.plot(proc.movingAverage(dates[mask]), 
                proc.movingAverage(waiting[mask]*norm), 
                '-',
                label="3 month average"*plot_points, 
                lw=2,
                color = "#e60000")
        
    ax = fix_xticks(ax, dates[mask])
    ax.legend(prop={"size":14},
              frameon=False,
              framealpha = 0, 
              loc=2)
    fig.tight_layout()
    
    return fig

    
def plotWaitingData(data):
    ''' Plot data NHS England A&E 4 hour waiting data'''
    
    print("Generating 4 hour waiting time graphs...", end = " ")
    
    # Load data
    NHSdata = np.load(data, allow_pickle=True)
    
    names, dates, _, waiting = NHSdata
    dates = proc.dates2num(dates)
    
    ### Plot and save the data ###
    
    # List of old trusts which have since merged into something else
    oldTrusts = proc.get_old_trusts(mergered_trusts)
    for i, name in enumerate(names[:]):
        mask = waiting[i,:] != "-"

        #print(sum(mask))
        check1 = type(name) == str
        check2 = name not in oldTrusts
        check3 = sum(mask)>=10 or name in mergered_trusts.keys()
        
        if check1 and check2 and check3:
            figName = proc.makeFigureName(name, "waiting")
            
            fig = makeAnEgraph(name, NHSdata, 
                               plot_points = True,
                               plot_average = True)
              
            fig.savefig("figures/{}".format(figName))
            plt.close(fig)             
           
    print("Done.")
    
    
def plotMergedBedData(newName, NHSdata):
    barColours = ["#004684", "#006BC8", "#39A1FC", "#71BCFE"]
     
    allNames, dates, beds = NHSdata

    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(111)
    
    # plot main data
    mainData = beds[allNames == newName][0]
    mainMask = mainData != "-"
    if len(mainData[mainMask])>0:
        ax.bar(dates[mainMask], 
               mainData[mainMask], 
               lw=3, 
               width = 0.2, 
               color = barColours[0], 
               label = make_label(newName))
        
    # plot old data
    
    oldDataTotal = np.zeros(len(dates))
    for i, oldTrustName in enumerate(mergered_trusts[newName]):
        oldData = beds[allNames == oldTrustName][0]
        oldDataMask = oldData != "-"
        
        ax.bar(dates[oldDataMask], oldData[oldDataMask], 
                lw=3, width = 0.2,
                bottom = oldDataTotal[oldDataMask], 
                color = barColours[i+1],
                label = make_label(oldTrustName))
  
        # determine bottom of the bars
        if i == 0:
            oldDataTotal = oldData
        else:
            oldDataTotal[oldDataMask] += oldData[oldDataMask]
            
    ax.set_ylabel("Total # of Available Beds")
    ax.set_ylim(0, (1.2 + \
        len(mergered_trusts[newName])/10)*max(max(oldDataTotal[oldDataMask]), 
                                              max(mainData[mainMask])))
    ax.legend(prop={"size":14},frameon=False, framealpha = 0, loc=2)
    fig.tight_layout()
    
    return fig  

def plotBeds(name, dates, beds):
    figName = proc.makeFigureName(name, "beds")
    
    # rescale large numbers to be in thousands
    if max(beds) > 1000:
        rescale = 1/1000
    else:
        rescale = 1
        
    ylabel = "# of Overnight Beds" + "\n(Thousands)"*(rescale==1/1000)
    
    fig = plt.figure(figsize=(6,4))
    if min(beds) > 300 and (max(beds) - min(beds)) < min(beds)/3:
        bax = brokenaxes(ylims=((0, 0.005*max(beds)*rescale), 
         (0.95*min(beds)*rescale, 1.02*max(beds)*rescale)), hspace=0.08)
        bax.set_ylabel(ylabel, labelpad = 50)
    else:
        bax = fig.add_subplot(111)
        bax.set_ylim(0, 1.1*max(beds)*rescale)
        bax.set_ylabel(ylabel)
    
    bax.bar(dates, beds*rescale, width=0.18, color = NHSblue)
    
    xup = int(np.ceil(max(dates)))+1
    xdown = int(np.floor(min(dates)))
    xint = range(xdown, xup, 2*(xup-xdown > 5) + 1*(xup-xdown <= 5))
    
    bax.set_xticks(xint)
    
    fig.savefig("figures/{}".format(figName), bbox_inches = 'tight')
    plt.close(fig)

def plotBedData(data):
    ''' Plot the number of beds at NHS England Trusts'''
    
    print("Generating graphs for the number of beds ...", end = " ")
    
    # Load data
    NHSdata = np.load(data, allow_pickle=True)
    
    names, dates, beds = NHSdata
    # format name to match waiting data
    names = proc.capitaliseFirst(names)
    
    #### Plot and save the data ####
    
    # List of old trusts which have since merged into something else
    oldTrusts = proc.get_all_dict_values(mergered_trusts)
    for i, name in enumerate(names[:]):
        if type(name) == str and not (name in oldTrusts):
            figName = proc.makeFigureName(name, "beds")
            mask = (beds[i,:] != '-')     
            if name in mergered_trusts.keys():
                #print("Merged!!!!!")
                fig = plotMergedBedData(name, NHSdata)
                fig.savefig("figures/{}".format(figName))
                plt.close()
            elif sum(mask)>=4:
                plotBeds(name, dates[mask],  beds[i,:][mask])

    #### Plot trust change pie chart #### 
    more, same, fewer = proc.bed_change_per_trust(names,
                                             beds,
                                             mergered_trusts)
    
    plt.figure(figsize = (6,4))
    labels = 'Fewer Beds', 'Same*', 'More Beds'
    sizes = [fewer, same, more]
    
    colors = ['lightcoral', 'lightgray', 'yellowgreen']
    explode = (0.05, 0.0, 0.0)  # explode 1st slice
    
    # Plot
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=140)
    
    plt.axis('equal')
    plt.tight_layout()
    plt.annotate("* change smaller than 50 beds.", 
                 (0.2, -1.2), size = 13, color = "gray")
    plt.savefig("figures/BedsPieChart.svg")      
    plt.close( )      
                
    print("Done.")
