'''
Module for building the HowsMyNHS website
'''

# standard python packages
import numpy as np

# local packages
import build_website.news as news
import build_website.process_data as pd




str2num = np.vectorize(float)
intvec = np.vectorize(int)

NHSblue = "#0072CE"

# Merged trusts
mergered_trusts = {
    "Bedfordshire Hospitals NHS Foundation Trust": \
        ['Bedford Hospital NHS Trust',
         'Luton And Dunstable University Hospital NHS Foundation Trust'],
        
    "Mid And South Essex NHS Foundation Trust" : \
        ["Basildon And Thurrock University Hospitals NHS Foundation Trust",
          "Mid Essex Hospital Services NHS Trust",
          "Southend University Hospital NHS Foundation Trust"],
        
    "Manchester University NHS Foundation Trust" : \
        ["Central Manchester University Hospitals NHS Foundation Trust",
         "University Hospital Of South Manchester NHS Foundation Trust"],
        
    "Liverpool University Hospitals NHS Foundation Trust" : \
        ["Royal Liverpool And Broadgreen University Hospitals NHS Trust",
         "Aintree University Hospital NHS Foundation Trust"]
        
}



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
    names2 = pd.capitaliseFirst(names2)
    
    allNames = pd.combineNames(names1, names2)
    
    # Make list of hospital names
    hospitalLinksList = []
    for i, name in enumerate(allNames):
        # Check if the trust is in contained in the values of merged_trust
        # i.e. is it an old trust which has since merged into something else.
        oldTrust = name in pd.get_all_dict_values(mergered_trusts)
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
    '''
    names, dates, attendance, waiting = np.load(data, allow_pickle=True)
    dates = pd.dates2num(dates)
    i = np.where(names == name)[0][0]
    
    
    if name not in mergered_trusts.keys():
        attendanceData = attendance[i,:]
        waitingData = waiting [i,:]
    else:
        # Combine merged trust data
        attendanceData, _ = pd.combineAnEData(attendance, 
                                              names,
                                              name,
                                              mergered_trusts)
        waitingData, _ = pd.combineAnEData(waiting, 
                                           names, 
                                           name,
                                           mergered_trusts)
        
    if i == 0:
        # Get figure path
        figName = pd.makeFigureName(name, "waiting", "svg")
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
        figName = pd.makeFigureName(name, "waiting", "svg")
        path = "../figures/{}".format(figName)
        
        imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path,
             "A&E waiting data for {} - Number of people waiting over four hours each month.".format(name))
        
        smoothWait = pd.movingAverage(waitingData[waitingData != '-'])
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
            <p>After nearly a decade of Conservative rule, on average, <b>{}</b> more people each month are being left to wait over 
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
    


def make_bed_block(beds_data, name):
    ''' Generates the chunk of HTML relating to the A&E waiting time data for NHS trust <name>.

    '''
    names, dates, beds = np.load(beds_data, allow_pickle=True)
    
    names = pd.capitaliseFirst(names)
    
    i = np.where(names == name)[0]
    
    figName = pd.makeFigureName(name, "beds", "svg")
    path = "../figures/{}".format(figName)
    imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path, 
                    "Number of available overnight beds for {}.".format(name))
    
    england_bed_change = beds[0][-1] - beds[0][0]
    england_bed_change_perc = (beds[0][-1] - beds[0][0])/beds[0][0]*100
    
    trusts_with_more, _, trust_with_fewer = pd.bed_change_per_trust(names, 
                                                                    beds,
                                                                    mergered_trusts)
    
    # Calculate fractional change
    if name not in mergered_trusts.keys():
        mask = beds[i][0] != "-"
        num_change = beds[i][0][mask][0] - beds[i][0][mask][-1]
        change = num_change/beds[i][0][mask][-1]
    else:
        # Combine merged trust data
        totalBeds = pd.combineBedData(beds,
                                      names, 
                                      name, 
                                      mergered_trusts)
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
           int(percentage_change), imgHTML, england_bed_change, 
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
        chunk = beds_better.format(name, int(trusts_with_more), start_date, 
                format_number(num_change), imgHTML,england_bed_change, 
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

def makeCovidBlock(covid_data, name):
    names, dates, covid_deaths = np.load(covid_data, allow_pickle=True)
    names = pd.capitaliseFirst(names)
    #print(name, covid_deaths[names == name].shape)
    trust_deaths = covid_deaths[names == name][0]
    
    total_deaths = sum(trust_deaths)
    weeks_deaths = sum(trust_deaths[-7::])
    
    # image html
    figName = pd.makeFigureName(name, "covid", "svg")
    path = "../figures/{}".format(figName)
    imgHTML = "<center><img src=\"{}\" alt=\"{}\"></center>".format(path, 
                    "Number of Covid-19 related deaths for {}.".format(name))

    if name == "England":
        first_para = '''<p>
        So far, for yesterday, there have been {} reported deaths related to Covid-19 in English hospitals.
        This gives a total of {} deaths over the past week and {} since the outbreak of the pandemic.
        </p>'''.format(int(trust_deaths[-1]), int(weeks_deaths), int(total_deaths))
    elif total_deaths == 0:
        first_para = "<p>No deaths.</p>"
    elif total_deaths == 1:
        first_para = "<p>Total equal to one.</p>"
    elif total_deaths > 1:
        first_para = "<p>Total greater than one.</p>"
    chunk = first_para + imgHTML
    
    return chunk

def whichChunks(name, ane_names, bed_names, covid_names, all_waiting, all_beds, all_covid):
    '''Determins which HTML chunks are needed 
    
    Returns: Boolian array
        - A&E Needed
        - Beds Needed
    '''
    ane_block, bed_block, covid_block = False, False, False
    
    # Check if A&E block is needed
    if name in ane_names:
        attendence = all_waiting[ane_names == name]
        ane_points = len(attendence[attendence != "-"])
        if ane_points >= 10:
            ane_block = True
            
    # if trust is made from merger, check the old trusts
    if name in mergered_trusts.keys():
        for oldTrust in mergered_trusts[name]:
            if oldTrust in ane_names:
                attendence = all_waiting[ane_names == oldTrust]
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
                    
    if name in covid_names:
        covid_block = True
            
    return ane_block, bed_block, covid_block
    
def generate_meta(name, AnEblock, bedblock):
    '''Creates meta HTML for given trust page'''
    
    meta_desc = '''Over the last 10 years A&E waiting times have risen and the number of available overnight beds has fallen. Find out here out {} is doing.'''.format(name)
        

    meta_image = "https://howsmynhs.co.uk/figures/og/" + pd.makeFigureName(name, "og", "png")
    
    if name == "England":
        subTitle = "NHS England Overview"
    else:
        subTitle = name
    
    meta_title = "How's my NHS? - " + subTitle + " [Official Data]"
    
    meta_url = "https://howsmynhs.co.uk/" + makeURL(name)
    
    meta_HTML = '''\t<meta name="description" content="{}" />
    <!--  General META Tags -->
    <meta property="og:title" content="{}" />
    <meta property="og:image" content="{}" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:url" content="{}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="How's My NHS?">
    
    <!--  Twitter META Tags -->
    <meta name="twitter:title" content="{}">
    <meta name="twitter:description" content="{}">
    <meta name="twitter:image" content="{}">
    <meta name="twitter:card" content="summary_large_image">
    '''.format(meta_desc,
    meta_title,
    meta_image,
    meta_url,
    meta_title,
    meta_desc,
    meta_image)
    
    return meta_HTML

def build_trust_pages(waiting_data, beds_data, covid_data, news_file):
    print("Building trust pages...", end = " ")
    
    # Load data
    names1, dates, attendance, waiting = np.load(waiting_data, allow_pickle=True)
    names2, dates, beds = np.load(beds_data, allow_pickle=True)
    names3, dates, covid_deaths = np.load(covid_data, allow_pickle=True)
    
    # Format and combine all names
    names2 = pd.capitaliseFirst(names2)
    names3 = pd.capitaliseFirst(names3)
    allNames = pd.combineNames(names1, names2)
    allNames = pd.combineNames(allNames, names3)
    
    # Load news
    newsDict = news.makeNewsDictionary(allNames,news_file)
    
    # list of old trusts
    oldTrusts = pd.get_all_dict_values(mergered_trusts)
    for i, name in enumerate(allNames):
        #print(name)
        AnEblock, bedblock, covidblock = whichChunks(name, names1, names2, 
                                                     names3, attendance, beds, covid_deaths)
        
        if (AnEblock or bedblock or covidblock) and (name not in oldTrusts):
            
            url = makeURL(name)
            file = open(url, "w")
            
            if name == "England":
                subTitle = "NHS England Overview"
            else:
                subTitle = name
            
            meta_HTML = generate_meta(name, AnEblock, bedblock)
                        
            subTitleHTML = '''
            <div class = \"box\">
            \n<h2 class = \"subtitle\">{}</h2>\n'''.format(subTitle)
            
            
            tab_HTML = '<div class="tab">' + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'AnE')\" id=\"defaultOpen\">A&E Waiting Times</button>"*AnEblock + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'beds')\" id=\"defaultOpen\">Number of Beds</button>"*bedblock + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'covid')\" id=\"defaultOpen\">Covid-19 Deaths</button>"*covidblock + \
            "<button class=\"tablinks\" onclick=\"openCity(event, 'news')\" id=\"defaultOpen\">News</button></div>" 
            
            
            supTextHTML = ""
            
            if AnEblock:
                supTextHTML += "<div id=\"AnE\" class=\"tabcontent\">" + make_AnE_waiting_block(waiting_data, name) + "</div>\n"
            
            if bedblock:
                supTextHTML += "<div id=\"beds\" class=\"tabcontent\">" + make_bed_block(beds_data, name) + "</div>\n"
            if covidblock:
                supTextHTML += "<div id=\"covid\" class=\"tabcontent\">" + makeCovidBlock(covid_data, name) + "</div>\n"
                
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

    <title>How's my NHS? - Offical NHS data for your local NHS Trust</title>
    
    <meta name="description" content="Over the last 10 years A&E waiting times have risen and 
    the number of available overnight beds has fallen. How is your local NHS
    Trust doing?">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!--  General META Tags -->
    <meta property="og:title" content="How's my NHS? - Offical NHS data for your local NHS Trust" />
    <meta property="og:image" content="https://howsmynhs.co.uk/figures/og/england-og.png" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:url" content="https://howsmynhs.co.uk/hospitals/england.html" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="How's My NHS?">
    
    <!--  Twitter META Tags -->
    <meta name="twitter:title" content="How's my NHS? - Offical NHS data for your local NHS Trust">
    <meta name="twitter:description" content="Over the last 10 years A&E waiting times have risen and the number of available overnight beds has fallen. How is your local NHS Trust doing?">
    <meta name="twitter:image" content="https://howsmynhs.co.uk/figures/og/england-og.png">
    <meta name="twitter:card" content="summary_large_image">
    
    <link href="favicon.png" rel="icon" type="image/x-icon" />
    <link rel="stylesheet" type="text/css" href="style.css">
    <link rel="stylesheet" type="text/css" href="narrow.css">
