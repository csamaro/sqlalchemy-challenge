# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1>Welcome to Climate App!<br/></h1>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #get precipitation for the last 12 months
    precip = session.query(Measurement.prcp, Measurement.date).filter(Measurement.date >= '2016-08-23').all()
    session.close()
    
    #create dictionary using date and prcp
    prcpdict = {date: prcp for date, prcp in precip}
    return jsonify(prcpdict)

@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #query all stations
    stat_results = session.query(Station.station).all()
    session.close()

    #convert list of tuples into normal list
    all_stations = list(np.ravel(stat_results))
    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #query in the dates & temps for station USC00519281 for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").filter(Measurement.date >= '2016-08-23').all()
    session.close()

    #create dictionary
    res_dict = []
    for dates, temps in results:
        temp_dict = {}
        temp_dict["Date"] = dates
        temp_dict["Temperature"] = temps
        res_dict.append(temp_dict)
    return jsonify(res_dict)

@app.route('/api/v1.0/<start>')
def starter(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #convert start from user to valid date
    start_dt = dt.datetime.strptime(start, "%Y-%m-%d")

    #query min max avg from start date
    agg_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_dt).all()
    session.close()

    #convert to list
    agg_list = list(np.ravel(agg_results))
    return jsonify(agg_list)

@app.route('/api/v1.0/<start>/<end>')
def startend(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #convert start & end from user to valid date
    start_dt = dt.datetime.strptime(start, "%Y-%m-%d")
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    #query min max avg from start date
    agg_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt).all()
    session.close()

    #convert to list
    agg_list = list(np.ravel(agg_results))
    return jsonify(agg_list)


if __name__ == "__main__":
    app.run(debug=True)