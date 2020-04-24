#importing 
from flask import Flask
from flask import Flask, jsonify,request, render_template
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import json
import datetime as dt
from datetime import timedelta
import requests
import argparse

#creating engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#base
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

#setting up engine and flask
session = Session(engine)
app = Flask(__name__)

#calculating dates needed for the query
last_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
last_date = last_date[0]
last_date = dt.datetime.strptime(last_date,'%Y-%m-%d')
year = timedelta(days=365)
one_year_ago = last_date - year

session.close()

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Hawaii API! Aloha! <br/>"
        f"  <br/>"
        f"Available Routes:<br/>"
        f" <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date?start_date=YOURDATE<br/>"
        f"/api/v1.0/date?start_date=YOURDATE&end_date=YOURDATE<br/>"
        f" <br/>"
        f"EXAMPLE DATE FORMAT: 2012-06-21<br/>"
        f" <br/>"
        "Enjoy! A hui hou!")
        

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date > one_year_ago).order_by(Measurement.date).all()
    precipitation_list = []
    for prcp_data in precipitation_data:
        prcp_data_dict = {}
        prcp_data_dict["Date"] = prcp_data.date
        prcp_data_dict["Precipitation"] = prcp_data.prcp
        precipitation_list.append(prcp_data_dict)
    return jsonify(precipitation_list)
    session.close()


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Station.name, Station.station).all()
    station_list = []
    for stn in station_data:
        st_dict = {}
        st_dict["Name"] = stn.name
        st_dict["Station"] = stn.station
        station_list.append(st_dict)
    return jsonify(station_list)
    session.close()


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    the_most_active = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    the_station = the_most_active[0]
    station_id = the_station[0]
    tobs_data = session.query(Measurement.date, Measurement.tobs, Measurement.station).filter(Measurement.station == station_id).filter(Measurement.date > one_year_ago).order_by(Measurement.date).all()
    tobs_list = []
    for tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["Date"] = tobs.date
        tobs_dict["Tobs"] = tobs.tobs
        tobs_dict["Station"] = tobs.station
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)
    session.close()


@app.route("/api/v1.0/date")
def date():
    session = Session(engine)
    temp_list =[]
    date_format = "%Y-%m-%d"
    start_date = dt.datetime.strptime(request.args.get('start_date'),date_format)

    results = session.query(Measurement.date, func.avg(Measurement.tobs),func.max(Measurement.tobs), func.min(Measurement.tobs)).filter(Measurement.date >= start_date).group_by(Measurement.date).all()
    for result in results:
        temp_dict ={}
        temp_dict["Date"] = result[0]
        temp_dict["Avg"] = result[1]
        temp_dict["Max"] = result[2]
        temp_dict["Min"] = result[3]
        temp_list.append(temp_dict)
    return jsonify(temp_list)
    session.close()


@app.route("/api/v1.0/date?start_date=YOURDATE&end_date=YOURDATE")
def twodates():
    session = Session(engine)
    temp_list =[]
    date_format = "%Y-%m-%d"
    start_date = dt.datetime.strptime(request.args.get('start_date'),date_format)
    end_date = dt.datetime.strptime(request.args.get('end_date'),date_format)

    results = session.query(Measurement.date, func.avg(Measurement.tobs),func.max(Measurement.tobs), func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
    for result in results:
        temp_dict ={}
        temp_dict["Date"] = result[0]
        temp_dict["Avg"] = result[1]
        temp_dict["Max"] = result[2]
        temp_dict["Min"] = result[3]
        temp_list.append(temp_dict)
    return jsonify(temp_list)
    session.close()
   

if __name__ == "__main__": 
    app.run(debug=True)