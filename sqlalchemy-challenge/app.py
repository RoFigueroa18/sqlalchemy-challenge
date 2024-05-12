# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

Base =automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################

app=Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Welcome to the climate homepage, here you can see a list with all our available api routes."""
    return (
        f"<h1>Welcome to the Climate page!</h1>"
        f"<h2>Available Routes:</h2>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/&lt;start&gt;</li>"
        f"<li>/api/v1.0/&lt;start&gt;/&lt;end&gt;</li>"
        f"</ul>"
    )

    #Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date=session.query(func.max(Measurement.date)).scalar()
    most_recent_date=datetime.strptime(most_recent_date,"%Y-%m-%d")
    one_year_before_date=most_recent_date-timedelta(days=366)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_before_date).all()
    
    session.close()

    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

    #Stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.name,Station.station).all()
    session.close()

    station_list = [{"station_id":station[0],"name":station[1]} for station in results]
    return jsonify(station_list)

#tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_recent_date=session.query(func.max(Measurement.date)).first()
    most_recent_date=datetime.strptime(most_recent_date[0],"%Y-%m-%d")
    one_year_before_date=most_recent_date-timedelta(days=366)

#Using the code previously used in the climate_starter.ipynb

    most_active_stations=session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    station_list=[]

    for station in most_active_stations:
        station_list.append((station[0],station[1]))

    most_active_station_id = station_list[0][0]

    temperatures = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.station == most_active_station_id).all()
    min_temp, max_temp, avg_temp = temperatures[0]

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= one_year_before_date).all()
    session.close()

    tobs_list = {date: tobs for date, tobs in results}
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    start_date=datetime.strptime(start,"%Y-%m-%d")
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()

    if not results:
        return jsonify({"message": "The date provieded as start date is not available in the temperature data"})
    else:
        temps = [{'TMIN': result[0], 'TAVG': result[1], 'TMAX': result[2]} for result in results]
        return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)

    start_date=datetime.strptime(start,"%Y-%m-%d")
    end_date=datetime.strptime(end,"%Y-%m-%d")

    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    if not results:
        return jsonify({"message": "The range date provieded is not available in the temperature data"})
    
    else:
        temps = [{'TMIN': result[0], 'TAVG': result[1], 'TMAX': result[2]} for result in results]
        return jsonify(temps)

if __name__ =="__main__":
    app.run(debug=True)