</head>
<body>

<!--  Navigation bar -->
<ul id="nav-links">
  <li><a href="" class="active">Home</a></li>
  <li><a href="articles.html">Articles</a></li>
  <li style="float:right"><a href="about.html">About</a></li>
</ul>

<div class="maintitle">
<a href="index.html"><img src="logo.png" alt="How's my NHS?" /></a>
</div>

<div class="searchbox">
<div class="description">
<p style="padding: 0px; margin: 0px; padding-bottom: 10px;">
A&E waiting times are soaring and there are fewer and fewer beds for those that need them.
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


headHTML2 ='''<title>How's my NHS? - {} [Official Data]</title>
<link href="../favicon.png" rel="icon" type="image/x-icon" />
<link rel="stylesheet" type="text/css" href="../style.css">
<link rel="stylesheet" type="text/css" href="../narrow.css">
<!-- meta data-->
{}

<meta name="viewport" content="width=device-width, initial-scale=1.0">

</head>
<body>

<!--  Navigation bar -->
<ul id="nav-links">
  <li><a href="../index.html" class="active">Home</a></li>
  <li><a href="../articles.html">Articles</a></li>
  <li style="float:right"><a href="../about.html">About</a></li>
</ul>

<div class="maintitle2">
<a href="../index.html"><img src="../logo.png" alt="How's my NHS?"/></a>
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
            
            <center><img src=\"../figures/BedsPieChart.svg\" alt=\"Beds Pie Chart\"></center>
            
            {}
                        
            '''

