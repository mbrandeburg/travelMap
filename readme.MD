# Mapping Script for Travel Locations

Fun side-project to make an interactive map of places I've traveled.

*Stretch Goal: Tie into Telegraph API for a chatbot that automatically updates my map, and other interactions.* 

## General Usage

Rather than editing the `initiallyPopulated.csv` file, better to update `mapBuilder.py` with any trips. In fact, *best* to also blow away the `initiallyPopulated.csv` each time you want to add trips overall (unless these trips are added via the web interface).


## Heroku Usage

1. `heroku login`
2. `git push heroku master`