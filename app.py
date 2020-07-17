import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """Listed are all api routes."""
    return (
        f"SQLAlchemy API Homepage: Hawaii Climate:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Start session linking DB
    session = Session(engine)

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_results =   session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    # Return the JSONified dictionary.
    prcp_date_api = []

    for date, prcp in precipitation_results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_date_api.append(new_dict)

    session.close()

    return jsonify(prcp_date_api)

@app.route("/api/v1.0/stations")
def stations():
    # Start session linking DB
    session = Session(engine)

    stations = {}

    # Return a JSON list of stations from the dataset
    station_results = session.query(Station.station, Station.name).all()
    for s,name in station_results:
        stations[s] = name

    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Start session linking DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    observation_results = session.query(Measurement.date,  Measurement.tobs).\
                    filter(Measurement.station == "USC00519281").\
                    filter(func.strftime("%Y-%m-%d", Measurement.date) >= '2016-08-23').all()
    
      # Return a JSON list of temperature observations (TOBS) for the previous year.
   
    tobs_date_api = []

    for date, tobs in observation_results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_api.append(new_dict)

    session.close()

    return jsonify(tobs_date_api)



# Return a JSON list of the minimum temperature, 
# the average temperature, and the max temperature for a given start or start-end range.

@app.route("/api/v1.0/<start>")
# When given the start only, calculate TMIN, TAVG, and TMAX 
# for all dates greater than and equal to the start date.

def temp_start(start):
 

    # Start session linking DB
    session = Session(engine)

    start_temp_list = []

    start_results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in start_results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        start_temp_list.append(new_dict)

    session.close()    

    return jsonify(start_temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):
 

    # Start session linking DB
    session = Session(engine)

    start_end_temp_list = []

    start_end_results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start, Measurement.date <= end).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in start_end_results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        start_end_temp_list.append(new_dict)

    session.close()    

    return jsonify(start_end_temp_list)

if __name__ == '__main__':
    app.run(debug=True)
