'''
Playing around with building functions for generating the news page
'''

from pandas_ods_reader import  read_ods
import numpy as np

def sanitize_names(names):
    names = list(names)
    # Remove all trailing spaces
    for i, name in enumerate(names):
        while names[i][-1] == " ":
            names[i] = names[i][:-1]
    return np.asarray(names)

def collectTrustNews(name, allNewsArray):
    names = sanitize_names(allNewsArray[:,0])
    #print(names, ">>>>>>"+name+"\n\n\n\n\n")
    releventItems = allNewsArray[names == name]
    #print(releventItems)
    newsItems = [newsItem for newsItem in releventItems]
    
    return newsItems

def makeNewsDictionary(allNames, newsFile):
    df = read_ods(newsFile, 1, headers=False)
    everything = df.values[4:,:]
    
    news_dict = {}
    
    for name in allNames:
        news_dict[name] = collectTrustNews(name, everything)
        
    return news_dict
    
def makeNewsItem(newsItem):
    _, title, source,date, url, theme, decription, \
    paywall, img_src, img_alt = newsItem
    
    if img_src != None:
        imgHTML = "<img src=\"{}\" alt=\"{}\">".format(img_src, img_alt) 
    else:
        imgHTML = ""
        
    itemHTML = '''
    <div id="news-item">
	
		<span id="news-text">
		{}
		
		<p id="news-date"> {} </p>
		<h3><a href = "{}">{}</a></h3>
		<p>{}</p>
		</span>
		
		
		<p id = "news-source">Source: NHS</p>
	</div>
    
    '''.format(imgHTML, date,url, title, decription)
    
    return itemHTML

def makeNewsBlock(name, newsDict):
    '''Returns news block HTML for trust name based of the contents of 
    newsDict.'''    

    trust_news = newsDict[name]
    if len(trust_news)==0:
        blockHTML = noNewsHTML
    else:
        blockHTML = "<div id=\"news\" class=\"tabcontent\">"
        for newsItem in trust_news:
            blockHTML += makeNewsItem(newsItem)
        blockHTML += missing_somthing
        blockHTML += "\n</div>"
    return blockHTML

noNewsHTML = '''	
    <div id="news" class="tabcontent">
    	<div id="news-missing">
    		<h3>Oops, there's nothing here.</h3>
    		<p>Unfortunatly, we don't have any news articles for this trust right now.
                If if you know of a news article that you think we should include, please
                <a href="mailto:nhs_news@howsmynhs.co.uk?subject=Article Suggestion">
                contact us now</a>.</p>
    
    	</div>
    </div>
'''

missing_somthing = '''
        <div id="news-missing">
    		<h3>Something Missing?</h3>
    		<p>If there's an article about this NHS Trust you think we should 
            include, <a href="mailto:nhs_news@howsmynhs.co.uk?subject=Article Suggestion">
                contact us now</a>.</p>
    	</div>
'''

