import asf_search as asf
import os
import sys
import argparse
from shapely.geometry import shape
import json
from datetime import datetime
import requests # Import the requests library
import zipfile # Moved import to the top

def main():
    parser = argparse.ArgumentParser(
        description="Search and download Sentinel-1 SLC data from ASF."
    )
    parser.add_argument("aoi_geojson", help="Path to the AOI GeoJSON file.")
    parser.add_argument("start", help="Start date in YYYYMMDD format.")
    parser.add_argument("end", help="End date in YYYYMMDD format.")
    parser.add_argument("outdir", nargs='?', default="/opt/data/SAFE", help="Output directory for downloads.")
    args = parser.parse_args()

    # --- 1. Authentication ---
    try:
        username = os.environ.get("EARTHDATA_USERNAME")
        password = os.environ.get("EARTHDATA_PASSWORD")

        if not username or not password:
            print("ERROR: EARTHDATA_USERNAME and EARTHDATA_PASSWORD environment variables must be set and non-empty.")
            sys.exit(1)

        print(f"DEBUG: Attempting authentication for user: {username}")
        # Password is not printed for security reasons

    except KeyError:
        print("ERROR: EARTHDATA_USERNAME and EARTHDATA_PASSWORD environment variables must be set.")
        sys.exit(1)

    try:
        # Catch specific exceptions that might occur during asf_search authentication
        session = asf.ASFSession().auth_with_creds(username, password)
        print("DEBUG: Authentication successful with asf_search!")
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Authentication failed due to HTTP error. Status Code: {e.response.status_code}, Response: {e.response.text}")
        print("Please check your Earthdata Login credentials and ensure ASF access is authorized.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Authentication failed due to connection error. Details: {e}")
        print("Please check your internet connection or firewall settings.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Authentication failed. Please check your Earthdata Login credentials. Details: {e}")
        sys.exit(1)

    # --- 2. Search ---
    with open(args.aoi_geojson, 'r') as f:
        geojson_data = json.load(f)
        # Determine if GeoJSON is a FeatureCollection or a direct Geometry
        if geojson_data.get('type') == 'FeatureCollection':
            geom = shape(geojson_data['features'][0]['geometry'])
        elif geojson_data.get('type') in ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection']:
            geom = shape(geojson_data)
        else:
            print(f"ERROR: Unsupported GeoJSON type: {geojson_data.get('type')}")
            sys.exit(1)


    start_date_str = args.start
    end_date_str = args.end
    start_dt = datetime.strptime(start_date_str, '%Y%m%d')
    end_dt = datetime.strptime(end_date_str, '%Y%m%d')

    # Define search range for ASF, typically broader than the exact start/end dates for flexibility
    # Here, we use the provided start/end dates directly for the search range
    search_start_date = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    search_end_date = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"DEBUG: Searching for Sentinel-1 SLC data for AOI: {args.aoi_geojson}, Search Start: {search_start_date}, Search End: {search_end_date}")

    try:
        results = asf.geo_search(
            platform=[asf.PLATFORM.SENTINEL1],
            intersectsWith=geom.wkt,
            start=search_start_date,
            end=search_end_date,
            processingLevel=asf.PRODUCT_TYPE.SLC,
            beamMode=asf.BEAMMODE.IW,
            # session=session # Removed as geo_search does not accept a session argument
        )
    except Exception as e:
        print(f"ERROR: ASF search failed. Details: {e}")
        sys.exit(1)


    if len(results) < 2:
        print(f"Found {len(results)} scenes, but need at least 2 for InSAR.")
        sys.exit(1)

    print(f"Found {len(results)} scenes.")

    # --- 3. Select and Download ---
    # Select two scenes: one closest to the specified start date and one closest to the specified end date.
    # This is ideal for pre/post-event InSAR comparisons.
    scene1 = None
    scene2 = None
    min_diff1 = float('inf') # Minimum time difference for scene1 (closest to start_dt)
    min_diff2 = float('inf') # Minimum time difference for scene2 (closest to end_dt)

    for scene in results:
        scene_dt = datetime.strptime(scene.properties['startTime'], '%Y-%m-%dT%H:%M:%SZ')
        
        # Find the scene closest to start_dt
        diff1 = abs((scene_dt - start_dt).total_seconds())
        if diff1 < min_diff1:
            min_diff1 = diff1
            scene1 = scene
        
        # Find the scene closest to end_dt
        diff2 = abs((scene_dt - end_dt).total_seconds())
        if diff2 < min_diff2:
            min_diff2 = diff2
            scene2 = scene

    scenes_to_download = []
    if scene1:
        scenes_to_download.append(scene1)
    
    # Add scene2 only if it's distinct from scene1
    if scene2 and scene2 != scene1:
        scenes_to_download.append(scene2)
    # If scene1 and scene2 are the same (meaning the same scene was closest to both start_dt and end_dt)
    # and there are other scenes available, find the second closest scene to start_dt.
    elif scene2 and scene2 == scene1 and len(results) >= 2:
        min_diff_second = float('inf')
        second_closest_scene = None
        for scene in results:
            if scene != scene1: # Ensure it's a different scene
                diff = abs((datetime.strptime(scene.properties['startTime'], '%Y-%m-%dT%H:%M:%SZ') - start_dt).total_seconds())
                if diff < min_diff_second:
                    min_diff_second = diff
                    second_closest_scene = scene
        if second_closest_scene:
            scenes_to_download.append(second_closest_scene)


    if len(scenes_to_download) < 2:
        print(f"ERROR: Could not find 2 distinct scenes closest to {start_date_str} and {end_dt}.")
        sys.exit(1)

    print(f"Selected 2 scenes closest to {start_date_str} and {end_dt} for download:")
    for scene in scenes_to_download:
        print(f"- {scene.properties['fileName']} (Start Time: {scene.properties['startTime']})")

    os.makedirs(args.outdir, exist_ok=True)
    
    print(f"DEBUG: Attempting to download scenes to {args.outdir}")
    try:
        # Iterate through the list of scenes and download each one individually
        for scene in scenes_to_download:
            zip_filepath = os.path.join(args.outdir, scene.properties['fileName'])
            scene.download(path=args.outdir, session=session)
            
            # Unzip the downloaded file
            print(f"DEBUG: Unzipping {zip_filepath}...")
            with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                zip_ref.extractall(args.outdir)
            print(f"DEBUG: Successfully unzipped {zip_filepath}")
            os.remove(zip_filepath) # Remove the zip file after extraction
            print(f"DEBUG: Removed {zip_filepath}")

        print(f"\nSuccessfully downloaded and unzipped {len(scenes_to_download)} scenes to {args.outdir}")
    except Exception as e:
        print(f"ERROR: Download or unzipping failed. Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()