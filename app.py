import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from Python to the DB
session = Session(engine)


# last 12 months variable
# last_twelve_months = '2016-08-23'
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
last_12months = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Close the session
session.close()

#################################################
# Set up Flask and landing page
#################################################
app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"<p>Welcome to the Hawaii weather API!</p>"
#         f"<p>Usage:</p>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

# /api/v1.0/precipitation
# Query for the dates and temperature observations from the last year.
# Convert the query results to a Dictionary using date as the key and tobs as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Date 12 months ago
#     p_results = session.query(Measurement.date, func.avg(Measurement.prcp)).filter(Measurement.date >= last_twelve_months).group_by(Measurement.date).all()
    session = Session(engine)
        
    prcp_query=session.query(Measurement.date, func.avg(Measurement.prcp)).\
    filter(Measurement.date>= last_12months).group_by(Measurement.date).all()
    
    session.close()
    
    # Convert query results to dictionary
    date_list = []
    prcp_list = []

    for line in prcp_query:
        date_list.append(line[0])
        prcp_list.append(line[1])
    precipitation_dict = dict(zip(date_list,prcp_list))
    
    #return jsonify(prcp_query)
    return jsonify(precipitation_dict)
##=======================================================================

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    station_query = session.query(Station.station, Station.name).all()
    
    session.close()
    
    return jsonify(station_query)
    
##=======================================================================

# /api/v1.0/tobs
# Return a JSON list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    temp_12mnth = session.query(Measurement.station, Measurement.tobs).\
    filter(Measurement.date>=last_12months).\
    filter(Measurement.station =='USC00519281').all()
    session.close()
    
    return jsonify(temp_12mnth)

##=======================================================================

# /api/v1.0/<start>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def startDateOnly(start):
    session = Session(engine)
        
    active_station= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station =='USC00519281').all()
    
    session.close()
    return jsonify(active_station)

##=======================================================================

# /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    session = Session(engine)
    
    start_end_tobs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()    
    
    return jsonify(start_end_tobs)
        
if __name__ == "__main__":
    app.run(debug=True)