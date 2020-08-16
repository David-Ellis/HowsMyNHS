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

def format_number(num):
    '''rounds number to nearest hundred and adds commas'''
    if num > 100:
        num = int(np.round(num / 100.0)) * 100
        out = "{:,}".format(num)
    else:
        out = "{}".format(num)
    return out


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
                
            elif sum(mask)>=10:
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
    
def plotBedData(data):
    ''' Plot the number of beds at NHS England Trusts'''
    
    print("Generating graphs for the number of beds ...", end = " ")
    
    # Load data
    NHSdata = np.load(data, allow_pickle=True)
    
    names, dates, beds = NHSdata
    
    import matplotlib
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rc('font', size=20)

    # Plot and save the data

    for i, name in enumerate(names[:]):
        if type(name) == str:
            mask = (beds[i,:] != '-')
                  
            if sum(mask)>=4:
                fig = plt.figure(figsize=(7,5))
                plt.bar(dates[mask], beds[i,:][mask]*1e-3,lw=3, width = 0.2, align='center', 
                        alpha=1, color="#005EB8")
                plt.ylabel("Total # of Available Beds\n(Thousands)")
                
                plt.ylim(0.98*min(beds[i,:][mask])*1e-3, 1.01*max(beds[i,:][mask])*1e-3)
                figName = '_'.join(name.lower().split(' '))
                plt.tight_layout()
                plt.savefig("figures/{}_beds.png".format(figName))
                plt.close()
                
    print("Done.")
    
def capitaliseFirst(string_list):
    '''Capitalised the first letter of each word in each string in a list'''
    
    for i, string in enumerate(string_list):
        words = string.split(" ")
        words = [word[0].upper() + word[1:] for word in words]
        string_list[i] = " ".join(words).replace("Nhs", "NHS")
        
    return string_list
    
