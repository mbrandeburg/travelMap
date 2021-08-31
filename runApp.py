## How to push example: gp 'added div containers for Heroku' && git push heroku master

import pandas as pd
import os, json, plotly, mapBuilder
from flask import Flask, render_template, request, send_from_directory, redirect
from flask_bootstrap import Bootstrap
from datetime import datetime
app = Flask(__name__)
Bootstrap(app)

## FLASK RENDER THE WEBPAGE:
@app.route("/")
def webFramesUnique():
    returnedValues = mapBuilder.buildMap()
    fig = returnedValues[0]
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', graphJSON=graphJSON)

## favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

## background process for docker image retag and push
@app.route('/background_process', methods=['POST']) #, methods=['GET','POST'])
def test():
    if request.method == "POST":
        data=request.form['data']
        data2=request.form['data2']
        if len(data2) == 0:
            data2 = datetime.now().year
        else:
            data2 = int(data2)
        # print(data, data2, type(data), type(data2))
        mapBuilder.addTrip(data,data2)
    return "Hello World" ## nothing, just to silence errors and will appear if you hit the route via browser


### INITAITE IT VIA FLASK
if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5001)
    app.run() ##Unspecifying for heroku 