beds_worse = u'''
            <p>Under Conservative leadership, {} has around {} fewer beds than in {}. That's a {}% drop in the number of beds for those who might desperately need them.<p>

            {}
            
            <p>Unfortunately, similar things are being seen accross the country. 
            Overall, there are {} fewer NHS beds in England than in 2010. 
            That's a decrease of {}%.</p>
            
            <p>Over {}% of NHS trusts have fewer beds,  whereas only around {}%
            of trusts have significantly more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
            '''

beds_all_gone = u'''
            <p>Under Conservative leadership, {} has lost all {} of the beds it had in {}. This trust is no longer able to provide any beds for those that might need them.<p>

            {}
            
            <p>Unfortunately, similar things are being seen accross the country. 
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
            
            <p>Unfortunately, similar things are being seen accross the country. 
            Overall, there are {} fewer NHS beds in England than in 2010. 
            That's a decrease of {}%.</p>
            
            <p>Over {}% of NHS trusts have fewer beds,  whereas only around {}%
            of trusts have significantly more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
           '''

beds_little_change = u'''
            <p> For better or for worse, the number of beds owned by {} hasn't changed much. Under Conservative leadership, the trust has {} than in {}.<p>

            {}
            
            <p>Unfortunately, this isn't the case for many NHS trusts accross the country.
            Overall, there are {} fewer NHS beds in England than in 2010. 
            That's a decrease of over {}%.</p>
            
            <p>Over {}% of NHS trusts have fewer beds,  whereas only around {}%
            of trusts have significantly more. See our <a href = "england.html"> summary page for the whole of England</a>.</p>
            
            {}
           '''


