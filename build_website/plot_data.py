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
import build_website.process_data as pd
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
        i.e. whatever is before "Hospital(s)","University" or "NHS".

    Parameters
    ----------
    name : string
        NHS trust full name.

    Returns
    -------
    label : string
        Shortened NHS trust name.
    '''
    #print(name)
    words = np.asarray(name.split(" "))
    #print(np.asarray(words) == "Hospital")
    
    mask = (words == "Hospital") | (words == "Hospitals") | \
        (words == "University") | (words == "NHS")
        
    # make sure that one of these final words is in the name 
    assert sum(mask) > 0, \
        "Error: \'final\' label word not found for {}".format(name)
        
    final_word = np.where(mask)[0][0]
        
    words = words[0:final_word]
    label = ' '.join(words)
    
    return label

def plotMergedWaitingData(name, NHSdata):
    allNames, dates, _, waitingData = NHSdata
    dates = pd.dates2num(dates)
    
    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(111)
    yrange = [0,100]; xrange = [2020,2021]
    
    # plot main data
    i = np.where(allNames == name)[0][0]
    mask = (waitingData[i,:] != '-')
    if len(waitingData[i,:][mask])>0:
        NumWaiting = intvec(str2num(waitingData[i,:][mask]))
        ax.plot(dates[mask], NumWaiting/1e6,'b.',lw=3)
        
        ax.plot(pd.movingAverage(dates[mask]), pd.movingAverage(NumWaiting),
                 'r-', lw=2)
        yrange[1] = 1.1*max(NumWaiting)
        xrange[0] = min(dates[mask])-1/12
          
    OldWaiting, OldMask = pd.combineAnEData(waitingData,
                                            allNames,
                                            name,
                                            mergered_trusts)
    #print(OldWaiting)
    ax.plot(dates[OldMask], OldWaiting[OldMask],'b.', alpha = 0.2, ms = 10)
    ax.plot(pd.movingAverage(dates[OldMask]), pd.movingAverage(OldWaiting[OldMask]),
             'r-',lw=2)
    
    # if max waiting nunber more than current range, extend 
    # the range
    #print(OldWaiting)
    yrange[1] = max(yrange[1],  1.1*max(OldWaiting[OldMask]))
    # if min date is lower than current range, reduce the 
    # minimum
    xrange[0] = min(xrange[0], min(dates[OldMask])-1/12)
    
    # make x ticks integers only
    xup = int(np.ceil(max(dates[OldMask])))+1
    xdown = int(np.floor(min(dates[OldMask])))
    xint = range(xdown, xup, 2*(xup-xdown > 5) + 1*(xup-xdown <= 5))
    ax.set_xticks(xint)
    
    ax.set_ylabel("Number of people\n waiting over 4 hours")
    ax.plot(-100,0,"r-", label = "3 month average")
    ax.set_xlim(xrange)
    ax.set_ylim(yrange)
    ax.legend(prop = {"size":14},frameon=False, framealpha = 0,loc = 2)
    fig.tight_layout()
    
    return fig
    
def plotWaitingData(data):
    ''' Plot data NHS England A&E 4 hour waiting data'''
    
    print("Generating 4 hour waiting time graphs...", end = " ")
    
    # Load data
    NHSdata = np.load(data, allow_pickle=True)
    
    names, dates, _, waiting = NHSdata
    dates = pd.dates2num(dates)
    


    ### Plot and save the data ###
    
    # List of old trusts which have since merged into something else
    oldTrusts = pd.get_all_dict_values(mergered_trusts)
    for i, name in enumerate(names[:]):
        if type(name) == str and name not in oldTrusts:
            mask = (waiting[i,:] != '-')
            if name == "England":
                NumWaiting = intvec(str2num(waiting[i,:][mask]))
                fig = plt.figure(figsize=(6,4))
                plt.plot(dates[mask], NumWaiting/1e6,'b.', alpha = 0.2, ms = 10)
                plt.plot(pd.movingAverage(dates[mask]), pd.movingAverage(NumWaiting/1e6), 'r-',label="3 month average",lw=2)
                plt.ylabel("Number of people\n waiting over 4 hours (million)")
                
                # make x ticks integers only
                xup = int(np.ceil(max(dates[mask])))+1
                xdown = int(np.floor(min(dates[mask])))
                xint = range(xdown, xup, 2*(xup-xdown > 5) + 1*(xup-xdown <= 5))
                plt.xticks(xint)
                
                figName = pd.makeFigureName(name, "waiting")
                if abs(dates[mask][0]-dates[mask][-1])<1.5:
                    #print("Small", name)
                    plt.xlim([min(dates[mask])-0.2, np.floor(max(dates[mask]))+1])
                plt.legend(prop={"size": 14},frameon=False, framealpha = 0,
                           loc = 2)
                plt.tight_layout()
                plt.savefig("figures/{}".format(figName))
                plt.close()
                
            # Deal with trusts which have merged together.
            elif name in mergered_trusts.keys():
                figName = pd.makeFigureName(name, "waiting")
                fig = plotMergedWaitingData(name, NHSdata)
                
                fig.savefig("figures/{}".format(figName))
                plt.close(fig)
                
                
            elif sum(mask)>=10:
                NumWaiting = intvec(str2num(waiting[i,:][mask]))
                fig = plt.figure(figsize=(6,4))
                
                # plot data
                plt.plot(dates[mask], 
                         NumWaiting,
                         'b.',
                         alpha = 0.2,
                         ms = 10)
                
                # plot moving average
                plt.plot(pd.movingAverage(dates[mask]), 
                         pd.movingAverage(NumWaiting), 
                         'r-',
                         label="3 month average",
                         lw=2)
                
                plt.ylabel("Number of people\n waiting over 4 hours")
                
                # make x ticks integers only
                xup = int(np.ceil(max(dates[mask])))+1
                xdown = int(np.floor(min(dates[mask])))
                xint = range(xdown, xup, 2*(xup-xdown > 5) + 1*(xup-xdown <= 5))
                plt.xticks(xint)
                
                figName = pd.makeFigureName(name, "waiting")
                
                if abs(dates[mask][0]-dates[mask][-1])<1.5:
                    #print("Small:", name)
                    plt.xlim([min(dates[mask])-0.2, np.floor(max(dates[mask]))+1])
                plt.legend(prop={"size": 14},frameon=False, framealpha = 0,loc = 2)
                plt.tight_layout()
                plt.savefig("figures/{}".format(figName))
                plt.close()
                
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
    figName = pd.makeFigureName(name, "beds")
    
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
    names = pd.capitaliseFirst(names)
    
    #### Plot and save the data ####
    
    # List of old trusts which have since merged into something else
    oldTrusts = pd.get_all_dict_values(mergered_trusts)
    for i, name in enumerate(names[:]):
        if type(name) == str and not (name in oldTrusts):
            figName = pd.makeFigureName(name, "beds")
            mask = (beds[i,:] != '-')     
            if name in mergered_trusts.keys():
                #print("Merged!!!!!")
                fig = plotMergedBedData(name, NHSdata)
                fig.savefig("figures/{}".format(figName))
                plt.close()
            elif sum(mask)>=4:
                plotBeds(name, dates[mask],  beds[i,:][mask])

    #### Plot trust change pie chart #### 
    more, same, fewer = pd.bed_change_per_trust(names,
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
