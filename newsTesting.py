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

def makeNewsDictionary(newsFile):
    df = read_ods(newsFile, 1, headers=False)
    everything = df.values[4:,:]
    names = set(everything[:,0])
    names = sanitize_names(names)
    
    news_dict = {}
    
    for name in names:
        news_dict[name] = collectTrustNews(name, everything)
        
    return news_dict
    
    
if __name__ == "__main__":
    newsFile = "NHS_news_items.ods"
    newsDict = makeNewsDictionary(newsFile)
    
    trustsWithNews = list(newsDict.keys())
    
    for item in newsDict[trustsWithNews[0]]:
        print(item, "\n")
    