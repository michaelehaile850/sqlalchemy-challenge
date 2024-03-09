# Import the dependencies.
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import io
from flask import Flask, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite") # create an engine to connect to database
metadata = MetaData() #reflect the database schema into  new model
metadata.reflect(bind=engine) #



# Create an engine to connect to the existing database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database tables into Python classes
Base = automap_base()

# Reflect the database schema into Python classes
Base.prepare(engine, reflect=True)

# reflect the tables
for table_name,table in metadata.tables.items():
    print(f"Table Name : {table_name}")
    print(f"Columns : {table.columns.keys()}" )
    print()

# Save references to each table
tables = {}
# Access the reflected tables in dict
for table_name in metadata.tables:
    tables[table_name] = metadata.tables[table_name]
      

# Create our session (link) from Python to the DB


engine = create_engine('sqlite:///Resources/hawaii.sqlite')# create an engine to connect to db

Session = sessionmaker(bind=engine) # create sessionmaker object

session = Session() #create a session

session.close() # close the session
#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify
app = Flask(__name__)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer,String,Float,Date,ForeignKey
Base = declarative_base()

Base = declarative_base()

class Measurement(Base):
    __tablename__ = 'measurement'
    id = Column(Integer, primary_key=True)
    station_id = Column(String, ForeignKey('station.station'))
    date = Column(Date)
    prcp = Column(Float)
    tobs = Column(Float)
    station = relationship("Station", backref="measurements")  # Use a different backref name

class Station(Base):
    __tablename__ = 'station'
    station = Column(String, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)



#################################################
# Flask Routes
#################################################

    
import sqlite3
from flask import Flask, jsonify,request
import pandas as pd
from sqlalchemy import create_engine , func,text
from datetime import datetime, timedelta
   


app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


@app.route("/")
def welcome():
    """List all available routes."""
    return (
        "Welcome to the Climate App API!<br/><br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start_date<br/>"
        "/api/v1.0/start_date/end_date<br/>"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    query = """
            SELECT date, prcp
            FROM measurement
            WHERE date >= (SELECT DATE(MAX(date), '-1 year') FROM measurement)
            """
    
    # Execute the query and load the results into a Pandas DataFrame
    df = pd.read_sql_query(query, engine)
    
    # Sort the dataframe by date
    df_sorted = df.sort_values(by='date')
    
    # Convert DataFrame to a dictionary, date as the key and prcp as the value
    precipitation_data = dict(zip(df_sorted.date, df_sorted.prcp))   
    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    """Return the list of weather stations"""
    # SQL query to select station details
    query = """
            SELECT station, name
            FROM station
            """
    
    # Execute the query and load the results into a Pandas DataFrame
    df = pd.read_sql_query(query, engine)
    
    # Convert DataFrame to a list of dictionaries (one per row)
    stations_list = df.to_dict(orient='records')
    
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (TOBS) for the last year"""
    # First, find the most recent date in the database
    recent_date_query = "SELECT MAX(date) FROM measurement"
    recent_date_result = engine.execute(recent_date_query).fetchone()
    recent_date = recent_date_result[0] if recent_date_result else None

    # Calculate the date one year from the last date in the dataset
    if recent_date:
        last_year_date = datetime.strptime(recent_date, "%Y-%m-%d") - timedelta(days=365)
    else:
        return jsonify({"error": "No data found in the database."}), 404

    # Now, query for TOBS data from the last year
    tobs_query = f"""
        SELECT date, tobs
        FROM measurement
        WHERE date >= '{last_year_date.strftime("%Y-%m-%d")}'
        """
    
    # Execute the query and load the results into a Pandas DataFrame
    df_tobs = pd.read_sql_query(tobs_query, engine)

    # Convert DataFrame to a list of dictionaries
    tobs_list = df_tobs.to_dict(orient='records')

    return jsonify(tobs_list)



@app.route("/api/v1.0/<start_date>")
def get_data_from_start(start_date):
    session = Session()
    # Retrieve the maximum date from the database to use as the end date
    end_date = session.query(func.max(Measurement.date)).scalar()

    # Ensure there's an end date
    if not end_date:
        return jsonify({"error": "Could not find the maximum date in the database."}), 404

    # Query for data from start_date to the most recent data (end_date)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()

    # Convert the query results to a list of dictionaries
    data_list = [{"date": str(result.date), "temperature": result.tobs} for result in results]

    return jsonify(data_list)



@app.route("/api/v1.0/<start_date>/<end_date>")
def get_data_range(start_date, end_date):
    session = Session()
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()

    # Convert the query results to a list of dictionaries
    data_list = [{"date": str(result.date), "temperature": result.tobs} for result in results]

    return jsonify(data_list)



if __name__ == '__main__':
    
    app.run(debug=True)








