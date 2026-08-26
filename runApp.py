"""Flask entry point for the travel map app."""
import os
import re
import json
from datetime import datetime

import plotly
from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    redirect,
    flash,
    url_for,
    jsonify,
)
from flask_bootstrap import Bootstrap
import pandas as pd

import config
import mapBuilder

app = Flask(__name__)
Bootstrap(app)
app.secret_key = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_BYTES


def calculate_stats(df):
    """Travel statistics derived from parsed trip labels (USA/home excluded)."""
    travel = df[df["Code"] != "USA"]
    countries = 0
    trips = 0
    years = []
    for _, row in travel.iterrows():
        labels = mapBuilder.parse_years(row["Year Went"])
        if labels:
            countries += 1
            trips += len(labels)
            for label in labels:
                years.extend(int(y) for y in re.findall(r"\d{4}", str(label)))
    years_traveling = (max(years) - min(years) + 1) if years else 0
    return {"countries": countries, "trips": trips, "years": years_traveling}


def _is_valid_tracker(path):
    """A tracker upload must parse as CSV and contain the required columns."""
    try:
        sample = pd.read_csv(path, nrows=5)
    except Exception:
        return False
    return set(config.REQUIRED_COLUMNS).issubset(sample.columns)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files.get("file")
        if file is None or file.filename == "":
            flash("No file selected.")
            return redirect(request.url)
        if not file.filename.lower().endswith(".csv"):
            flash("Please upload a .csv file.")
            return redirect(request.url)

        # Save to a temp file, validate, then atomically swap into place.
        config.DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = config.DATA_PATH.with_name(config.DATA_PATH.name + ".upload.tmp")
        file.save(tmp)
        if not _is_valid_tracker(tmp):
            tmp.unlink(missing_ok=True)
            flash("That CSV is missing required columns: " + ", ".join(config.REQUIRED_COLUMNS))
            return redirect(request.url)
        os.replace(tmp, config.DATA_PATH)
        mapBuilder.invalidate_cache()
        return redirect(url_for("webFramesUnique"))
    return render_template(
        "upload.html",
        required_columns=", ".join(config.REQUIRED_COLUMNS),
        max_mb=config.MAX_UPLOAD_BYTES // (1024 * 1024),
    )


@app.route("/")
def webFramesUnique():
    fig, df = mapBuilder.buildMap()
    stats = calculate_stats(df)
    visited = mapBuilder.visited_rows(df)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("index.html", graphJSON=graphJSON, stats=stats, visited=visited)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/background_process", methods=["POST"])
def background_process():
    country = request.form.get("data", "").strip()
    year = request.form.get("data2", "").strip()
    if not country:
        return jsonify({"error": "Country name is required"}), 400

    if not year:
        year = datetime.now().year
    else:
        try:
            year = int(year)
        except ValueError:
            pass  # keep as a label, e.g. "Study Abroad 2011-2012"

    try:
        mapBuilder.addTrip(country, year)
    except mapBuilder.AmbiguousCountryError as exc:
        return jsonify({"error": str(exc), "options": exc.options}), 400
    except mapBuilder.CountryNotFoundError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:  # noqa: BLE001 - last resort, don't leak internals
        app.logger.exception("addTrip failed")
        return jsonify({"error": "Could not add trip."}), 500

    return jsonify({"success": True, "message": f"Added {country} ({year})"})


@app.errorhandler(413)
def upload_too_large(_error):
    flash(f"File too large (limit {config.MAX_UPLOAD_BYTES // (1024 * 1024)} MB).")
    return redirect(url_for("upload_file"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
