'''
Module for building the HowsMyNHS website
'''
import news

import numpy as np
import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
import matplotlib

str2num = np.vectorize(float)
intvec = np.vectorize(int)

NHSblue = "#0072CE"



def dates2num(dates_in):
    dates_out = []
    for period in dates_in:
        year = float(period.split('/')[1])
        month = float(period.split('/')[0])
        dates_out.append(year+month/12)
    return np.asarray(dates_out)

def movingAverage(data, N=3):
    cumsum, moving_aves = [0], []

    for i, x in enumerate(data, 1):
        cumsum.append(cumsum[i-1] + x)
        if i>=N:
            moving_ave = (cumsum[i] - cumsum[i-N])/N
            #can do stuff with moving_ave here
            moving_aves.append(moving_ave)
    return moving_aves

def format_number(num):
    '''rounds number to nearest hundred and adds commas'''
    if num > 100:
        num = int(np.round(num / 100.0)) * 100
        out = "{:,}".format(num)
    else:
        out = "{}".format(num)
    return out

def get_names(data_file, output = False):
    NHSdata = np.load(data_file, allow_pickle=True)
    names, _, _, _ = NHSdata
    if output:
        for name in names:
            print(name)
    return names

def all_dict_values_generator(d):
    ''' From Michael Dorner on StackOverflow:
        https://stackoverflow.com/users/1864294/michael-dorner'''
    if isinstance(d, dict):
        for v in d.values():
            yield from all_dict_values_generator(v)
    elif isinstance(d, list):
        for v in d:
            yield from all_dict_values_generator(v)
    else:
        yield d 
        
def get_all_dict_values(d):
    gen = all_dict_values_generator(d)
    output = []
    for item in gen:
        output.append(item)
    return output
        
def capitaliseFirst(string_list):
    '''Capitalised the first letter of each word in each string in a list
except NHS which should be in all-caps'''
    
    for i, string in enumerate(string_list):
        words = string.split(" ")
        words = [word[0].upper() + word[1:] for word in words]
        string_list[i] = " ".join(words).replace("Nhs", "NHS")
        
    return string_list

########################## Generate Plots ###########################

def make_label(name):
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

# Merged trusts
mergered_trusts = {
    "Bedfordshire Hospitals NHS Foundation Trust": \
        ['Bedford Hospital NHS Trust',
         'Luton And Dunstable University Hospital NHS Foundation Trust'],
        
    "Mid And South Essex NHS Foundation Trust" : \
        ["Basildon And Thurrock University Hospitals NHS Foundation Trust",
          "Mid Essex Hospital Services NHS Trust",
          "Southend University Hospital NHS Foundation Trust"]
}

def combineAnEData(allData, allNames, merged_trust):
    ''' Combines (adds) the data for given list of trusts. 
        Combined data is only given for dates at which *all*
        listed trusts reported numbers.
    '''
    # initite total and mask
    totalData = np.zeros(len(allData[0,:]), dtype = object)
    
    newTrustData = allData[allNames == merged_trust][0]
    
    newTrustMask = np.asarray(newTrustData != "-")
    
    totalData[newTrustMask] = newTrustData[newTrustMask]
    
    # Add all data together and make mask for dates at while all trusts
    # provided data.
    OldDataMask = np.ones(len(totalData), dtype = bool)
    for oldTrust in mergered_trusts[merged_trust]:
        
        assert oldTrust in allNames, "Error: {} data not found".format(oldTrust)
        
        oldTrustData = allData[allNames == oldTrust][0]
        newMask = np.asarray(oldTrustData != "-")
        
        totalData[newMask] += oldTrustData[newMask]
        OldDataMask = OldDataMask & newMask
         
    finalMask = OldDataMask | newTrustMask
    #print(len(finalMask), len(totalData))
    totalData[np.invert(finalMask)] = "-"
    
    return totalData, finalMask
 
