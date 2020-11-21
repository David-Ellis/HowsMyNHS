"""
Plotting website data
"""

# standard python packages
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib.image import imread
from matplotlib import patches
import matplotlib.dates as mdates
import os

# third party packages
from brokenaxes import brokenaxes

# local packages
import build_website.process_data as proc
from build_website.build_website import mergered_trusts, whichChunks

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
                  legend = True):
    '''
    Parameters
    ----------
    name : string
        Trust name.
    data : list
        All NHS A&E waiting data with the format
            [names, dates, attendance, waiting]
    legend : bool
        Include legend

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
    plot_average = True
    if max(waiting[mask]) < 10:
        plot_average = False
        
    # Add data points
    ax.plot(dates[mask], waiting[mask]*norm,'b.', 
             alpha = 0.2, ms = 10)
        
    # Add moving average
    #    - Only include label if data points aren't included
    if plot_average == True:
        ax.plot(proc.movingAverage(dates[mask]), 
                proc.movingAverage(waiting[mask]*norm), 
                '-',
                label="3 month average", 
                lw=2,
                color = "#e60000")
        
    ax = fix_xticks(ax, dates[mask])
    
    if legend and plot_average:
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
            figName = proc.makeFigureName(name, "waiting", "svg")
            
            fig = makeAnEgraph(name, NHSdata, legend = True)
              
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
    
    combined = proc.combineBedData(beds, allNames, newName, mergered_trusts)
    
    ax = fix_xticks(ax, dates[combined!="-"])
    fig.tight_layout()
    
    return fig  

def plotBeds(name, NHSdata):
    
    if name in mergered_trusts.keys():
        fig = plotMergedBedData(name, NHSdata)
    
    else:
        names, dates, all_beds = NHSdata
        
        beds = all_beds[names == name][0]
        
        dates = dates[beds != "-"]
        beds = beds[beds != "-"]
        # format name to match waiting data
        names = proc.capitaliseFirst(names)
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
        
    return fig

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
            
            mask = (beds[i,:] != '-')     
            
            if name in mergered_trusts.keys() or sum(mask)>=4:
                
                figName = proc.makeFigureName(name, "beds", "svg")
                fig = plotBeds(name, NHSdata)
                fig.savefig("figures/{}".format(figName), bbox_inches = 'tight')
                plt.close()         

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

def makeOGtempImgs(name, waiting_data, bed_data, AnEblock, bedblock):
    '''Makes and saves the temp files for making the OG image for trust
    'name'.'''
    def getAnEPart(name, waiting_data):
        '''
        Makes and saves the A&E part of the OG image
        '''
        fig = makeAnEgraph(name, 
                            waiting_data, 
                            legend = False)
        fig.set_size_inches(6, 4)

        fig.savefig("og_temp_AnE.png", dpi = 100, bbox_inches = 'tight')
        plt.close(fig)
        
    def getBedPart(name, bed_data):
        '''
        Makes and saves the bed part of the OG image
        '''    
        
        fig = plotBeds(name, bed_data)
        fig.set_size_inches(6, 4)
        fig.savefig("og_temp_bed.png", dpi = 100, bbox_inches = 'tight')
        plt.close(fig)
    
    # Make and save the figures as png files
    if AnEblock and not bedblock:
        #print("Only A&E plot")
        getAnEPart(name, waiting_data)
    elif bedblock and not AnEblock:
        #print("Only bed plot")
        getBedPart(name, bed_data)
    elif bedblock and AnEblock:
        #print("Both bed block and A&E plots")
        getBedPart(name, bed_data)
        getAnEPart(name, waiting_data)
    else:
        raise Exception("Error: neither A&E or bed plot available.")   
        
def addBorder(img, border_size = 4):
    newImg = np.zeros((img.shape[0] + border_size*2,
                     img.shape[1] + border_size*2,
                     4))
    newImg[:,:,3] = 1
    newImg[border_size:-border_size,border_size:-border_size,:] = img
    
    return newImg

def addLogo(fig):
    ax = fig.axes[0]
    circle1 = patches.Circle((1020, 500), 80, 
                            edgecolor = "#003087",
                            facecolor = "white",
                            lw = 3)

    ax.add_patch(circle1)
    ax.annotate("How's My",(952, 494), size = 21, color = "#231f20")
    ax.annotate("NHS",(968, 540), size = 28, color = NHSblue,
                style='italic', weight='bold')
    ax.annotate("?",(1059, 540), size = 28, color = "#231f20")
    return fig

def deleteTempOGFiles():
    try:
        os.remove("og_temp_bed.png")
    except:
        pass
    try:
        os.remove("og_temp_AnE.png")
    except:
        pass
    return None

def makeOGimage(name, waiting_data, bed_data):
    
    matplotlib.rc('font', size=18)
    ane_names, dates, attendance, waiting = waiting_data
    bed_names, dates, beds = bed_data
    bed_names = proc.capitaliseFirst(bed_names)
    
    AnEblock, bedblock = whichChunks(name, ane_names, bed_names, 
                                     waiting, beds)
    #print(AnEblock, bedblock)
    if not (AnEblock or bedblock):
        return None
    
    # Make temp files
    makeOGtempImgs(name, waiting_data, bed_data, AnEblock, bedblock)
        
    canvas = np.zeros((630, 1200, 4))
    
    # solid pale blue canvas
    canvas[:,:,1] = 0.4
    canvas[:,:,2] = 1
    canvas[:,:,3] = 0.1
    fig = plt.figure(figsize = (12, 6.3), dpi=100)
    ax1 = fig.add_axes((0, 0, 1, 1))    

    
    # Make and save the figures as png files
    if AnEblock and not bedblock:
        # Only A&E plot
        img1 = imread('og_temp_AnE.png')
        img1 = addBorder(img1)
        y1 = 140; x1 = 260
        
        canvas[y1:img1.shape[0]+y1, x1:img1.shape[1]+x1, :] = img1
        
        ax1.imshow(canvas)
        
    elif bedblock and not AnEblock:
        # Only bed plot       
        img1 = imread('og_temp_bed.png')
        img1 = addBorder(img1)
        
        y1 = 140; x1 = 260
        
        canvas[y1:img1.shape[0]+y1, x1:img1.shape[1]+x1, :] = img1
        
        ax1.imshow(canvas)
        
    elif bedblock and AnEblock:
        # Both bed block and A&E plots
        img1 = imread('og_temp_bed.png')
        
        img1 = addBorder(img1)
        
        # pixels from the top
        y1 = 190; y2 = 90
        x1 = 290; x2 = 140
        
        canvas[y1:img1.shape[0]+y1, x1:img1.shape[1]+x1, :] = img1

        img2 = imread('og_temp_AnE.png')
        img2 = addBorder(img2)
        
        canvas[y2:img2.shape[0]+y2:, x2:img2.shape[1]+x2, :] = img2
        
        ax1.imshow(canvas)
        
    else:
        return None 
       
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_axis_off()
    fig = addLogo(fig)
    # delete temp files
    deleteTempOGFiles()
    return fig
    
def makeOGfile():
    if not os.path.isdir("figures/og"):
        os.mkdir("figures/og")

def plotOGimages(waiting_file, bed_file):
    makeOGfile()
    
    # Load data
    waiting_data = np.load(waiting_file, allow_pickle=True)
    bed_data = np.load(bed_file, allow_pickle=True)
    
    bed_names = proc.capitaliseFirst(bed_data[0])
    allNames = proc.combineNames(waiting_data[0], bed_names)
    
    for name in allNames:
        figName = proc.makeFigureName(name, "og", "png")
        fig = makeOGimage(name, waiting_data, bed_data)
        if fig != None:
            fig.savefig("figures/og/{}".format(figName), 
                        bbox_inches = 'tight', pad_inches=0)
            plt.close(fig)

            
def makeCovidGraph(name, data, legend = True):
    fig  = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(111)
      
    names, dates, deaths = data
    trustDeaths = deaths[names == name].T
    
    # Add data points
    ax.plot_date(dates, trustDeaths,'b.', alpha = 0.2, ms = 10)
    
    # moving average
    ax.plot_date(dates[3:-3],
                proc.movingAverage(trustDeaths, N=7),
                 '-', label="Weekly Average", lw=2,
                 color = "#e60000")
    
#     ax.plot(proc.movingAverage(dateInYears, N=3),
#         proc.movingAverage(trustDeaths, N=3),
#         '--', label="3 Day Average", lw=2,
#         color = "tab:green")
    ax.xaxis.set_tick_params(rotation=35)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_ylabel("Daily Covid-19 Deaths")
    if legend == True:
        ax.legend(prop={"size":14}, frameon=False, 
                  framealpha = 0)
    fig.tight_layout()
    
    return fig
            
def plotCovidData(datafile):
    ''' Plot daily covid deaths'''
    
    print("Generating Covid-19 graphs...", end = " ")
    
    # Load data
    
    data = np.load(datafile, allow_pickle=True)
    names = data[0] 
    names = proc.capitaliseFirst(names)
    
    ### Plot and save the data ###
    for i, name in enumerate(names[:]):
        figName = proc.makeFigureName(name, "covid", "svg")

        fig = makeCovidGraph(name, data)

        fig.savefig("figures/{}".format(figName))
        plt.close(fig)             
           
    print("Done.")