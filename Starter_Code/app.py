# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"   
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    beginning = dt.datetime(2016,8,23).date()
    precip_data = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=beginning)
    precip_all = []
    for date,prcp in precip_data:
        precip = {}
        precip['Date'] = date
        precip['Precipitation'] = prcp
        precip_all.append(precip)
    return jsonify(precip_all)

@app.route('/api/v1.0/stations')
def stations():
    station_q = session.query(Station.station)
    station_list = []
    for item in station_q:
        station_list.append(tuple(item))
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    beginning = dt.datetime(2016,8,23).date()
    active_station = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= beginning).filter(Measurement.station == 'USC00519281').all()
    observed = []
    for date, t_obs in active_station:
        obs = {}
        obs['Date'] = date
        obs['Temperature'] = t_obs
        observed.append(obs)
    return jsonify(observed)
@app.route('/api/v1.0/<start>')
def start_temp(start):
    # adding in the date from string line fixes errors that arise when the month or day is not followed by a leading zero, resulting in null data or the year being the only part of the date read 
    summary = session.query(text('min(measurement.tobs)'),text('max(measurement.tobs) as Max'),text('avg(measurement.tobs) as Mean')).filter(
        Measurement.date >= dt.datetime.strptime(start,'%Y-%m-%d').date()).all()
    sum_dict = {'Minimum Temperature':f'{summary[0][0]} F','Maxmimum Temperature':f'{summary[0][1]} F','Average Temperature':f'{round(summary[0][2],2)} F'}
    return jsonify(sum_dict)

@app.route('/api/v1.0/<start>/<end>')
def start_end_temp(start,end):
    summary_range = session.query(text('min(measurement.tobs)'),text('max(measurement.tobs) as Max'),text('avg(measurement.tobs) as Mean')).filter(
        Measurement.date >= dt.datetime.strptime(start,'%Y-%m-%d').date()).filter(Measurement.date <=dt.datetime.strptime(end,'%Y-%m-%d').date()).all()
    sum_dict_range = {'Minimum Temperature':f'{summary_range[0][0]} F','Maxmimum Temperature':f'{summary_range[0][1]} F','Average Temperature':f'{round(summary_range[0][2],2)} F'}
    return jsonify(sum_dict_range)

if __name__ == '__main__':
    app.run(debug=True)