def combineBedData(bedData, allNames, merged_trust):
    '''Calculates total number of overnight beds for trusts that merged into 
    a final merged trust, as stored in the global merged_trusts dictionary'''
    
    # initite total and mask
    totalBeds = np.zeros(len(bedData[0,:]), dtype = object)
   
    # Add new trust data
    newTrustBeds = bedData[allNames == merged_trust][0]
    
    totalMask = np.asarray(newTrustBeds != "-")
    totalBeds[totalMask] += newTrustBeds[totalMask]
    
    # Add beds for old trusts
    for oldTrust in mergered_trusts[merged_trust]:
        
        assert oldTrust in allNames, "Error: {} data not found".format(oldTrust)
        
        oldTrustBeds = bedData[allNames == oldTrust][0]
        newMask  = np.asarray(oldTrustBeds != "-")
        totalBeds[newMask] += oldTrustBeds[newMask]
        
        totalMask = totalMask | newMask
        
    totalBeds[np.invert(totalMask)] = "-"
    
    return totalBeds
   
def makeFigureName(name, fig_type):
    fig_prefix = '-'.join(name.lower().split(' '))
    fig = ''.join([fig_prefix, "-", fig_type,".svg"])
    fig = fig.replace(',', '') 
    
    return fig    


def plotMergedWaitingData(name, NHSdata):
    allNames, dates, _, waitingData = NHSdata
    dates = dates2num(dates)
    
    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(111)
    yrange = [0,100]; xrange = [2020,2021]
    
    # plot main data
    i = np.where(allNames == name)[0][0]
    mask = (waitingData[i,:] != '-')
    if len(waitingData[i,:][mask])>0:
        NumWaiting = intvec(str2num(waitingData[i,:][mask]))
        ax.plot(dates[mask], NumWaiting/1e6,'b.',lw=3)
        
        ax.plot(movingAverage(dates[mask]), movingAverage(NumWaiting),
                 'r-', lw=2)
        yrange[1] = 1.1*max(NumWaiting)
        xrange[0] = min(dates[mask])-1/12
          
    OldWaiting, OldMask = combineAnEData(waitingData, allNames, name)
    #print(OldWaiting)
    ax.plot(dates[OldMask], OldWaiting[OldMask],'b.', alpha = 0.2, ms = 10)
    ax.plot(movingAverage(dates[OldMask]), movingAverage(OldWaiting[OldMask]),
             'r-',lw=2)
    
    # if max waiting nunber more than current range, extend 
    # the range
    #print(OldWaiting)
    yrange[1] = max(yrange[1],  1.1*max(OldWaiting[OldMask]))
    # if min date is lower than current range, reduce the 
    # minimum
    xrange[0] = min(xrange[0], min(dates[OldMask])-1/12)
    
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
    dates = dates2num(dates)
    
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rc('font', size=14)

    ### Plot and save the data ###
    
    # List of old trusts which have since merged into something else
    oldTrusts = get_all_dict_values(mergered_trusts)
    for i, name in enumerate(names[:]):
        if type(name) == str and name not in oldTrusts:
            mask = (waiting[i,:] != '-')
            if name == "England":
                NumWaiting = intvec(str2num(waiting[i,:][mask]))
                fig = plt.figure(figsize=(6,4))
                plt.plot(dates[mask], NumWaiting/1e6,'b.', alpha = 0.2, ms = 10)
                plt.plot(movingAverage(dates[mask]), movingAverage(NumWaiting/1e6), 'r-',label="3 month average",lw=2)
                plt.ylabel("Number of people\n waiting over 4 hours (million)")
                figName = makeFigureName(name, "waiting")
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
                figName = makeFigureName(name, "waiting")
                fig = plotMergedWaitingData(name, NHSdata)
                
                fig.savefig("figures/{}".format(figName))
                plt.close(fig)
                
                
            elif sum(mask)>=10:
                NumWaiting = intvec(str2num(waiting[i,:][mask]))
                fig = plt.figure(figsize=(6,4))
                plt.plot(dates[mask], NumWaiting,'b.', alpha = 0.2, ms = 10)
                plt.plot(movingAverage(dates[mask]), movingAverage(NumWaiting), 'r-',label="3 month average",lw=2)
                plt.ylabel("Number of people\n waiting over 4 hours")
                figName = makeFigureName(name, "waiting")
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
        ax.bar(dates[mainMask], mainData[mainMask], 
               lw=3, width = 0.2,color = barColours[0], 
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
    figName = makeFigureName(name, "beds")
    
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
    
    
    
    
    
    fig.savefig("figures/{}".format(figName), bbox_inches = 'tight')
    plt.close(fig)

def plotBedData(data):
    ''' Plot the number of beds at NHS England Trusts'''
    
    print("Generating graphs for the number of beds ...", end = " ")
    
    # Load data
    NHSdata = np.load(data, allow_pickle=True)
    
    names, dates, beds = NHSdata
    # format name to match waiting data
    names = capitaliseFirst(names)
    
    
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rc('font', size=14)

    #### Plot and save the data ####
    
    # List of old trusts which have since merged into something else
    oldTrusts = get_all_dict_values(mergered_trusts)
    for i, name in enumerate(names[:]):
        if type(name) == str and not (name in oldTrusts):
            figName = makeFigureName(name, "beds")
            mask = (beds[i,:] != '-')     
            if name in mergered_trusts.keys():
                #print("Merged!!!!!")
                fig = plotMergedBedData(name, NHSdata)
                fig.savefig("figures/{}".format(figName))
                plt.close()
            elif sum(mask)>=4:
                plotBeds(name, dates[mask],  beds[i,:][mask])

    #### Plot trust change pie chart #### 
    more, same, fewer = bed_change_per_trust(names, beds)
    
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


def combineNames(names1, names2):
    '''Makes a single list of each name appearing in either list'''
    namesOut = names1
    for name in names2:
        if name not in names1:
            namesOut = np.append(namesOut, name)
    return namesOut

def makeURL(name):
    url_prefix = '-'.join(name.lower().split(' '))
    url = ''.join(["hospitals/",url_prefix,".html"])
    url = url.replace(',', '') 
    return url
    
    
def MakeHomepage(waiting_data, bed_data):
    print("Building homepage...", end = " ")
    
    # Load data
    names1, _, _, waiting = np.load(waiting_data, allow_pickle=True)
    names2, _, beds = np.load(bed_data, allow_pickle=True)
    names2 = capitaliseFirst(names2)
    
    allNames = combineNames(names1, names2)
    
    # Make list of hospital names
    hospitalLinksList = []
    for i, name in enumerate(allNames):
        # Check if the trust is in contained in the values of merged_trust
        # i.e. is it an old trust which has since merged into something else.
        oldTrust = name in get_all_dict_values(mergered_trusts)
        if type(name) == str and not oldTrust:
            ane_points, bed_points = 0, 0
            merged = name in mergered_trusts.keys()
            
            if name in names1:
                ane_points = len(waiting[names1 == name][waiting[names1 == name] != '-'])
                
            if name in names2:
                bed_points = len(beds[names2 == name][beds[names2 == name] != '-'])
            
            if ane_points >= 10 or bed_points>= 4 or merged:
                url = makeURL(name)
                hospitalLinksList.append("<li><a href=\"{}\">{}</a></li>\n".format(url,name))

    hospitalLinks = ''.join(hospitalLinksList)
    file = open("index.html", "w") 

    file.write(''.join([homeHTML1, hospitalLinks, homeHTML2])) 
 
    file.close() 
    
    print("Done")
    
def make_AnE_waiting_block(data, name):
    ''' Generates the chunk of HTML relating to the A&E waiting time data for NHS trust <name>.
    
    TODO: Turn big chunks of text into global variables defined below with the other text.
    '''
    names, dates, attendance, waiting = np.load(data, allow_pickle=True)
    dates = dates2num(dates)
    i = np.where(names == name)[0][0]
    
    
    if name not in mergered_trusts.keys():
        attendanceData = attendance[i,:]
        waitingData = waiting [i,:]
    else:
        # Combine merged trust data
        attendanceData, _ = combineAnEData(attendance, names, name)
        waitingData, _ = combineAnEData(waiting, names, name)
        
    if i == 0:
        # Get figure path
        figName = makeFigureName(name, "waiting")
        path = "../figures/{}".format(figName)

        
        imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path,
             "A&E waiting data for all of England.")
        supTextHTML = u'''

            <p>After nearly a decade of Conservative rule, in December over <b>500,000</b> more people were made to wait
            <b>over four hours</b> to be seen at A&E than in 2011. That's an increase of over <b>900%</b>.
            The number of people attending A&E, however, had only increased by less than 30%.<p>

            {}

            {}
                  
            '''

        chunk = supTextHTML.format(imgHTML, brexit_et_al)
        
    elif sum(attendanceData != '-')>=10:
        # Get figure path
        figName = makeFigureName(name, "waiting")
        path = "../figures/{}".format(figName)
        
        imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path,
             "A&E waiting data for {} - Number of people waiting over four hours each month.".format(name))
        
        smoothWait = movingAverage(waitingData[waitingData != '-'])
        avAtt = np.mean(attendanceData[attendanceData != '-'])
        #print(waiting[i,:] != '-')
        #print(dates)
        sampleDates = dates[waitingData != '-']
        diff = smoothWait[0]-smoothWait[-1]
        
        if max(smoothWait) < 15 and avAtt<2000:
            chunk = '''
            <!--Minimal Change Hospital + less than 2000 monthy attendance-->

            <p>It looks like things haven't changed much for your hospital! On average only {} people attend this A&E 
            each month.</p>
            <p>Unfortunately, things aren't so great for the rest of England. After nearly a decade of Conservative rule,
            each month over <b>400,000</b> more people are made to wait <b>over four hours</b> to be seen at A&E than 
            in {}.

            {}

            {}
            
            '''.format(int(avAtt), int(round(min(sampleDates))), imgHTML, brexit_et_al)

        elif max(smoothWait) < 15:
            chunk = '''
            <!--Minimal Change Hospital + more than 2000 monthy attendance-->

            <p> It looks like things haven't changed much for your hospital!</p>
            <p>Unfortunately, things aren't so great for the rest of England. After nearly a decade of Conservative rule,
            each month over <b>400,000</b> more people are made to wait <b>over four hours</b> to be seen at A&E than in 2011.

            {}

            {}

            '''.format(imgHTML, brexit_et_al)

        elif avAtt>2000 and diff > 100:
            diff = smoothWait[0]-smoothWait[-1]
            chunk = '''
            <p>After nearly a decade of Conservative rule, on average, <b>{}</b> more people are being left to wait over 
            four hours at A&E at <b>your</b> hospital than back in {}.</p>

            {}

            <p>And things are bad for the rest of England too. Each month over <b>400,000</b> more people are made to wait
            <b>over four hours</b> to be seen at A&E than in 2011.

            {}
            
            '''.format(int(diff),int(np.floor(min(sampleDates))), imgHTML, brexit_et_al)
        elif diff < 100:
            #print(name)
            chunk = '''
            <p> 
            The data shows that, for this trust, on average {} fewer people 
            are waiting over four hours to be seen at A&E than in {}.
            </p>
            
            <p>
            Unfortunately, for many English hospitals, the situation is much worse.
            After nearly a decade of Conservative rule, each month over <b>400,000</b>
            more people are made to wait <b>over four hours</b> to be seen at A&E than in 2011.
            </p>

             {}

             {}

            '''.format(abs(int(diff)), int(np.floor(min(sampleDates))), imgHTML, brexit_et_al)
        else:
            #print(name)
            chunk = '''
            <p> 
            The data shows that thing's have gotten worse in your hospital. With {} more people each month 
             being forced to wait over 4 hours to be seen at A&E since {}.
            </p>
            <p>
             Unfortunately, for many English NHS Trusts, the situation is much worse.
             After nearly a decade of Conservative rule, each month over <b>400,000</b> more people are made 
             to wait <b>over four hours</b> to be seen at A&E than in 2011.
             </p>

             {}

             {}
            
            '''.format(int(diff), int(np.floor(min(sampleDates))), imgHTML, brexit_et_al)
    else:
        print("Error: Trust \"{}\" doesn't quite fit.".format(name))
        chunk = "<p> Error: Please contact website administrator. </p>"
            
    return chunk
    
