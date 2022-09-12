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

    ## Add Base Trips 
    initialDF.to_csv('initiallyPopulated.csv', index=False)
    initialDF = addTrip('Bahamas', 2006)
    initialDF = addTrip('Mexico', 2007)
    initialDF = addTrip('Jamaica', 2007)
    initialDF = addTrip('Cayman Islands', 2007)
    initialDF = addTrip('Italy', 2009)
    initialDF = addTrip('Vatican', 2009)
    initialDF = addTrip('Greece', 2009)
    initialDF = addTrip('Haiti', 2009)
    initialDF = addTrip('Costa Rica', 2010)
    initialDF = addTrip('France', "Summer of 2010")
    initialDF = addTrip('United Kingdom', 2010)
    initialDF = addTrip('Germany', 2010)
    initialDF = addTrip('Spain', "Study Abroad 2011-2012") ## NOTE: more than one must be a string, or else it tries to do math (i.e., returns -1 in map rather than 2011-2012)
    initialDF = addTrip('France', 2011)
    initialDF = addTrip('Ireland', 2011)
    initialDF = addTrip('Portugal', 2011)
    initialDF = addTrip('Andorra', 2011)
    initialDF = addTrip('Netherlands', 2012)
    initialDF = addTrip('Netherlands', 2012)
    initialDF = addTrip('Mexico', 2013)
    initialDF = addTrip('South Korea', "Worked 2013-2014")
    initialDF = addTrip('Thailand', 2014)
    initialDF = addTrip('Japan', 2014)
    initialDF = addTrip('Japan', 2014) ## NOTE: Yep, 2x same year
    initialDF = addTrip('Israel', 2015)
    initialDF = addTrip('Palestine', 2015)
    initialDF = addTrip('Germany', 2016)
    initialDF = addTrip('Senegal', 2016)
    initialDF = addTrip('Argentina', 2016)
    initialDF = addTrip('Japan', 2017)
    initialDF = addTrip('United Kingdom', 2017)
    initialDF = addTrip('Portugal', 2017)
    initialDF = addTrip('Spain', 2017)
    initialDF = addTrip('South Africa', 2017)
    initialDF = addTrip('China', 2018)
    initialDF = addTrip('Germany', 2018)
    initialDF = addTrip('Egypt', 2018)
    initialDF = addTrip('Jordan', 2018)
    initialDF = addTrip('Italy', 2019)
    initialDF = addTrip('Vatican City', 2019)
    initialDF = addTrip('France', 2019)
    initialDF = addTrip('Vietnam', 2019)
    initialDF = addTrip('Hong Kong', 2019)
    initialDF = addTrip('Kenya', 2020)
    initialDF = addTrip('Puerto Rico', 2021)
    initialDF = addTrip('Colombia', 2021)
    initialDF = addTrip('Brazil', 2022)
    initialDF = addTrip('United Kingdom', 2022)
    initialDF = addTrip('Canada', 2022)

    ## Extend places lived by a few shades
    initialDF['Have Been'][initialDF['Code'] == 'FRA'] += 3 ## Just a summer
    initialDF['Have Been'][initialDF['Code'] == 'KOR'] += 5 ## One full year
    initialDF['Have Been'][initialDF['Code'] == 'ESP'] += 5 ## One full year

    initialDF.to_csv('initiallyPopulated.csv', index=False)
    return initialDF

def addTrip(country, yearWent):
    df = pd.read_csv('initiallyPopulated.csv')
    dfCountryList = df['Country'].tolist()
    df['Year Went'] = df['Year Went'].fillna('N/A')
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
                        if ',' in foundItem:
                            newSplit = foundItem.split(',')
                            for foundSplit in newSplit:
                                newlist.append(foundSplit.replace('[','').replace(']','').replace("'",'')) #.replace(" ","")
                        else:
                            newlist.append(foundItem.replace('[','').replace(']','').replace("'",''))
                newlist.append(yearWent)
                # print(newlist, len(newlist))
                df.at[indexValue, 'Year Went'] = newlist
                df['Have Been'][df['Country'] == item] = len(newlist)
    elif counter == 0:
        ## Do a fuzzy-ish matcher
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
                            if ',' in foundItem:
                                newSplit = foundItem.split(',')
                                for foundSplit in newSplit:
                                    newlist.append(foundSplit.replace('[','').replace(']','').replace("'",'')) #.replace(" ","")
                            else:
                                newlist.append(foundItem.replace('[','').replace(']','').replace("'",''))
                    newlist.append(yearWent)
                    df.at[indexValue, 'Year Went'] = newlist
                    df['Have Been'][df['Country'] == item] = len(newlist)
        elif fuzzyCounter == 0:
            print('The country ** {} ** was not recognized. Please check spelling and try again. (The closest match was {})'.format(country,highest[0]))
            exit(1)
    else:
        print('Unfortunately more than one country can meet the name given. Please specify between the following: ', *countryOptions, sep='\n- ')
        exit(1)

    df.to_csv('initiallyPopulated.csv', index=False) ## overwrites each time
    return df


##  Render everything
def buildMap():
    try:
        df = pd.read_csv('initiallyPopulated.csv')
    except: ## if it doesn't exist yet, then use seeded DF above
        df = buildDF()
    df['Year Went'] = df['Year Went'].fillna('N/A')
    fig = px.choropleth(df, locations="Code", color='Have Been', hover_name='Country',hover_data=['Year Went'],color_continuous_scale=px.colors.sequential.Mint) #["green",'yellow','orange',"red"]) #px.colors.sequential.Plasma)
    fig.update_layout(
        title = "Places I've Been",
        coloraxis_showscale=False,
        # # If I want to disable Automargins
        # autosize=False,
        # width=1500,
        # height=450,
        font=dict(
            family="Helvetica, monospace",
            size=18,
            color="#7f7f7f")
    )
    # fig.show()

    return fig, df