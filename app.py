import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import numpy as np

engine = create_engine("sqlite:///hawaii.sqlite")
session = Session(bind=engine)
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station
conn = engine.connect()

from flask import Flask, jsonify
import datetime as dt

app = Flask(__name__)

# Home page. List all routes that are available

@app.route("/")
def homepage():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value. Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    recentdate = dt.date(2017, 8 ,23)
    year_ago = recentdate - dt.timedelta(days=365)

    past_temp = (session.query(Measurement.date, Measurement.prcp)
                .filter(Measurement.date <= recentdate)
                .filter(Measurement.date >= year_ago)
                .order_by(Measurement.date).all())

    session.close()
    
    precip = {date: prcp for date, prcp in past_temp}
    
    return jsonify(precip)

# Return a JSON list of stations from the dataset.

@app.route('/api/v1.0/stations')
def stations():

    stations_all = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(stations_all))
    return jsonify(stations=stations)

# Query the dates and temperature observations of the most active station for the last year of data. Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route('/api/v1.0/tobs') 
def tobs():  
    recentdate = dt.date(2017, 8 ,23)
    year_ago = recentdate - dt.timedelta(days=365)

    lastyear = (session.query(Measurement.tobs)
                .filter(Measurement.station == 'USC00519281')
                .filter(Measurement.date <= recentdate)
                .filter(Measurement.date >= year_ago)
                .order_by(Measurement.tobs).all())
    session.close()
    newtobs = list(np.ravel(lastyear))
    return jsonify(newtobs=newtobs)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route('/api/v1.0/<start>') 
def start(start=None):

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)


@app.route('/api/v1.0/<start>/<end>') 
def startend(start=None, end=None):

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()
    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
