from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt


engine = create_engine("sqlite:///C:/Users/railc/OneDrive/Desktop/Bootcamp docs/sqlalchemy-challenge/Module 10 Starter Code/Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)


@app.route("/")
def home():
    """Homepage route"""
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last 12 months"""
    
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)

   
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    
    precip_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations"""
   
    stations = session.query(Station.station, Station.name).all()

    
    station_list = [{"station": station, "name": name} for station, name in stations]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the previous year"""
    
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)

    
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()

    
    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return the minimum, average, and maximum temperatures from the start date to the last date"""
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    
    temp_dict = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "min_temp": temp_data[0][0],
        "avg_temp": temp_data[0][1],
        "max_temp": temp_data[0][2]
    }

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Return the minimum, average, and maximum temperatures for the date range"""
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    
    temp_dict = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "min_temp": temp_data[0][0],
        "avg_temp": temp_data[0][1],
        "max_temp": temp_data[0][2]
    }

    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)


