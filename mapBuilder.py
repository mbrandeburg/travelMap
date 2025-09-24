## Map builder using plotly (run `-W ignore` since I force lists into cells for years visit visualization renderings.)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fuzzywuzzy import process
import os
import numpy as np
import json
from functools import lru_cache

def buildDF():
    initialDF = pd.read_csv('countryCodes.csv')
    initialDF['Have Been'] = 0
    initialDF['Year Went'] = 'N/A'

    # Use loc for pandas 3.0 compatibility
    initialDF.loc[initialDF['Code'] == 'USA', 'Have Been'] = 7  ## Infinity value
    initialDF.loc[initialDF['Code'] == 'USA', 'Year Went'] = 'Home'

    ## Add Base Trips 
    initialDF.to_csv('/mnt/Travel Tracker - Main.csv', index=False)
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
    initialDF = addTrip('Mexico', 2022)
    initialDF = addTrip('Colombia', 2023)
    initialDF = addTrip('Spain', 2023)
    initialDF = addTrip('Spain', 2024)
    initialDF = addTrip('Morocco', 2024)

    ## Extend places lived by a few shades
    initialDF.loc[initialDF['Code'] == 'FRA', 'Have Been'] += 3  ## Just a summer
    initialDF.loc[initialDF['Code'] == 'KOR', 'Have Been'] += 5  ## One full year
    initialDF.loc[initialDF['Code'] == 'ESP', 'Have Been'] += 5  ## One full year

    initialDF.to_csv('/mnt/Travel Tracker - Main.csv', index=False)
    return initialDF

def addTrip(country, yearWent):
    # Clear cache when data changes
    _get_cached_dataframe.cache_clear()
    
    df = pd.read_csv('/mnt/Travel Tracker - Main.csv')
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
                df.loc[df['Country'] == item, 'Have Been'] = len(newlist)
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
                    df.loc[df['Country'] == item, 'Have Been'] = len(newlist)
        elif fuzzyCounter == 0:
            print('The country ** {} ** was not recognized. Please check spelling and try again. (The closest match was {})'.format(country,highest[0]))
            exit(1)
    else:
        print('Unfortunately more than one country can meet the name given. Please specify between the following: ', *countryOptions, sep='\n- ')
        exit(1)

    df.to_csv('/mnt/Travel Tracker - Main.csv', index=False) ## overwrites each time
    return df


##  Render everything
@lru_cache(maxsize=32)
def _get_cached_dataframe():
    """Cache the dataframe to improve performance"""
    try:
        df = pd.read_csv('/mnt/Travel Tracker - Main.csv')
    except:
        # Try to see if its a mnt issue?
        os.system('cp Travel*.csv /mnt/')
        try:
            df = pd.read_csv('/mnt/Travel Tracker - Main.csv')
        except: ## if it doesn't exist yet, then use seeded DF above
            df = buildDF()
    return df

def buildMap():
    df = _get_cached_dataframe().copy()
    df['Year Went'] = df['Year Went'].fillna('N/A')
    
    # Create logarithmic scale for better visibility of countries with few visits
    df['Log Visits'] = np.where(df['Have Been'] > 0, 
                                np.log1p(df['Have Been']), # log1p = log(1 + x) to handle 0 values
                                0)
    
    # Normalize the log scale to 0-10 range for better color mapping
    max_log = df['Log Visits'].max()
    if max_log > 0:
        df['Log Visits Normalized'] = (df['Log Visits'] / max_log) * 10
    else:
        df['Log Visits Normalized'] = df['Log Visits']
    
    # Create custom hover text with better formatting
    df['Hover Text'] = df.apply(lambda row: 
        f"<b>{row['Country']}</b><br>"
        f"Visits: {row['Have Been']}<br>"
        f"Years: {row['Year Went'] if row['Year Went'] != 'N/A' else 'Never visited'}"
        f"<extra></extra>", axis=1)
    
    # Create the choropleth map with improved styling
    fig = go.Figure(data=go.Choropleth(
        locations=df['Code'],
        z=df['Log Visits Normalized'],
        text=df['Country'],
        hovertemplate=df['Hover Text'],
        colorscale=[
            [0.0, 'rgb(247, 247, 247)'],    # Very light gray for unvisited
            [0.1, 'rgb(220, 245, 235)'],    # Very light mint
            [0.3, 'rgb(180, 217, 204)'],    # Light mint
            [0.5, 'rgb(137, 192, 182)'],    # Medium mint
            [0.7, 'rgb(99, 166, 160)'],     # Darker mint
            [0.85, 'rgb(68, 140, 138)'],    # Dark mint
            [1.0, 'rgb(13, 88, 95)']        # Darkest mint
        ],
        colorbar=dict(
            title="Visit Frequency (Log Scale)",
            tickmode="array",
            tickvals=[0, 2, 4, 6, 8, 10],
            ticktext=["Never", "1", "2-3", "4-7", "8-15", "15+"],
            len=0.7,
            thickness=20
        )
    ))
    
    fig.update_layout(
        title={
            'text': "Places I've Been - Interactive Travel Map",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgb(204, 204, 204)",
            projection_type='natural earth'
        ),
        font=dict(
            family="Arial, Helvetica, Ubuntu, sans-serif",
            size=14,
            color="#2c3e50"
        ),
        paper_bgcolor='rgb(248, 249, 250)',
        plot_bgcolor='rgb(248, 249, 250)',
        margin=dict(l=0, r=0, t=50, b=0),
        height=600
    )
    
    return fig, df