# -*- coding: utf-8 -*-
"""
process data
"""

import numpy as np

def combineNames(names1, names2):
    '''Makes a single list of each name appearing in either list'''
    namesOut = names1
    for name in names2:
        if name not in names1:
            namesOut = np.append(namesOut, name)
    return namesOut

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

def makeFigureName(name, fig_type, save_format):
    fig_prefix = '-'.join(name.lower().split(' '))
    fig = ''.join([fig_prefix, "-", fig_type,".", save_format])
    fig = fig.replace(',', '') 
    
    return fig   

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

def get_old_trusts(d):
    old_trusts = np.array([])
    
    for key in d.keys():
        old_trusts = np.concatenate((old_trusts, d[key]))
        
    return old_trusts

def capitaliseFirst(string_list):
    '''Capitalised the first letter of each word in each string in a list
except NHS which should be in all-caps'''
    
    for i, string in enumerate(string_list):
        words = string.lower().split(" ")
        words = [word[0].upper() + word[1:] for word in words]
        string_list[i] = " ".join(words).replace("Nhs", "NHS")
        
    return string_list 

def combineAnEData(allData, allNames, merged_trust, mergered_trusts):
    ''' Combines (adds) the data for given list of trusts. 
        Combined data is only given for dates at which *all*
        listed trusts reported numbers.
    '''
    # initite total and mask
    totalData = np.zeros(len(allData[0,:]), dtype = object)
    
    try:
        newTrustData = allData[allNames == merged_trust][0]
    except:
        raise Exception("Couldn't find merged Trust: {}".format(merged_trust))
    
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

def combineBedData(bedData, allNames, merged_trust, mergered_trusts):
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

def bed_change_per_trust(names, bed_data, mergered_trusts):
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
                trust_beds = combineBedData(bed_data, 
                                            names, 
                                            name,
                                            mergered_trusts)
            
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