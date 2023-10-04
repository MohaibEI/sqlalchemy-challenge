# Import the dependencies.



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################




#################################################
# Flask Routes
#################################################


import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the measurement and stations tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes

# Welcome route ("/")
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation - Precipitation data for the last year<br/>"
        "/api/v1.0/stations - List of weather stations<br/>"
        "/api/v1.0/tobs - Temperature observations for the last year<br/>"
        "/api/v1.0/start - Min, Max, and Avg temperatures for a given start date<br/>"
        "/api/v1.0/start/end - Min, Max, and Avg temperatures for a date range"
    )

# Precipitation route ("/api/v1.0/precipitation")
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of dates and precipitation from the last year."""
    # Calculate the date one year from the last date in the dataset
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)

    # Query for the dates and precipitation from the last year
    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .order_by(Measurement.date).all()

    # Convert the query results to a list of dictionaries
    precipitation_data = [{"date": date, "prcp": prcp} for date, prcp in results]

    return jsonify(precipitation_data)

# Stations route ("/api/v1.0/stations")
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of weather stations."""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert the list of tuples into a list of station names
    station_names = [result[0] for result in results]

    return jsonify(station_names)

# Temperature Observations route ("/api/v1.0/tobs")
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observations from the last year."""
    # Get the most active station from the previous query
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year from the last date in the dataset
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)

    # Query temperature observations for the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago)\
        .order_by(Measurement.date).all()

    # Convert the query results to a list of dictionaries
    temperature_data = [{"date": date, "tobs": tobs} for date, tobs in results]

    return jsonify(temperature_data)

# Temperature Statistics route ("/api/v1.0/<start>" and "/api/v1.0/<start>/<end>")
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """Return temperature statistics for a given start date or date range."""
    # Convert start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    if end:
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    else:
        # If end date is not provided, use the latest date in the dataset
        end_date = recent_date

    # Query temperature statistics for the specified date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date)\
        .filter(Measurement.date <= end_date).all()

    # Create a dictionary with the temperature statistics
    temperature_stats = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "min_temperature": results[0][0],
        "avg_temperature": results[0][1],
        "max_temperature": results[0][2]
    }

    return jsonify(temperature_stats)

if __name__ == '__main__':
    app.run()