def bed_change_per_trust(names, bed_data):
    better = 0
    worse = 0
    same = 0
    
    oldTrusts = get_all_dict_values(mergered_trusts)
    numTrusts = 0
    for i, name in enumerate(names):
        if name != "England" and name not in oldTrusts:
            if name not in mergered_trusts.keys():
                trust_beds = bed_data[i]
            else:
                trust_beds = combineBedData(bed_data, names, name)
            
            trust_beds = trust_beds[trust_beds!='-']
            
            if len(trust_beds) >= 2:
                numTrusts += 1
                change = (trust_beds[0]-trust_beds[-1])
                if change>=50:
                    better += 1
                elif change<=-50:
                    worse += 1
                else:
                    same += 1
    
    return better/numTrusts*100, same/numTrusts*100, worse/numTrusts*100

def make_bed_block(beds_data, name):
    ''' Generates the chunk of HTML relating to the A&E waiting time data for NHS trust <name>.
    
    TODO: Turn big chunks of text into global variables defined below with the other text.
    '''
    names, dates, beds = np.load(beds_data, allow_pickle=True)
    
    names = capitaliseFirst(names)
    
    i = np.where(names == name)[0]
    
    figName = makeFigureName(name, "beds")
    path = "../figures/{}".format(figName)
    imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path, 
                    "Number of available overnight beds for {}.".format(name))
    
    england_bed_change = beds[0][-1] - beds[0][0]
    england_bed_change_perc = (beds[0][-1] - beds[0][0])/beds[0][0]*100
    
    trusts_with_more, _, trust_with_fewer = bed_change_per_trust(names, beds)
    
    # Calculate fractional change
    if name not in mergered_trusts.keys():
        mask = beds[i][0] != "-"
        num_change = beds[i][0][mask][0] - beds[i][0][mask][-1]
        change = num_change/beds[i][0][mask][-1]
    else:
        # Combine merged trust data
        totalBeds = combineBedData(beds, names, name)
        mask = totalBeds != "-"
        
        # calculate change
        num_change = totalBeds[mask][0] - totalBeds[mask][-1]  
        change = num_change/totalBeds[mask][-1]
    
    if i == 0:

        chunk = england_beds.format(format_number(-num_change),
                format_number(-num_change), imgHTML, int(trust_with_fewer),
           int(trusts_with_more), brexit_et_al)
        
    elif change < -0.05 and change > -1:
        start_date = int(np.floor(dates[mask][-1]))
        percentage_change = abs(change)*100
       
        chunk = beds_worse.format(name, format_number(-num_change), start_date, 
           percentage_change, imgHTML, england_bed_change, 
           int(england_bed_change_perc), int(trust_with_fewer),
           int(trusts_with_more), brexit_et_al)
        
    elif change == -1:
        # All of the beds are gone
        start_date = int(np.floor(dates[mask][-1]))
        chunk = beds_all_gone.format(name, format_number(-num_change), 
                start_date, imgHTML, england_bed_change, 
           int(england_bed_change_perc), int(trust_with_fewer),
           int(trusts_with_more), brexit_et_al)
    elif change > 0.05:
        # Things are better
        start_date = int(np.floor(dates[mask][-1]))
        chunk = beds_better.format(name, int(trusts_with_more), start_date, format_number(num_change),
                     imgHTML,england_bed_change, 
           int(england_bed_change_perc), int(trust_with_fewer),
           int(trusts_with_more), brexit_et_al)
   
    else:
        # Not much change
        #print(name)
        
        start_date = int(np.floor(dates[mask][-1]))
        
        if num_change>1:
            more_or_less = "{} more beds".format(format_number(abs(num_change)))
        elif num_change == 1:
            more_or_less = "exactly 1 more bed"
        elif num_change<-1:
            more_or_less = "{} fewer beds".format(format_number(abs(num_change)))
        elif num_change==-1:
            more_or_less = "exactly 1 less bed"
        else:
            more_or_less = "exactly the same number of beds"
        chunk = beds_little_change.format(name, more_or_less, start_date, 
                   imgHTML, england_bed_change, 
           int(england_bed_change_perc), int(trust_with_fewer),
           int(trusts_with_more), brexit_et_al)
        
    return chunk   

