# 1. import flask
from flask import Flask, jsonify

#set up sqlalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#set up numpy
import numpy as np

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#create base and reflect tables
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

#assign tables to classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# create the app
app = Flask(__name__)


# define homepage
@app.route("/")
def hommepage():
    return (f"This app returns weather analysis about Honolulu, Hawaii<br/>"
            f"/api/v1.0/precipitation returns <br/>"
            f"/api/v1.0/stations returns a JSON list of stations.<br/>"
            f"/api/v1.0/tobs returns a JSON list of temperature observations for the last 12 months of data.<br/>"
            f"/api/v1.0/start-date and /api/v1.0/start-date/end-date return a JSON list of the min, avg and max temperature for a specific start or start-end range."
    )

#define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    prev_12_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime(Measurement.date) >= "2016-08-23").all()
    
    session.close()
    
    prcp_results = []
    for date, prcp in prev_12_prcp:
        prcp_results_dict = {}
        prcp_results_dict[date] = prcp
        prcp_results.append(prcp_results_dict)

    return jsonify(prcp_results)

#defire stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations_query = session.query(Station).all()

    session.close()

    stations_list = list(np.ravel(stations_query))

    return jsonify(stations_list)

#define temperature route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    most_active_station = station_activity[0][0]

    most_active_12 = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(func.strftime(Measurement.date) >= "2016-08-23").all()

    session.close()

    tobs_list = list(np.ravel(most_active_12))

    return jsonify(tobs_list)

#define stats route
@app.route("/api/v1.0/<start>/<end>")
def stats(start, end = "2016-08-23"):
    session = Session(engine)

    range_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((func.strftime(Measurement.date) >= func.strftime(start)) & (func.strftime(Measurement.date) <= func.strftime(end))).\
        all()

    session.close()

    range_list = []
    for tmin, tavg, tmax in prev_12_prcp:
        range_dict = {}
        range_dict['Minimum Temperature'] = tmin
        range_dict['Average Temperature'] = tavg
        range_dict['Maximum Temperature'] = tmax
        range_list.append(range_dict)

    return jsonify(range_list)


if __name__ == '__main__':
    app.run(debug=True)
