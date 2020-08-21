#Import dependencies
from flask import Flask, jsonify

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Create Engine
engine = create_engine("sqlite:///hawaii.sqlite")
session = Session(engine)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

#Identify table names
#Base.classes.keys()

#Save Tables
Measurement = Base.classes.measurement
Station = Base.classes.station

######################FLASK SETUP
#Create an app, pass __name__
app = Flask(__name__)

######################FLASK ROUTES
# Define Home route
@app.route("/")
def Home():
    """All available api routes."""
    return (
    f"Available routes:<br/>"
    f"/<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/&lt;start&gt;<br/>"
    f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    #Query latest date
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #Query one year before the last date
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
                                    .filter(Measurement.date >=year_ago).all()
    session.close()
                                    
#Convert precipitation data into a dictionary and return JSON
    precip = []
    for date, prcp in precipitation_data:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precip.append(prcp_dict)
    return jsonify(precip)
    

#Define stations route, query and return JSON
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.name).group_by(Station.name).all()
    session.close()

    return jsonify(stations)

#Define the tobs route, query the most active station, and return JSON
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobs_data = session.query(Measurement.date,Measurement.tobs)\
    .filter(Measurement.date >= year_ago)\
    .filter(Measurement.station == "USC00519281")\
    .all()
    session.close()

    return jsonify(tobs_data)

#TMIN, TAVG, and TMAX for >=start date
@app.route("/api/v1.0/<start>")
def startdate(start):
    session = Session(engine)
    startdate_query = session.query(func.min(Measurement.tobs),\
    func.avg(Measurement.tobs),\
    func.max(Measurement.tobs))\
    .filter(Measurement.date >= start)\
    .all()
    
    session.close()

    return jsonify(startdate_query)

## TMIN, TAVG, and TMAX for dates between the start and end date inclusive (<= >=)
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    session = Session(engine)
    startend_query = session.query(func.min(Measurement.tobs),\
    func.avg(Measurement.tobs),\
    func.max(Measurement.tobs))\
    .filter(Measurement.date >= start)\
    .filter(Measurement.date<=end)\
    .all()

    session.close()

    return jsonify(startend_query)

if __name__ == "__main__":
    app.run(debug=True)