def whichChunks(name, ane_names, bed_names, all_attendence, all_beds):
    '''Determins which HTML chunks are needed 
    
    Returns: Boolian array
        - A&E Needed
        - Beds Needed
    '''
    ane_block, bed_block = False, False
    
    # Check if A&E block is needed
    if name in ane_names:
        attendence = all_attendence[ane_names == name]
        ane_points = len(attendence[attendence != "-"])
        if ane_points >= 10:
            ane_block = True
            
    # if trust is made from merger, check the old trusts
    if name in mergered_trusts.keys():
        for oldTrust in mergered_trusts[name]:
            if oldTrust in ane_names:
                attendence = all_attendence[ane_names == oldTrust]
                #print(oldTrust, attendence)
                ane_points = len(attendence[attendence != "-"])
                if ane_points >= 10:  
                    ane_block = True
                    #print("merged A&E block added")
                    
    # Check if Bed block is needed
    if name in bed_names:
        beds = all_beds[bed_names == name]
        bed_points = len(beds[beds != "-"])
        if bed_points >= 4:
            bed_block = True
            
        # if trust is made from merger, check the old trusts
    if name in mergered_trusts.keys():
        for oldTrust in mergered_trusts[name]:
            if oldTrust in bed_names:
                beds = all_beds[bed_names == oldTrust]
                #print(oldTrust, beds)
                bed_points = len(beds[beds != "-"])
                if bed_points >= 4:
                    bed_block = True
                    #print("merged bed block added: {}".format(name))
            
    return ane_block, bed_block
    
