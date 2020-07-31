'''
Module for building the HowsMyNHS website
'''
import numpy as np
import matplotlib.pyplot as plt

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

################## Generate Plots ##################

def plotWaitingData(data):
    ''' Plot data NHS England A&E 4 hour waiting data'''
    
    print("Generating 4 hour waiting time graphs...", end = " ")
    
    # Load data
    NHSdata = np.load(data, allow_pickle=True)
    
    names = NHSdata[0]
    dates = dates2num(NHSdata[1])
    attendance = NHSdata[2]
    waiting = NHSdata[3]
    
    str2num = np.vectorize(float)
    intvec = np.vectorize(int)
    import matplotlib
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rc('font', size=20)

    # Plot and save the data

    for i, name in enumerate(names[:]):
        if type(name) == str:
            mask = (waiting[i,:] != '-')
            if name == "England":
                NumWaiting = intvec(str2num(waiting[i,:][mask]))
                fig = plt.figure(figsize=(7,5))
                plt.plot(dates[mask], NumWaiting/1e6,'k.',lw=3,label="data")
                plt.plot(movingAverage(dates[mask]), movingAverage(NumWaiting/1e6), 'r-',label="moving average",lw=2)
                plt.ylabel("Number of people\n waiting over 4 hours (million)")
                figName = '_'.join(name.lower().split(' '))
                if abs(dates[mask][0]-dates[mask][-1])<1.5:
                    #print("Small", name)
                    plt.xlim([min(dates[mask])-0.2, np.floor(max(dates[mask]))+1])
                plt.legend()
                plt.tight_layout()
                plt.savefig("figures/{}.png".format(figName))
                plt.close()
                
            elif sum(mask)>10:
                NumWaiting = intvec(str2num(waiting[i,:][mask]))
                fig = plt.figure(figsize=(7,5))
                plt.plot(dates[mask], NumWaiting,'k.',lw=3,label="data")
                plt.plot(movingAverage(dates[mask]), movingAverage(NumWaiting), 'r-',label="moving average",lw=2)
                plt.ylabel("Number of people\n waiting over 4 hours")
                figName = '_'.join(name.lower().split(' '))
                if abs(dates[mask][0]-dates[mask][-1])<1.5:
                    #print("Small:", name)
                    plt.xlim([min(dates[mask])-0.2, np.floor(max(dates[mask]))+1])
                plt.legend()
                plt.tight_layout()
                plt.savefig("figures/{}.png".format(figName))
                plt.close()
                
    print("Done.")
    
def MakeHomepage(data):
    print("Building homepage...", end = " ")
    
    # Load data
    NHSdata = np.load(data, allow_pickle=True)
    names = NHSdata[0]
    dates = dates2num(NHSdata[1])
    attendance = NHSdata[2]
    waiting = NHSdata[3]
    
    # Make list of hospital names
    hospitalLinksList = []
    for i, name in enumerate(names):
            if type(name) == str:
                mask = (waiting[i,:] != '-')
                if sum(mask)>10:
                    url_prefix = '_'.join(name.lower().split(' '))
                    url = ''.join(["hospitals/",url_prefix,".html"])
                    hospitalLinksList.append("<li><a href=\"{}\">{}</a></li>\n".format(url,name))

    hospitalLinks = ''.join(hospitalLinksList)
    file = open("index.html", "w") 

    file.write(''.join([homeHTML1, hospitalLinks, homeHTML2])) 
 
    file.close() 
    
    print("Done")
    
    
####################################################################################################
########################################### Website Text ########################################### 
####################################################################################################

siteURL = "https://howsmynhs.co.uk/"

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
<link rel="stylesheet" type="text/css" href="style.css">

</head>
<body>
<div class="maintitle">
<h1><center><a href="index.html"><img src="logo.png" alt="How's my NHS?" /></a></center></h1>
</div>

<center>
<div class="searchbox">
<div class="description">
<p style="padding: 0px; margin: 0px;">The number of people waiting over 4 hours at A&E in England has increase by over 900%.
How is your local NHS Trust doing?</p>
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












