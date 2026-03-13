import pandas as pd
import json
import os

# --- CONFIGURATION ---
DATA_DIR = 'data'

# --- CLEANING RULES ---
# 1. Ignore these IDs entirely (The "X" lines)
IGNORE_SUFFIX = 'X' 

# 2. Rename these specific IDs (Internal Code -> Your Display Name)
ID_MAPPING = {
    'GS': 'S',          # 42 St Shuttle -> S
    'H':  'S Beach',    # Rockaway Shuttle -> S Beach
    'SI': 'SIR',        # Staten Island -> SIR
    'FS': 'S Franklin'  # (Optional) Renaming Franklin Shuttle to be clear
}

def build_route_database():
    print("⏳ Loading GTFS files...")
    
    try:
        routes = pd.read_csv(os.path.join(DATA_DIR, 'routes.txt'), dtype=str)
        trips = pd.read_csv(os.path.join(DATA_DIR, 'trips.txt'), dtype=str)
        stop_times = pd.read_csv(os.path.join(DATA_DIR, 'stop_times.txt'), dtype=str)
        stops = pd.read_csv(os.path.join(DATA_DIR, 'stops.txt'), dtype=str)
    except FileNotFoundError as e:
        print(f"❌ Error: {e.filename} not found.")
        return

    print("🔨 Processing data...")

    # 1. Map Stops to Parent Stations
    stop_to_parent = {}
    stop_info = {} 
    
    for _, row in stops.iterrows():
        s_id = row['stop_id']
        p_id = row['parent_station'] if pd.notna(row['parent_station']) else s_id
        name = row['stop_name']
        stop_to_parent[s_id] = p_id
        stop_info[p_id] = name

    # 2. Merge Data
    # Merge Routes -> Trips
    route_trips = pd.merge(trips[['route_id', 'trip_id']], routes[['route_id', 'route_color', 'route_text_color']], on='route_id')
    
    # Merge Stops (Optimized)
    full_chain = pd.merge(route_trips, stop_times[['trip_id', 'stop_id']], on='trip_id')
    
    # 3. Build & Clean the Dictionary
    route_map = {}
    
    print("🧹 Applying cleaning rules...")
    
    # Group by the ORIGINAL route_id first
    for route_id, group in full_chain.groupby('route_id'):
        
        # RULE 1: Skip if it ends in 'X' (e.g., 6X, 7X)
        if route_id.endswith(IGNORE_SUFFIX):
            continue
            
        # RULE 2: Rename specific IDs (GS -> S)
        display_id = ID_MAPPING.get(route_id, route_id)
        
        # Get colors (Default to grey/black if missing)
        color = group.iloc[0]['route_color'] if pd.notna(group.iloc[0]['route_color']) else "999999"
        text_color = group.iloc[0]['route_text_color'] if pd.notna(group.iloc[0]['route_text_color']) else "000000"
        
        # Get unique stations
        raw_stops = group['stop_id'].unique()
        parent_ids = set()
        
        for s in raw_stops:
            if s in stop_to_parent:
                parent_ids.add(stop_to_parent[s])
        
        stations_list = []
        for p_id in parent_ids:
            if p_id in stop_info:
                stations_list.append({'id': p_id, 'name': stop_info[p_id]})
        
        stations_list.sort(key=lambda x: x['name'])
        
        # Save to the map using the NEW display_id
        # Note: This automatically merges data if two IDs map to the same name
        route_map[display_id] = {
            'color': color,
            'text_color': text_color,
            'stations': stations_list
        }

    # 4. Save
    with open('station_database.json', 'w') as f:
        json.dump(route_map, f, indent=4)
        
    print("✅ Success! Database rebuilt with correct Line Names.")

if __name__ == "__main__":
    build_route_database()