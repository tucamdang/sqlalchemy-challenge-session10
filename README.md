# SQLAlchemy Homework - Surfs Up! session10

## Step 1 - Climate Analysis and Exploration
#### Precipitation Analysis (in 12 months)
Design a query to retrieve the last 12 months of precipitation data and plot the results. 
The recent date is 2017-08-23 and last 12 months is 2016-08-23 by using: 
``````
last_12months = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
``````
Then plot
![Precipitation](https://user-images.githubusercontent.com/99168697/165026366-ccd95584-085d-4b94-bda5-ab24f699cd18.png)

#### Station Analysis: ( find the most active stations)
Calculate the total number of stations in the dataset.
Which station id has the highest number of observations ? And found (USC00519281) is the most active station.

````
station_query= session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
````

Using the most active station id, calculate the lowest, highest, and average temperature.
Hint: You will need to use a function such as ``func.min``, ``func.max``, ``func.avg``, and ``func.count`` in your queries.

````
most_act_station = station_query[0][0]
active_station= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
    func.avg(Measurement.tobs)).filter(Measurement.station =='USC00519281').all()
````

THEN plot histogram
``temp_12mnth_df.plot.hist(bins=12, figsize=(10,8))``

![StationTemps](https://user-images.githubusercontent.com/99168697/165027069-89441ca9-b8f5-47f2-90c3-f7077f0e2616.png)

## Step 1 - Create Climate App:
Design a Flask API based on the queries that you have just developed.

Create new python file 'app.py' and store all queries + Routes, so we can run  ``http://127.0.0.1:5000/`` link
- Routes:
          /api/v1.0/precipitation
          /api/v1.0/stations
          /api/v1.0/tobs
          /api/v1.0/<start>
          /api/v1.0/<start>/<end>

![image](https://user-images.githubusercontent.com/99168697/165027650-c0897863-9bbf-4070-b32c-1372f4650293.png)
![image](https://user-images.githubusercontent.com/99168697/165027716-0710ddc8-600c-48a5-9ef0-6fbf8c739115.png)

``````
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
``````
## BONUS ANALYSIS:

### Temperature Analysis I: (inside climate_starter.jupyternotebook)
Identify the average temperature in June at all stations across all available years in the dataset. Do the same for December temperature:
``from scipy import stats
stats.ttest_ind(june_tmp_list, dec_tmp_list, equal_var=False)``
  In gereral, It is a statistically significant difference in means (p-value of less than 0.05). Very small value - means of these two populations are significantly different. lower probability that the difference is random.    Reject the null hypothesis. null hypothesis - there is no meaningful difference between the temperature in June and December in Hawaii.

![June vs December Scatter Plot](https://user-images.githubusercontent.com/99168697/165028392-94e4e42d-69fd-4ffa-a8a1-4e312af9d7b4.png)

![june_dec_histogram](https://user-images.githubusercontent.com/99168697/165028401-ecd5e93f-dd63-4a4c-81de-6da5b078e397.png)

### Temperature Analysis II: (separate temp_analysis_bonus_2_starter.jupyternotenook)

#### Trip Avg Temp
We plan to take a trip from August first to August seventh of this year. By using database, we search for this August time.
By using the calc_temps function to calculate the min, avg, and max temperatures for your trip using the matching dates from a previous year (i.e., use "2017-08-01").

![TripTempSummary](https://user-images.githubusercontent.com/99168697/165028756-c743a42a-df06-4b62-838a-4f24332fa6da.png)

#### Daily Rainfall Average
``````
# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's 
# matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation
# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation
sel=[Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
station_Measurment_join=session.query(*sel,func.sum(Measurement.prcp)).\
                       group_by(Measurement.station).\
                       order_by(Measurement.station).\
                       filter(Measurement.date>=start_date).\
                       filter(Measurement.date<=end_date).\
                       filter(Measurement.station==Station.station).all()
                        
rainfall_df = pd.DataFrame(station_Measurment_join, columns=['Station','Name', 'Latitude', 'Longtitude', 'Elevation', 'Total Precipitation'])
rainfall_df
``````
![image](https://user-images.githubusercontent.com/99168697/165028805-70052b74-4a1c-4fcb-8c48-9658dffcba3e.png)

#### Daily Temperature Normals
Use the daily_normals function to calculate the normals for each date string and append the results to a list called normals   
                                                           
``````
# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index
normals_df = pd.DataFrame(normals_list, columns = ['Tmin', 'Tavg', 'Tmax'])
normals_df['Date'] = trip_dates
normals_df = normals_df.set_index('Date')
``````
![Predict temperature Jan 2018](https://user-images.githubusercontent.com/99168697/165029201-2df09cda-9409-423b-8e4f-20e8895fd215.png)

``session.close()``                                                     
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                           
                                                       
