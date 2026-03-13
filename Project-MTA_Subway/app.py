from flask import Flask, render_template, redirect, url_for
from google.transit import gtfs_realtime_pb2
import requests
import json
import os
import time
import io
from feed_map import get_feed_url # Import the mapper we just made

app = Flask(__name__)

# --- DATABASE SETUP ---
DB_FILE = 'station_database.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

TRANSIT_DATA = load_db()

# --- HELPER: GET LIVE DATA ---
def get_live_predictions(route_id, station_id):
    """Fetches and parses real-time data for a specific station."""
    url = get_feed_url(route_id)
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print(f"📡 Connecting to {url} for {route_id} @ {station_id}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, "MTA Server Error"

        # Parse the binary data
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        # Lists to store arrival times (in minutes)
        northbound = []
        southbound = []
        mta_time = feed.header.timestamp
        current_time = time.time() # Backup if MTA time is weird

        for entity in feed.entity:
            if entity.HasField('trip_update'):
                for update in entity.trip_update.stop_time_update:
                    if station_id in update.stop_id:
                        # Find arrival time
                        t = update.arrival.time or update.departure.time
                        if t:
                            # Calculate minutes until arrival
                            # Use MTA timestamp for accuracy, fallback to system time
                            ref_time = mta_time if mta_time > 0 else current_time
                            diff_seconds = t - ref_time
                            diff_mins = int(diff_seconds / 60)
                            
                            # Filter: Keep trains 0-60 mins away
                            if diff_mins >= 0 and diff_mins <= 60:
                                # Determine direction based on 'N' or 'S' suffix
                                if update.stop_id.endswith('N'):
                                    northbound.append(diff_mins)
                                elif update.stop_id.endswith('S'):
                                    southbound.append(diff_mins)

        # Sort and take top 3
        northbound = sorted(list(set(northbound)))[:3]
        southbound = sorted(list(set(southbound)))[:3]
        
        return {'N': northbound, 'S': southbound}, None

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None, str(e)


# --- ROUTES ---

@app.route('/')
def menu_routes():
    routes = []
    for r_id, data in TRANSIT_DATA.items():
        routes.append({'id': r_id, 'color': data['color'], 'text_color': data['text_color']})
    routes.sort(key=lambda x: x['id'])
    return render_template('routes.html', routes=routes)

@app.route('/stations/<route_id>')
def menu_stations(route_id):
    if route_id not in TRANSIT_DATA: return redirect(url_for('menu_routes'))
    line_data = TRANSIT_DATA[route_id]
    return render_template('stations.html', route_id=route_id, stations=line_data['stations'], 
                         color=line_data['color'], text_color=line_data['text_color'])

# UPDATED: Now accepts route_id AND station_id
@app.route('/live/<route_id>/<station_id>')
def live_board(route_id, station_id):
    # 1. Get Static Info (Name, Color)
    if route_id not in TRANSIT_DATA: return redirect(url_for('menu_routes'))
    
    # Find station name from our DB
    station_name = station_id # Default
    for s in TRANSIT_DATA[route_id]['stations']:
        if s['id'] == station_id:
            station_name = s['name']
            break
            
    # 2. Get Live Data
    predictions, error = get_live_predictions(route_id, station_id)
    
    return render_template('board.html', 
                         station_name=station_name,
                         route_id=route_id,
                         predictions=predictions,
                         error=error,
                         color=TRANSIT_DATA[route_id]['color'],
                         text_color=TRANSIT_DATA[route_id]['text_color'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)