## Map builder using plotly (run `-W ignore` since I force lists into cells for years visit visualization renderings.)
import pandas as pd
import plotly.express as px
from fuzzywuzzy import process

def buildDF():
    initialDF = pd.read_csv('countryCodes.csv')
    initialDF['Have Been'] = 0
    initialDF['Year Went'] = 'N/A'

    initialDF['Have Been'][initialDF['Code'] == 'USA'] = 7 ## Infinity value
    initialDF['Year Went'][initialDF['Code'] == 'USA'] = 'Home'

    ''' TODO: this will get replciated in another page we interact with for 
    adding new trips. You'll use datetime for current year:
    from datetime import datetime
    datetime.now().year 
    '''
    ## Add Base Trips 
    initialDF = addTrip(initialDF,'Bahamas', 2006)
    initialDF = addTrip(initialDF,'Mexico', 2007)
    initialDF = addTrip(initialDF,'Jamaica', 2007)
    initialDF = addTrip(initialDF,'Cayman Islands', 2007)
    initialDF = addTrip(initialDF,'Italy', 2009)
    initialDF = addTrip(initialDF,'Vatican', 2009)
    initialDF = addTrip(initialDF,'Greece', 2009)
    initialDF = addTrip(initialDF,'Haiti', 2009)
    initialDF = addTrip(initialDF,'Costa Rica', 2010)
    initialDF = addTrip(initialDF,'France', "Summer of 2010")
    initialDF = addTrip(initialDF,'United Kingdom', 2010)
    initialDF = addTrip(initialDF,'Germany', 2010)
    initialDF = addTrip(initialDF,'Spain', "Study Abroad 2011-2012") ## NOTE: more than one must be a string, or else it tries to do math (i.e., returns -1 in map rather than 2011-2012)
    initialDF = addTrip(initialDF,'France', 2011)
    initialDF = addTrip(initialDF,'Ireland', 2011)
    initialDF = addTrip(initialDF,'Portugal', 2011)
    initialDF = addTrip(initialDF,'Andorra', 2011)
    initialDF = addTrip(initialDF,'Netherlands', 2012)
    initialDF = addTrip(initialDF,'Netherlands', 2012)
    initialDF = addTrip(initialDF,'Mexico', 2013)
    initialDF = addTrip(initialDF,'South Korea', "Worked 2013-2014")
    initialDF = addTrip(initialDF,'Thailand', 2014)
    initialDF = addTrip(initialDF,'Japan', 2014)
    initialDF = addTrip(initialDF,'Japan', 2014) ## NOTE: Yep, 2x same year
    initialDF = addTrip(initialDF,'Israel', 2015)
    initialDF = addTrip(initialDF,'Palestine', 2015)
    initialDF = addTrip(initialDF,'Germany', 2016)
    initialDF = addTrip(initialDF,'Senegal', 2016)
    initialDF = addTrip(initialDF,'Argentina', 2016)
    initialDF = addTrip(initialDF,'Japan', 2017)
    initialDF = addTrip(initialDF,'United Kingdom', 2017)
    initialDF = addTrip(initialDF,'Portugal', 2017)
    initialDF = addTrip(initialDF,'Spain', 2017)
    initialDF = addTrip(initialDF,'South Africa', 2017)
    initialDF = addTrip(initialDF,'China', 2018)
    initialDF = addTrip(initialDF,'Germany', 2018)
    initialDF = addTrip(initialDF,'Egypt', 2018)
    initialDF = addTrip(initialDF,'Jordan', 2018)
    initialDF = addTrip(initialDF,'Italy', 2019)
    initialDF = addTrip(initialDF,'Vatican City', 2019)
    initialDF = addTrip(initialDF,'France', 2019)
    initialDF = addTrip(initialDF,'Vietnam', 2019)
    initialDF = addTrip(initialDF,'Kenya', 2020)

    ## Extend places lived by a few shades
    initialDF['Have Been'][initialDF['Code'] == 'FRA'] += 3 ## Just a summer
    initialDF['Have Been'][initialDF['Code'] == 'KOR'] += 5 ## One full year
    initialDF['Have Been'][initialDF['Code'] == 'ESP'] += 5 ## One full year

    return initialDF


def addTrip(df,country, yearWent):
    ## Do a fuzzy-ish matcher
    dfCountryList = df['Country'].tolist()
    counter = 0
    countryOptions = list()
    for item in dfCountryList:
        if country in item:
            counter += 1
            countryOptions.append(item)
    if counter == 1:
        for item in dfCountryList:
            if country in item:
                indexValue = df[df['Country'] == item].index[0]
                prevItems = df['Year Went'][df['Country'] == item]
                newlist = list()
                for foundItem in prevItems:
                    if foundItem != 'N/A':
                        for superFoundItem in foundItem:
                            newlist.append(superFoundItem)
                newlist.append(yearWent)
                df.at[indexValue, 'Year Went'] = newlist
                df['Have Been'][df['Country'] == item] = len(newlist)
    elif counter == 0:
        print('\n WARNING: EMPLOYING FUZZY MATCH. CHECK THE FOLLOWING RESULT WAS AS INTENDED:')
        highest = process.extractOne(country,dfCountryList)
        print('Currently adding {}, the match to entry {} with a probability of {}.\n'.format(highest[0], country, highest[1]))
        fuzzyCounter = 0
        for item in dfCountryList:
            if highest[0] in item:
                fuzzyCounter += 1
                countryOptions.append(item)
        if fuzzyCounter == 1:
            for item in dfCountryList:
                if highest[0] in item:
                    indexValue = df[df['Country'] == item].index[0]
                    prevItems = df['Year Went'][df['Country'] == item]
                    newlist = list()
                    for foundItem in prevItems:
                        if foundItem != 'N/A':
                            for superFoundItem in foundItem:
                                newlist.append(superFoundItem)
                    newlist.append(yearWent)
                    df.at[indexValue, 'Year Went'] = newlist
                    df['Have Been'][df['Country'] == item] = len(newlist)
        elif fuzzyCounter == 0:
            print('The country ** {} ** was not recognized. Please check spelling and try again. (The closest match was {})'.format(country,highest[0]))
            exit(1)
    else:
        print('Unfortunately more than one country can meet the name given. Please specify between the following: ', *countryOptions, sep='\n- ')
        exit(1)

    return df


##  Render everything
def buildMap():
    initiallyPopulatedDF = buildDF()
    initiallyPopulatedDF.to_csv('initiallyPopulated.csv')
    fig = px.choropleth(initiallyPopulatedDF, locations="Code", color='Have Been', hover_name='Country',hover_data=['Year Went'],color_continuous_scale=px.colors.sequential.Mint) #["green",'yellow','orange',"red"]) #px.colors.sequential.Plasma)
    fig.update_layout(
        title = "Places I've Been",
        ## If I want to disable Automargins
        # width=1500,
        # height=1300,
        font=dict(
            family="Helvetica, monospace",
            size=18,
            color="#7f7f7f")
    )
    fig.show()

buildMap()