#import dependencies
from flask import Flask
from flask.json import jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from sqlalchemy import desc
import datetime as dt
from statistics import mean
#create engine
engine = create_engine("sqlite:///hawaii.sqlite")
#reflect into new model
Base = automap_base()
Base.prepare(engine,reflect=True)
Measure = Base.classes.measurement
Station = Base.classes.station
#set up Flask
app = Flask(__name__)
#set up routes
@app.route("/")
def home():
    return(
        f"Welcome!<br/>"
        f"Available Routes<br/>"
        f"/api/v1.0/precipitation (returns a dictionary of date/precipitation) <br/>"
        f"/api/v1.0/stations (returns a list of all stations by ID) <br/>"
        f"/api/v1.0/2016-5-30/ (returns minimum, average and max temperatures recorded AFTER 2016-05-30) <br/>"
        f"/api/v1.0/2016-5-30/2017-6-22 (returns minimum, average and max temperatures BETWEEN 2016-05-30 and 2017-06-22"
        )


#Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    my_query = session.query(Measure.date, Measure.prcp).all()
    session.close()
    all_date_prcp = []
    for date, prcp in my_query:
        query_dict = {}
        query_dict["date"] = date
        query_dict["prcp"] = prcp
        all_date_prcp.append(query_dict)
#* Return the JSON representation of your dictionary.
    return jsonify(all_date_prcp)


#* Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stationslist():
    session = Session(engine)
    station_query = session.query(Station.station).all()
    session.close()
    stationlist =  []
    for s in station_query:
        stationlist.append(s)
#return json
    return jsonify(stationlist)

#* Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    prevyear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session = Session(engine)
    tobsquery = session.query(Measure.date, Measure.tobs).\
    filter(Measure.date >= prevyear).\
    filter(Measure.station == 'USC00519281').\
    order_by(desc(Measure.date)).all()
    session.close()
    tobslist = []
    session.close()
#* Return a JSON list of temperature observations (TOBS) for the previous year.
    for t in tobsquery:
        tobslist.append(t)
    return jsonify(tobslist)
#* Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>/")
def temp_calc_start(start):
    startdate = start.replace(" ", " ") 
    session = Session(engine)
    select = [func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)]
    temp_stats = session.query(*select).\
    filter(Measure.date >= startdate).all()
    session.close()
    print()
    print(f"Lowest, average and highest temperatures for dates after {startdate}")
    print(temp_stats)
    return jsonify(temp_stats)
#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temp_calc_start_range(start, end):
    startdate = start.replace(" ", " ") 
    enddate = end.replace(" ", " ")
    session = Session(engine)
    select = [func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)]
    range_temp_stats = session.query(*select).\
    filter(Measure.date >= startdate).filter(Measure.date <= enddate).all()
    session.close()
    return jsonify(range_temp_stats)


if __name__ == "__main__":
    app.run(debug=True)
