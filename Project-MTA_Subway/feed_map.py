# Maps Route IDs to their specific MTA Real-Time Feed URL
BASE_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2F"

FEED_URLS = {
    # The Numbered Lines (1, 2, 3, 4, 5, 6, S-42St)
    '1': BASE_URL + "gtfs", '2': BASE_URL + "gtfs", '3': BASE_URL + "gtfs",
    '4': BASE_URL + "gtfs", '5': BASE_URL + "gtfs", '6': BASE_URL + "gtfs", 'S': BASE_URL + "gtfs",
    
    # The Blue Lines (A, C, E, H-Rockaway, S-Rockaway)
    'A': BASE_URL + "gtfs-ace", 'C': BASE_URL + "gtfs-ace", 'E': BASE_URL + "gtfs-ace",
    'H': BASE_URL + "gtfs-ace", 'S Beach': BASE_URL + "gtfs-ace",
    
    # The Orange Lines (B, D, F, M)
    'B': BASE_URL + "gtfs-bdfm", 'D': BASE_URL + "gtfs-bdfm", 
    'F': BASE_URL + "gtfs-bdfm", 'M': BASE_URL + "gtfs-bdfm",
    
    # The Yellow Lines (N, Q, R, W)
    'N': BASE_URL + "gtfs-nqrw", 'Q': BASE_URL + "gtfs-nqrw", 
    'R': BASE_URL + "gtfs-nqrw", 'W': BASE_URL + "gtfs-nqrw",
    
    # The Shuttles & Individuals
    'L': BASE_URL + "gtfs-l",
    'G': BASE_URL + "gtfs-g",
    'J': BASE_URL + "gtfs-jz", 'Z': BASE_URL + "gtfs-jz",
    '7': BASE_URL + "gtfs-7",
    'SIR': BASE_URL + "gtfs-si"
}

def get_feed_url(route_id):
    """Returns the correct URL for a given train line."""
    return FEED_URLS.get(route_id, BASE_URL + "gtfs") # Default to numbered if unknown