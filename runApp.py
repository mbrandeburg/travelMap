## How to push example: gp 'added div containers for Heroku' && git push heroku master

import pandas as pd
import os, json, plotly, mapBuilder
from flask import Flask, render_template, request, send_from_directory, redirect, flash, url_for, jsonify
from flask_bootstrap import Bootstrap
from datetime import datetime
from werkzeug.utils import secure_filename
import numpy as np

app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'your-secret-key-change-this'  # Add secret key for flash messages

def calculate_stats(df):
    """Calculate travel statistics from the dataframe"""
    visited_countries = len(df[df['Have Been'] > 0])
    total_trips = df[df['Have Been'] > 0]['Have Been'].sum()
    
    # Calculate years of traveling (from first trip to most recent)
    years_data = []
    for _, row in df.iterrows():
        if row['Have Been'] > 0 and row['Year Went'] != 'N/A':
            year_went = str(row['Year Went'])
            if ',' in year_went:
                # Multiple years
                years_list = year_went.replace('[', '').replace(']', '').replace("'", '').split(', ')
                for year in years_list:
                    try:
                        years_data.append(int(year))
                    except:
                        # Handle non-numeric years like "Study Abroad 2011-2012"
                        pass
            else:
                try:
                    years_data.append(int(year_went))
                except:
                    pass
    
    if years_data:
        years_traveling = max(years_data) - min(years_data) + 1
    else:
        years_traveling = 0
    
    return {
        'countries': visited_countries,
        'trips': int(total_trips),
        'years': years_traveling
    }

## FLASK RENDER THE WEBPAGE:
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            file.save(os.path.join('/mnt', 'Travel Tracker - Main.csv'))
            return redirect(url_for('webFramesUnique'))
    return render_template('upload.html')

@app.route("/")
def webFramesUnique():
    returnedValues = mapBuilder.buildMap()
    fig = returnedValues[0]
    df = returnedValues[1]
    
    # Calculate statistics
    stats = calculate_stats(df)
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', graphJSON=graphJSON, stats=stats)

## favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

## background process for docker image retag and push
@app.route('/background_process', methods=['POST']) #, methods=['GET','POST'])
def test():
    try:
        if request.method == "POST":
            data = request.form.get('data', '').strip()
            data2 = request.form.get('data2', '').strip()
            
            if not data:
                return jsonify({'error': 'Country name is required'}), 400
            
            if len(data2) == 0:
                data2 = datetime.now().year
            else:
                try:
                    data2 = int(data2)
                except ValueError:
                    # Keep as string if it's not a number (e.g., "Study Abroad 2011-2012")
                    pass
            
            # Add the trip
            mapBuilder.addTrip(data, data2)
            return jsonify({'success': True, 'message': f'Added {data} for {data2}'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid request'}), 400


### INITAITE IT VIA FLASK
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
    # app.run() ##Unspecifying for heroku 