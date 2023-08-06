#import flask
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

#create the app
app = Flask(__name__)


#define homepage
@app.route("/")
def hommepage():
    return (f"This app returns weather analysis about Honolulu, Hawaii<br/>"
            f"/api/v1.0/precipitation returns a JSON list of the lastest 12 months of precipitation data.<br/>"
            f"/api/v1.0/stations returns a JSON list of stations and their information.<br/>"
            f"/api/v1.0/tobs returns a JSON list of temperature observations for the most recent 12 months of data.<br/>"
            f"/api/v1.0/start-date and /api/v1.0/start-date/end-date return a JSON list of the min, avg and max temperature for a specific start or start-end range."
    )

#define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #open session
    session = Session(engine)

    #query for precipitation data for the last 12 months
    prev_12_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime(Measurement.date) >= "2016-08-23").all()
    
    #close session
    session.close()
    
    #unzip query results into json friendly list of dicts
    prcp_results = []
    for date, prcp in prev_12_prcp:
        prcp_results_dict = {}
        prcp_results_dict[date] = prcp
        prcp_results.append(prcp_results_dict)

    #jsonify results and return
    return jsonify(prcp_results)

#defire stations route
@app.route("/api/v1.0/stations")
def stations():
    #open session
    session = Session(engine)

    #query to return entire station table
    stations_query = session.query(Station).all()

    #close session
    session.close()

    #unzip query results into json friendly list of dicts
    stations_list = []  
    for station in stations_query:
        stations_dict = {}
        stations_dict['id'] = station.id
        stations_dict['station'] = station.station
        stations_dict['name'] = station.name
        stations_dict['latitude'] = station.latitude
        stations_dict['longitude'] = station.longitude
        stations_dict['elevation'] = station.elevation
        stations_list.append(stations_dict)

    #jsonify results and return 
    return jsonify(stations_list)

#define temperature route
@app.route("/api/v1.0/tobs")
def tobs():
    #open session
    session = Session(engine)

    #query to return the stations in order of most active
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    #assign most active station to a variable
    most_active_station = station_activity[0][0]

    #query the tobs data from the most active station from the most recent 12 months of data
    most_active_12 = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(func.strftime(Measurement.date) >= "2016-08-23").all()

    #close session
    session.close()

    #unzip query return into json friendly list
    tobs_list = list(np.ravel(most_active_12))

    #return jsonified info
    return jsonify(tobs_list)

#define stats route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start, end = "2017-08-23"):

    #open session
    session = Session(engine)

    #query the required stats from the measurement table based on the date range selected
    range_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((func.strftime(Measurement.date) >= func.strftime(start)) & (func.strftime(Measurement.date) <= func.strftime(end))).\
        all()

    #close session
    session.close()

    #unzip query results into json friendly list of dicts
    range_list = []
    for tmin, tavg, tmax in range_results:
        range_dict = {}
        range_dict['Minimum Temperature'] = tmin
        range_dict['Average Temperature'] = tavg
        range_dict['Maximum Temperature'] = tmax
        range_list.append(range_dict)

    #return jsonified stats
    return jsonify(range_list)


#run in debugging mode
if __name__ == '__main__':
    app.run(debug=True)