def combineNames(names1, names2):
    '''Makes a single list of each name appearing in either list'''
    namesOut = names1
    for name in names2:
        if name not in names1:
            namesOut = np.append(namesOut, name)
    return namesOut

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
        if type(name) == str:
            ane_points, bed_points = 0, 0
            
            if name in names1:
                ane_points = len(waiting[names1 == name][waiting[names1 == name] != '-'])
                
            if name in names2:
                bed_points = len(beds[names2 == name][beds[names2 == name] != '-'])
            
            if ane_points >= 10 or bed_points>= 4:
                url_prefix = '_'.join(name.lower().split(' '))
                url = ''.join(["hospitals/",url_prefix,".html"])
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
    
    if i == 0:
        # Get figure path
        figName = '_'.join(name.lower().split(' '))
        path = "../figures/{}.png".format(figName)

        imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path, name)

        supTextHTML = u'''

            <p>After nearly a decade of Conservative rule, in December over <b>500,000</b> more people were made to wait
            <b>over four hours</b> to be seen at A&E than in 2011. That's an increase of over <b>900%</b>.
            The number of people attending A&E, however, had only increased by less than 30%.<p>

            {}

            {}
                  
            '''

        chunk = supTextHTML.format(imgHTML, brexit_et_al)
        
    elif sum(attendance[i,:] != '-')>=10:
        # Get figure path
        figName = '_'.join(name.lower().split(' '))
        path = "../figures/{}.png".format(figName)
        
        imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path, name)

        smoothWait = movingAverage(waiting[i,:][waiting[i,:] != '-'])
        avAtt = np.mean(attendance[i,:][attendance[i,:] != '-'])
        #print(waiting[i,:] != '-')
        #print(dates)
        sampleDates = dates[waiting[i,:] != '-']
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
            <p> The data show's that, for this trust, on average {} fewer people are waiting over four hours to be seen at A&E than in {}. It many English hospitals, the situation is much worse. After nearly a decade of Conservative rule, each month over <b>400,000</b> more people are made to wait <b>over four hours</b> to be seen at A&E than in 2011.</p>

             {}

             {}

            '''.format(abs(int(diff)), int(np.floor(min(sampleDates))), imgHTML, brexit_et_al)
        else:
            #print(name)
            chunk = '''
            <p> The data show's that thing's have gotten worse in your hospital. With {} more people each month 
             being forced to wait over 4 hours to be seen at A&E since {}. It many English hospitals, the situation is much
             worse. After nearly a decade of Conservative rule, each month over <b>400,000</b> more people are made 
             to wait <b>over four hours</b> to be seen at A&E than in 2011.</p>

             {}

             {}
            
            '''.format(int(diff), int(np.floor(min(sampleDates))), imgHTML, brexit_et_al)
            
            
    return chunk
    
def make_bed_block(beds_data, name):
    ''' Generates the chunk of HTML relating to the A&E waiting time data for NHS trust <name>.
    
    TODO: Turn big chunks of text into global variables defined below with the other text.
    '''
    names, dates,  beds = np.load(beds_data, allow_pickle=True)
    
    names = capitaliseFirst(names)
    
    i = np.where(names == name)[0]
    
    figName = '_'.join(name.lower().split(' '))
    path = "../figures/{}_beds.png".format(figName)
    imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path, name)
    
    # Calculate fractional change
    mask = beds[i][0] != "-"
    num_change = beds[i][0][mask][0] - beds[i][0][mask][-1]
    change = num_change/beds[i][0][mask][-1]
    
    #print("beds=", beds[i])
    #print(len(dates), len(mask))
    
    if i == 0:

        chunk = england_beds.format(format_number(-num_change), format_number(-num_change), imgHTML, brexit_et_al)
        
    elif change < -0.05 and change > -1:
        start_date = int(np.floor(dates[mask][-1]))
        percentage_change = abs(change)*100
       
        chunk = beds_worse.format(name, format_number(-num_change), start_date, percentage_change, imgHTML, brexit_et_al)
        
    elif change == -1:
        # All of the beds are gone
        start_date = int(np.floor(dates[mask][-1]))
        chunk = beds_all_gone.format(name, format_number(-num_change), start_date, imgHTML, brexit_et_al)
    elif change > 0.05:
        # Things are better
        start_date = int(np.floor(dates[mask][-1]))
        chunk = beds_better.format(name, start_date, format_number(num_change), imgHTML, brexit_et_al)
   
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
        chunk = beds_little_change.format(name, more_or_less, start_date, imgHTML, brexit_et_al)
        
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
            
    # Check if Bed block is needed
    if name in bed_names:
        beds = all_beds[bed_names == name]
        bed_points = len(beds[beds != "-"])
        if bed_points >= 4:
            bed_block = True
            
    return ane_block, bed_block
    
def build_trust_pages(waiting_data, beds_data):
    print("Building trust pages...", end = " ")
    
    # Load data
    names1, dates, attendance, waiting = np.load(waiting_data, allow_pickle=True)
    names2, dates, beds = np.load(beds_data, allow_pickle=True)
    
    names2 = capitaliseFirst(names2)
    allNames = combineNames(names1, names2)
   
    for i, name in enumerate(allNames):
        
        AnEblock, bedblock = whichChunks(name, names1, names2, attendance, beds)
        
        if AnEblock or bedblock:
            
            url_prefix = '_'.join(name.lower().split(' '))
            url = ''.join([url_prefix,".html"])
            file = open("hospitals/{}".format(url), "w")
            
                        
            subTitleHTML = '''
            <div class = \"box\">
            \n<h2 class = \"subtitle\"><center>{}</center></h2>\n'''.format(name)
            
            
            tab_HTML = '<div class="tab">' + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'AnE')\" id=\"defaultOpen\">A&E Waiting Times</button>"*AnEblock + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'beds')\" id=\"defaultOpen\">Number of Beds</button>"*bedblock + "</div>"
            
            
            supTextHTML = ""
            
            if AnEblock:
                supTextHTML += "<div id=\"AnE\" class=\"tabcontent\">" + make_AnE_waiting_block(waiting_data, name) + "</div>\n"
            
            if bedblock:
                supTextHTML += "<div id=\"beds\" class=\"tabcontent\">" + make_bed_block(beds_data, name) + "</div>\n"
                
            supTextHTML += "</div>\n"
            
            file.write(''.join([headHTML,subTitleHTML,tab_HTML,
                                supTextHTML,whatNextHTML,tailHTML, tab_script]))
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