def generate_meta(name, AnEblock, bedblock):
    '''Creates meta HTML for given trust page'''
    
    meta_desc = "Number of hospital beds" * bedblock \
        +  " and " * AnEblock * bedblock \
        + "A&E waiting data" * AnEblock \
        + " for {}.".format(name)
        
    meta_keywords = "NHS, " + "A&E waiting data, " * AnEblock \
        + "Number of hospital beds, " * bedblock \
        + name

    meta_HTML = '''\t<meta name="description" content="{}">
    <meta name="keywords" content="{}">'''.format(meta_desc, meta_keywords)
    
    return meta_HTML

def build_trust_pages(waiting_data, beds_data, news_file):
    print("Building trust pages...", end = " ")
    
    # Load data
    names1, dates, attendance, waiting = np.load(waiting_data, allow_pickle=True)
    names2, dates, beds = np.load(beds_data, allow_pickle=True)
    
    names2 = capitaliseFirst(names2)
    allNames = combineNames(names1, names2)
   
    # Load news
    newsDict = news.makeNewsDictionary(allNames,news_file)
    
    # list of old trusts
    oldTrusts = get_all_dict_values(mergered_trusts)
    for i, name in enumerate(allNames):
        #print(name)
        AnEblock, bedblock = whichChunks(name, names1, names2, attendance, beds)
        
        if (AnEblock or bedblock) and (name not in oldTrusts):
            
            url = makeURL(name)
            file = open(url, "w")
            
            meta_HTML = generate_meta(name, AnEblock, bedblock)
                        
            subTitleHTML = '''
            <div class = \"box\">
            \n<h2 class = \"subtitle\"><center>{}</center></h2>\n'''.format(name)
            
            
            tab_HTML = '<div class="tab">' + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'AnE')\" id=\"defaultOpen\">A&E Waiting Times</button>"*AnEblock + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'beds')\" id=\"defaultOpen\">Number of Beds</button>"*bedblock + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'news')\" id=\"defaultOpen\">News</button></div>" 
            
            
            supTextHTML = ""
            
            if AnEblock:
                supTextHTML += "<div id=\"AnE\" class=\"tabcontent\">" + make_AnE_waiting_block(waiting_data, name) + "</div>\n"
            
            if bedblock:
                supTextHTML += "<div id=\"beds\" class=\"tabcontent\">" + make_bed_block(beds_data, name) + "</div>\n"
                
            supTextHTML += news.makeNewsBlock(name, newsDict)
            
            supTextHTML += "</div>\n"
            
            file.write(''.join([headHTML1,headHTML2.format(name, meta_HTML),subTitleHTML,tab_HTML,
                                supTextHTML,tailHTML, tab_script]))
            file.close() 
    print("Done.")
    
