import logging
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def writeMetarToInfluxDb2(metar, bucket):
    try:
        client = InfluxDBClient.from_config_file("config.ini")
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("metar") \
            .tag("icao", metar["station"]) \
            .field("temperature", metar["temperatures"]["temperature"]) \
            .field("dewpoint", metar["temperatures"]["dew_point"]) \
            .field("humidity", metar["humidity"]) \
            .field("wind_direction", metar["wind"]["direction"]) \
            .field("wind_speed", metar["wind"]["speed"]) \
            .field("wind_gust", metar["wind"]["gust"]) \
            .field("visibility", metar["visibility"]) \
            .field("weather", metar["weather"]) \
            .field("qnh", metar["QNH"])
        write_api.write(bucket=bucket, org=client.org, record=point)
    except Exception as e:
        logger.error(f"Error writing METAR to InfluxDB: {e}")

def fetchMetar(icao, bucket):
    try:
        client = InfluxDBClient.from_config_file("config.ini")
        query_api = client.query_api()
        
        # Query to get the latest METAR for the specified ICAO
        query = f'''
            from(bucket: "{bucket}")
                |> range(start: -24h)
                |> filter(fn: (r) => r["_measurement"] == "metar")
                |> filter(fn: (r) => r["icao"] == "{icao}")
                |> last()
        '''
        result = query_api.query(query)
        
        if not result:
            return None
            
        # Convert the result to a dictionary
        metar_data = {}
        for table in result:
            for record in table.records:
                field = record.get_field()
                value = record.get_value()
                metar_data[field] = value
                
        return metar_data
        
    except Exception as e:
        logger.error(f"Error querying InfluxDB: {e}")
        return None
    finally:
        client.close()