#####################################################################################################
######################################  Trust pages text ############################################
#####################################################################################################

headHTML = '''
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
<link rel="stylesheet" type="text/css" href="../style.css">

</head>
<body>
<div class="maintitle">
<h1><center><a href="../index.html"><img src="../logo.png" alt="How's my NHS?" width="392" height="230"/></a></center></h1>
</div>'''

tailHTML = '''
</body>
</html>'''

whatNextHTML = '''
    </br>
    <div class ="box">
    <h2 class = \"subtitle\"><center>What Next?</center></h2>\n
    
    <p><b style="color:#005EB8;">Prevent the spread:</b> With the outbreak of the Coronavirus (COVID-19)
    the NHS is under more pressure than ever. We <b>need</b> to do everything we can to slow its
    spread. Follow the official government guidance: 
    <ul>
    <li>Stay at home as much as possible</li>
    <li>Work from home if you can</li>
    <li>Limit contact with other people</li>
    <li>Keep your distance from people not in your household (2 metres apart where possible)</li>
    <li>Wash your hands regularly</li>
    
    </ul>
    Many young people experience few to no symptoms at all but can still carry the virus and pass 
    it on to those who are more vulnerable.
    </p>
    <p>
    Stay informed with reliable sources such as the governments 
    <a href="https://www.gov.uk/coronavirus" target="_blank">offical Coronavirus page</a>.
    </p> 

    <p><b style="color:#005EB8;">Share the message:</b> Fight for change. Let your friends and family know that the Conservatives 
    are not the party for the NHS. One vote may have little impact, particularly with our broken electoral system. 
    But together we can bring about great change.</p> 

<div id="share-buttons" align="center" style="color:#ffffff;">
    
    <!-- Twitter -->
    <a href="https://twitter.com/share?url=https://howsmynhs.co.uk/&amp;text=How%20has%20YOUR%20NHS%20changed%20under%20the%20Tories?&amp;hashtags=NHS"target="_blank">
    <img src="https://simplesharebuttons.com/images/somacro/twitter.png" alt="Twitter" /></a>
    
    <!-- Email -->
    <a href="mailto:?Subject=Simple Share Buttons&amp;Body=How%20has%20YOUR%20NHS%20changed%20under%20the%20Tories?%20 https://howsmynhs.co.uk/">
    <img src="https://simplesharebuttons.com/images/somacro/email.png" alt="Email" /></a>
 
    <!-- Facebook -->
    <a href="http://www.facebook.com/sharer.php?u=https://howsmynhs.co.uk/" target="_blank">
    <img src="https://simplesharebuttons.com/images/somacro/facebook.png" alt="Facebook" /></a>
    
    <!-- Reddit -->
    <a href="http://reddit.com/submit?url=https://howsmynhs.co.uk/&amp;title=How has your NHS changed under the Tories?" target="_blank">
    <img src="https://simplesharebuttons.com/images/somacro/reddit.png" alt="Reddit" /></a>

    <!-- Tumblr-->
    <a href="http://www.tumblr.com/share/link?url=https://howsmynhs.co.uk/.com&amp;title=Simple Share Buttons" target="_blank">
    <img src="https://simplesharebuttons.com/images/somacro/tumblr.png" alt="Tumblr" /></a>
    
    <!-- LinkedIn -->
    <a href="http://www.linkedin.com/shareArticle?mini=true&amp;url=https://howsmynhs.co.uk/" target="_blank">
    <img src="https://simplesharebuttons.com/images/somacro/linkedin.png" alt="LinkedIn" /></a>
    
   <! -- Share buttons from: https://simplesharebuttons.com/html-share-buttons/ --!>
</div>

    <p><b style="color:#005EB8;">Email your MP:</b> Enter your postcode 
    <a href="https://members.parliament.uk/" target="_blank">here</a>.
    to find the email address for your local MP. Send them this graph of 
    how <b>your</b> local A&E has changed and urge them to use their power to
    protect it from further damage and to restore our NHS to it's former 
    glory.
    </p>

    <p><b style="color:#005EB8;">Use this data:</b> All of the data presented here, as well as the code used to collect it, is <a href="https://github.com/David-Ellis/NHSdata" target="_blank"> freely availble via github</a>. 
    You don't need to cite us. This is all publically available data from <a href="https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/" target="_blank">NHS England</a>. 
    </p>    
    
    </br></br></br></br></br></br></br></br>
    '''