if __name__ == "__main__":
    newsFile = "NHS_news_items.ods"
    allNames = np.array(["England", "Bedfordshire Hospitals NHS Foundation Trust", "Cambridge University Hospitals NHS Foundation Trust", "Clacton Hospital", "East And North Hertfordshire NHS Trust", "East Suffolk And North Essex NHS Foundation Trust", "Fryatt Hospital", "Hertfordshire Community NHS Trust", "Herts Urgent Care (Ascots Lane)", "James Paget University Hospitals NHS Foundation Trust", "Mid And South Essex NHS Foundation Trust", "Milton Keynes University Hospital NHS Foundation Trust", "Norfolk And Norwich University Hospitals NHS Foundation Trust", "North West Anglia NHS Foundation Trust", "Putnoe Medical Centre Walk In Centre", "The Princess Alexandra Hospital NHS Trust", "The Queen Elizabeth Hospital, King's Lynn, NHS Foundation Trust", "West Hertfordshire Hospitals NHS Trust", "West Suffolk NHS Foundation Trust", "Barking, Havering And Redbridge University Hospitals NHS Trust", "Barts Health NHS Trust", "Beckenham Beacon Ucc", "Central London Community Healthcare NHS Trust", "Chelsea And Westminster Hospital NHS Foundation Trust", "Croydon Health Services NHS Trust", "Epsom And St Helier University Hospitals NHS Trust", "Guy's And St Thomas' NHS Foundation Trust", "Hhcic East Wic", "Homerton University Hospital NHS Foundation Trust", "Hounslow And Richmond Community Healthcare NHS Trust", "Imperial College Healthcare NHS Trust", "King's College Hospital NHS Foundation Trust", "Kingston Hospital NHS Foundation Trust", "Lewisham And Greenwich NHS Trust", "London North West University Healthcare NHS Trust", "Moorfields Eye Hospital NHS Foundation Trust", "North East London NHS Foundation Trust", "North Middlesex University Hospital NHS Trust", "Royal Brompton & Harefield NHS Foundation Trust", "Royal Free London NHS Foundation Trust", "Royal National Orthopaedic Hospital NHS Trust", "St George's University Hospitals NHS Foundation Trust", "The Hillingdon Hospitals NHS Foundation Trust", "The Pinn Unregistered Wic", "University College London Hospitals NHS Foundation Trust", "Urgent Care Centre (Qms)", "Whittington Health NHS Trust", "Assura Vertis Urgent Care Centres (Birmingham)", "Badger Ltd", "Birmingham Wic", "Birmingham Women's And Children's NHS Foundation Trust", "Chesterfield Royal Hospital NHS Foundation Trust", "Corby Urgent Care Centre", "Coventry And Warwickshire Partnership NHS Trust", "Derbyshire Community Health Services NHS Foundation Trust", "Dhu Health Care C.I.C", "Erdington GP Health & Wellbeing Wic", "George Eliot Hospital NHS Trust", "Kettering General Hospital NHS Foundation Trust", "Latham House Medical Practice", "Lincolnshire Community Health Services NHS Trust", "Llr Ea - The Merlyn Vaz Health & Social Care Centre", "Loughborough Urgent Care Centre", "Market Harborough", "Market Harborough Med.Ctr", "Melton Mowbray", "Northampton General Hospital NHS Trust", "Nottingham Citycare Partnership", "Nottingham University Hospitals NHS Trust", "Oadby", "Oakham", "Oakham Medical Practice", "Sandwell And West Birmingham Hospitals NHS Trust", "Sherwood Forest Hospitals NHS Foundation Trust", "Shrewsbury And Telford Hospital NHS Trust", "Shropshire Community Health NHS Trust", "Sleaford Medical Group", "South Birmingham GP Walk In Centre", "South Warwickshire NHS Foundation Trust", "Summerfield GP Surg & Urgent Care Centre", "The Dudley Group NHS Foundation Trust", "The Robert Jones And Agnes Hunt Orthopaedic Hospital NHS Foundation Trust", "The Royal Wolverhampton NHS Trust", "United Lincolnshire Hospitals NHS Trust", "University Hospitals Birmingham NHS Foundation Trust", "University Hospitals Coventry And Warwickshire NHS Trust", "University Hospitals Of Derby And Burton NHS Foundation Trust", "University Hospitals Of Leicester NHS Trust", "University Hospitals Of North Midlands NHS Trust", "Walsall Healthcare NHS Trust", "Worcestershire Acute Hospitals NHS Trust", "Wye Valley NHS Trust", "Airedale NHS Foundation Trust", "Barnsley Hospital NHS Foundation Trust", "Bradford Teaching Hospitals NHS Foundation Trust", "Bransholme Health Centre", "Calderdale And Huddersfield NHS Foundation Trust", "County Durham And Darlington NHS Foundation Trust", "Doncaster And Bassetlaw Teaching Hospitals NHS Foundation Trust", "East Riding Community Hospital", "Gateshead Health NHS Foundation Trust", "Goole & District Hospital", "Harrogate And District NHS Foundation Trust", "Hull University Teaching Hospitals NHS Trust", "Humber Teaching NHS Foundation Trust", "Leeds Teaching Hospitals NHS Trust", "Local Care Direct", "Mid Yorkshire Hospitals NHS Trust", "North Cumbria Integrated Care NHS Foundation Trust", "North Tees And Hartlepool NHS Foundation Trust", "Northern Lincolnshire And Goole NHS Foundation Trust", "Northumbria Healthcare NHS Foundation Trust", "Park Community Practice", "Sheffield Children's NHS Foundation Trust", "Sheffield Teaching Hospitals NHS Foundation Trust", "South Tees Hospitals NHS Foundation Trust", "South Tyneside And Sunderland NHS Foundation Trust", "South West Yorkshire Partnership NHS Foundation Trust", "St.George's Centre", "The Newcastle Upon Tyne Hospitals NHS Foundation Trust", "The Rotherham NHS Foundation Trust", "The Wilberforce Health Centre", "Workington Health Limited", "York Teaching Hospital NHS Foundation Trust", "Alder Hey Children's NHS Foundation Trust", "Blackpool Teaching Hospitals NHS Foundation Trust", "Bolton NHS Foundation Trust", "Bridgewater Community Healthcare NHS Foundation Trust", "Countess Of Chester Hospital NHS Foundation Trust", "East Cheshire NHS Trust", "East Lancashire Hospitals NHS Trust", "Lancashire Teaching Hospitals NHS Foundation Trust", "Liverpool Heart And Chest Hospital NHS Foundation Trust", "Liverpool University Hospitals NHS Foundation Trust", "Liverpool Women's NHS Foundation Trust", "Manchester University NHS Foundation Trust", "Mersey Care NHS Foundation Trust", "Mid Cheshire Hospitals NHS Foundation Trust", "Miriam Minor Emergency", "North West Boroughs Healthcare NHS Foundation Trust", "Pennine Acute Hospitals NHS Trust", "Rossendale Minor Injuries Unit", "Salford Royal NHS Foundation Trust", "Skelmersdale Walk In Centre", "Southport And Ormskirk Hospital NHS Trust", "St Helens And Knowsley Teaching Hospitals NHS Trust", "Stockport NHS Foundation Trust", "Tameside And Glossop Integrated Care NHS Foundation Trust", "The Christie NHS Foundation Trust", "The Walton Centre NHS Foundation Trust", "University Hospitals Of Morecambe Bay NHS Foundation Trust", "Warrington And Halton Teaching Hospitals NHS Foundation Trust", "Wirral Community Health And Care NHS Foundation Trust", "Wirral University Teaching Hospital NHS Foundation Trust", "Wrightington, Wigan And Leigh NHS Foundation Trust", "Ashford And St Peter's Hospitals NHS Foundation Trust", "Ashford Walk-In-Centre", "Assura Reading Llp", "Berkshire Healthcare NHS Foundation Trust", "Bracknell Urgent Care Centre Wic", "Brighton And Sussex University Hospitals NHS Trust", "Brighton Station Health Centre", "Buckinghamshire Healthcare NHS Trust", "Dartford And Gravesham NHS Trust", "East Berks Primary Care Ooh(Wam)", "East Kent Hospitals University NHS Foundation Trust", "East Sussex Healthcare NHS Trust", "Eastbourne Station Health Centre", "First Community Health And Care Cic", "Frimley Health NHS Foundation Trust", "Hampshire Hospitals NHS Foundation Trust", "Haslemere Minor Injuries Unit", "Hastings Med P & Walkin", "Isle Of Wight NHS Trust", "Kent Community Health NHS Foundation Trust", "Maidstone And Tunbridge Wells NHS Trust", "Medway NHS Foundation Trust", "Oxford Health NHS Foundation Trust", "Oxford University Hospitals NHS Foundation Trust", "Phl Lymington Utc", "Portsmouth Hospitals University National Health Service Trust", "Queen Victoria Hospital NHS Foundation Trust", "Royal Berkshire NHS Foundation Trust", "Royal Surrey County Hospital NHS Foundation Trust", "Southampton NHS Treatment Centre", "Southern Health NHS Foundation Trust", "St Mary's NHS Treatment Centre", "Surrey And Sussex Healthcare NHS Trust", "Sussex Community NHS Foundation Trust", "University Hospital Southampton NHS Foundation Trust", "Western Sussex Hospitals NHS Foundation Trust", "Whitstable Medical Practice", "Woking Walk In Centre", "Cornwall Partnership NHS Foundation Trust", "Dorset County Hospital NHS Foundation Trust", "Dorset Healthcare University NHS Foundation Trust", "Exmouth Minor Injury Unit", "Gloucestershire Health And Care NHS Foundation Trust", "Gloucestershire Hospitals NHS Foundation Trust", "Great Western Hospitals NHS Foundation Trust", "North Bristol NHS Trust", "Northern Devon Healthcare NHS Trust", "Okehampton Medical Centre", "Paulton Memorial Hospital", "Poole Hospital NHS Foundation Trust", "Royal Cornwall Hospitals NHS Trust", "Royal Devon And Exeter NHS Foundation Trust", "Royal United Hospitals Bath NHS Foundation Trust", "Salisbury NHS Foundation Trust", "Sirona Care & Health", "Somerset NHS Foundation Trust", "Tetbury Hospital Trust Ltd", "The Royal Bournemouth And Christchurch Hospitals NHS Foundation Trust", "Torbay And South Devon NHS Foundation Trust", "University Hospitals Bristol And Weston NHS Foundation Trust", "University Hospitals Plymouth NHS Trust", "Wiltshire Health & Care", "Yeovil District Hospital NHS Foundation Trust"], dtype=object)
    newsDict = makeNewsDictionary(allNames,newsFile)
    
    name = allNames[2]
    print(makeNewsBlock(name, newsDict))
        
    