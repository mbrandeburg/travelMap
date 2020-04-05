## Map builder using plotly
import pandas as pd
import plotly.express as px

def buildDF():
    initialDF = pd.read_csv('countryCodes.csv')
    initialDF['Have Been'] = 0
    initialDF['Year Went'] = 'N/A'

    initialDF['Have Been'][initialDF['Code'] == 'USA'] = 5 ## Infinity value
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
    initialDF = addTrip(initialDF,'Vatican City', 2009)
    initialDF = addTrip(initialDF,'Greece', 2009)

    initialDF = addTrip(initialDF,'Mexico', 2013)

    initialDF = addTrip(initialDF,'Italy', 2016)
    initialDF = addTrip(initialDF,'Vatican City', 2016)

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
    else:
        print('Unfortunately more than one country can meet the name given. Please specify between the following: ', *countryOptions, sep='\n- ')

    return df


def buildMap():
    initiallyPopulatedDF = buildDF()
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