####################################################################################################
###########################################  Website JS  ########################################### 
####################################################################################################
 
tab_script = '''\n
<script>
function openCity(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}

// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();
</script>'''

####################################################################################################
########################################### Website Text ########################################### 
####################################################################################################

siteURL = "https://howsmynhs.co.uk/"

###########################################   Home page   ########################################### 

homeHTML1 = '''
<html>
<head>

<!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-154345093-1"></script>
    
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'UA-154345093-1');
    </script>

    <title>How's my NHS?</title>
    
    <meta name="description" content="How many people are
    waiting long hours at A&E at your local NHS Trust? How many beds does your 
    Trust have? How has this all changed over time? Find out here.">
    <meta name="keywords" content="NHS, A&E, Overnight beds, data">
    
    <link rel="stylesheet" type="text/css" href="style.css">

</head>
<body>
<div class="maintitle">
<h1><center><a href="index.html"><img src="logo.png" alt="How's my NHS?" /></a></center></h1>
</div>

<center>
<div class="searchbox">
<div class="description">
<p style="padding: 0px; margin: 0px; padding-bottom: 10px;">
A&E waiting times are soring and there are fewer and fewer beds for those that need them.
The NHS is in crisis.</p>

<pstyle="padding: 0px; margin: 0px;">
How is your local NHS Trust doing?
</p>
</div>

<input type="text" id="myInput" onkeyup="myFunction()" placeholder="Search for name...">
</br>

</br></br>
<ul id="myUL">'''

