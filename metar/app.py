import metar_parser as mp
import metar_crawler as mc
import logging
import json
from datetime import datetime
import TimeSeriesRepository as tsr
import schedule
import threading
import time
from flask import Flask, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration handling
class Config:
    FLASK_PORT = 5000
    FLASK_HOST = '0.0.0.0'
    SCHEDULER_INTERVALS = ['21', '51']  # Minutes past the hour

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def process(event):
    try:
        icao = event["icao"]
        logger.info(f"Fetch METAR for airport: {icao}")
        metar = mc.fetchMETAR(event["icao"])
        logger.info(f"Process METAR: {metar}")
        weather = mp.parseMETAR(metar)
        logger.info(f"METAR transformed weather: {weather}")
        return json.loads(json.dumps(weather, cls=DateTimeEncoder))
    except Exception as e:
        logger.error(f"Error processing METAR for airport: {icao}")
        logger.error(e)
        return None

def processMetar():
    metar = process({"icao": "LOWW"})
    logger.info(metar)
    if metar is not None:
        tsr.writeMetarToInfluxDb2(metar, "metar")

def scheduled_job():
    processMetar()

def run_scheduler():
    """Function to run the scheduler in a separate thread"""
    logger.info("Starting scheduler thread")
    
    # Schedule jobs for :21 and :51 of every hour
    schedule.every(1).minutes.do(scheduled_job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    
# Graceful shutdown handling
def shutdown_handler():
    logger.info("Shutting down application...")
    # Add any cleanup code here
    
# Enhanced scheduler with error recovery
def run_scheduler_with_recovery():
    while True:
        try:
            run_scheduler()
        except Exception as e:
            logger.error(f"Scheduler crashed: {e}")
            logger.info("Restarting scheduler in 60 seconds...")
            time.sleep(60)

@app.route('/v1/api/metar/airports', methods=['GET'])
def fetchAirports():
    response = make_response([
        {
            "icao": "LOWW",
            "name": "Vienna"
        }
    ])

    # Add CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')

    return response

# serve a REST endpoint to provide the metar data for a airport from the influxdb
@app.route('/v1/api/metar/airports/weather/<icao>', methods=['GET'])
def fetchMetar(icao):
    metar = tsr.fetchMetar(icao, "metar")
    response = None
    if metar is not None:
        response = make_response(jsonify(metar))
    else:
        response = make_response(jsonify({"error": "METAR not found"}), 404)
    
    # Add CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')

    return response
    
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'scheduler_running': any(thread.name == 'scheduler' 
                               for thread in threading.enumerate()),
        'timestamp': datetime.now().isoformat()
    })

# Error handler for 404 errors
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

# Error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Enhanced Flask startup
def start_flask_with_config():
    app.config.from_object(Config)
    app.run(
        host=app.config['FLASK_HOST'],
        port=app.config['FLASK_PORT'],
        use_reloader=False  # Important when using threads
    )

if __name__ == '__main__':
    try:
        # Create and start the scheduler thread
        scheduler_thread = threading.Thread(target=run_scheduler_with_recovery)
        scheduler_thread.daemon = True  # This ensures the thread will shut down when the main program exits
        scheduler_thread.start()
        
        # Start Flask in the main thread
        start_flask_with_config()
        
    except KeyboardInterrupt:
        logger.info("Shutting down application...")
    except Exception as e:
        logger.error(f"Application error: {e}")