brexit_et_al = '''<p>Now, Brexit and an impending trade deal with Trump's US threatens to increase the NHS drug bill from &pound18 billion to as much as <b>&pound45 billion</b> a year while shutting out the nurses, carers and other workers that the health service depends on.</p>

            <p><i>Note: Over the past few months A&E attendance across England has fallen by more than 50% as people choose to stay at home to help reduce the pressure on the NHS 
            during the current pandemic.</i></p>'''

####################################### Number of Beds Text #########################################

england_beds = u'''

            <p>Since the Conservatives came to power in 2010, there are {} fewer NHS beds in England. That's {} fewer beds for those that who might need them. That's a decrease of over 10%. <p>

            {}
            
            <p>Over 41% of NHS trusts have fewer beds, whereas less than 25% of trusts have more.</p>
            
            <center><img src=\"..\BedsPieChart.png\" alt=\"Beds Pie Chart\"></center>
            
            {}
                        
            '''

beds_worse = u'''
            <p>Under Conservative leadership, {} has around {} fewer beds than in {}. That's a {:.3}% drop in the number of beds for those who might desperately need them.<p>

            {}
            
            <p>Unfortunatly, similar things are being seen accross the country. Overall, there are 15,500 fewer NHS beds in England than in 2010. That's a decrease of over 10%.</p>
            
            <p>Over 41% of NHS trusts have fewer beds, whereas less than 25% of trusts have more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
            '''

beds_all_gone = u'''
            <p>Under Conservative leadership, {} has lost all {} of the beds it had in {}. This trust is no longer able to provide any beds for those that might need them.<p>

            {}
            
            <p>Unfortunatly, similar things are being seen accross the country. Overall, there are 15,500 fewer NHS beds in England than in 2010. That's a decrease of over 10%.</p>
            
            <p>Over 41% of NHS trusts have fewer beds, whereas less than 25% of trusts have more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
            '''

beds_better = u'''
            <p> {} is one of the lucky 25% of NHS England trusts which, under Conservative leadership, has more beds than in {}. With an increase of around {} beds.<p>

            {}
            
            <p>Unfortunatly, this isn't the case for many NHS trusts accross the country. Overall, there are 15,500 fewer NHS beds in England than in 2010. That's a decrease of over 10%.</p>
            
            <p>Over 41% of NHS trusts have fewer beds, whereas less than 25% of trusts have more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
           '''

beds_little_change = u'''
            <p> For better or for worse, the number of beds owned by {} hasn't changed much. Under Conservative leadership, the trust has {} than in {}.<p>

            {}
            
            <p>Unfortunatly, this isn't the case for many NHS trusts accross the country. Overall, there are 15,500 fewer NHS beds in England than in 2010. That's a decrease of over 10%.</p>
            
            <p>Over 41% of NHS trusts have fewer beds, whereas less than 25% of trusts have more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
           '''