homeHTML2 = '''
</ul> 
</div>

<script>
function myFunction() {
    // Declare variables
    var input, filter, ul, li, a, i;
    input = document.getElementById('myInput');
    filter = input.value.toUpperCase();
    ul = document.getElementById("myUL");
    li = ul.getElementsByTagName('li');

    if(input.value.length == 0){
        ul.style.display = "none";
        return;
    }else{
        ul.style.display = "block";
    }
    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "block";
        } else {
            li[i].style.display = "none";
        }
    }
}
</script>

</body>
</html>
''' 

#####################################################################################################
######################################  Trust pages text ############################################
#####################################################################################################

headHTML1 = '''
<html>
<head>

<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-154345093-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-154345093-1');
</script>'''


headHTML2 ='''<title>How's my NHS? - {}</title>
<link rel="stylesheet" type="text/css" href="../style.css">

<!-- meta data-->
{}

</head>
<body>
<div class="maintitle">
<h1><center><a href="../index.html"><img src="../logo.png" alt="How's my NHS?" width="392" height="230"/></a></center></h1>
</div>'''

tailHTML = '''
</body>
</html>'''

brexit_et_al = '''<p>Now, Brexit and an impending trade deal with Trump's US threatens to increase the NHS drug bill from &pound18 billion to as much as <b>&pound45 billion</b> a year while shutting out the nurses, carers and other workers that the health service depends on.</p>

            <p><i>Note: Over the past few months A&E attendance across England has fallen by more than 50% as people choose to stay at home to help reduce the pressure on the NHS 
            during the current pandemic.</i></p>
            
            <a href="..\whatnext.html" style = "text-decoration: none;"><div class="action">Call to Action</div></a>
            
            '''

####################################### Number of Beds Text #########################################

england_beds = u'''

            <p>Since the Conservatives came to power in 2010, there are {} fewer NHS beds in England. 
            That's {} fewer beds for those that who might need them. That's a decrease of over 20%. <p>

            {}
            
            <p> Roughly {}% of NHS trusts have fewer beds, whereas only around {}%
            of trusts have significantly more.</p>
            
            <center><img src=\"../figures/BedsPieChart.png\" alt=\"Beds Pie Chart\"></center>
            
            {}
                        
            '''

beds_worse = u'''
            <p>Under Conservative leadership, {} has around {} fewer beds than in {}. That's a {:.2}% drop in the number of beds for those who might desperately need them.<p>

            {}
            
            <p>Unfortunatly, similar things are being seen accross the country. 
            Overall, there are {} fewer NHS beds in England than in 2010. 
            That's a decrease of {}%.</p>
            
            <p>Over {}% of NHS trusts have fewer beds,  whereas only around {}%
            of trusts have significantly more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
            '''

beds_all_gone = u'''
            <p>Under Conservative leadership, {} has lost all {} of the beds it had in {}. This trust is no longer able to provide any beds for those that might need them.<p>

            {}
            
            <p>Unfortunatly, similar things are being seen accross the country. 
            Overall, there are {} fewer NHS beds in England than in 2010. 
            That's a decrease of {}%.</p>
            
            <p>Over {}% of NHS trusts have fewer beds, whereas only around {}%
            of trusts have significantly more. See our 
            <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
            '''

beds_better = u'''
            <p> {} is one of the lucky {}% of NHS England trusts which, under Conservative leadership, has more beds than in {}. With an increase of around {} beds.<p>

            {}
            
            <p>Unfortunatly, similar things are being seen accross the country. 
            Overall, there are {} fewer NHS beds in England than in 2010. 
            That's a decrease of {}%.</p>
            
            <p>Over {}% of NHS trusts have fewer beds,  whereas only around {}%
            of trusts have significantly more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
           '''

beds_little_change = u'''
            <p> For better or for worse, the number of beds owned by {} hasn't changed much. Under Conservative leadership, the trust has {} than in {}.<p>

            {}
            
            <p>Unfortunatly, this isn't the case for many NHS trusts accross the country.
            Overall, there are {} fewer NHS beds in England than in 2010. 
            That's a decrease of over {}%.</p>
            
            <p>Over {}% of NHS trusts have fewer beds,  whereas only around {}%
            of trusts have significantly more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
           '''


