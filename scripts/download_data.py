import asf_search as asf
import os
import sys
import argparse
from shapely.geometry import shape
import json
from datetime import datetime
import requests
import zipfile


def get_relative_orbit(scene):
    """Extract relative orbit number safely."""
    return scene.properties.get("relativeOrbit")


def pick_best_orbit(scenes):
    """Select the orbit that has the most scenes (best temporal sampling)."""
    orbit_counts = {}

    for s in scenes:
        orbit = get_relative_orbit(s)
        if orbit:
            orbit_counts[orbit] = orbit_counts.get(orbit, 0) + 1

    if not orbit_counts:
        return None

    # Orbit with the MOST scenes
    best = max(orbit_counts, key=orbit_counts.get)
    return best


def select_best_pair(scenes, start_dt, end_dt):
    """Select closest scenes to start_dt and end_dt."""
    scene1 = None
    scene2 = None
    diff1_min = float('inf')
    diff2_min = float('inf')

    for scene in scenes:
        scene_dt = datetime.strptime(scene.properties['startTime'], '%Y-%m-%dT%H:%M:%SZ')

        diff1 = abs((scene_dt - start_dt).total_seconds())
        if diff1 < diff1_min:
            diff1_min = diff1
            scene1 = scene

        diff2 = abs((scene_dt - end_dt).total_seconds())
        if diff2 < diff2_min:
            diff2_min = diff2
            scene2 = scene

    # Ensure two distinct scenes
    if scene1 == scene2:
        candidates = sorted(
            scenes,
            key=lambda s: abs(
                (datetime.strptime(s.properties['startTime'], '%Y-%m-%dT%H:%M:%SZ') - start_dt
                 ).total_seconds()
            )
        )
        if len(candidates) >= 2:
            scene1, scene2 = candidates[0], candidates[1]

    return [scene1, scene2]


def unzip_and_cleanup(zip_path, outdir):
    """Unzip SAFE and delete zip."""
    print(f"DEBUG: Unzipping {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(outdir)
    print("DEBUG: Unzipped successfully.")
    os.remove(zip_path)
    print(f"DEBUG: Removed {zip_path}")


def main():
    parser = argparse.ArgumentParser(description="Search & download Sentinel-1 SLC InSAR-ready scenes.")
    parser.add_argument("aoi_geojson", help="Path to AOI GeoJSON.")
    parser.add_argument("start", help="Start date YYYYMMDD.")
    parser.add_argument("end", help="End date YYYYMMDD.")
    parser.add_argument("outdir", nargs="?", default="/opt/data/SAFE", help="Output directory.")
    args = parser.parse_args()

    # --- 1. AUTH ---
    username = os.environ.get("EARTHDATA_USERNAME")
    password = os.environ.get("EARTHDATA_PASSWORD")

    if not username or not password:
        print("ERROR: EARTHDATA_USERNAME and EARTHDATA_PASSWORD must be set.")
        sys.exit(1)

    print(f"DEBUG: Authenticating as {username}")
    try:
        session = asf.ASFSession().auth_with_creds(username, password)
        print("DEBUG: Authentication OK")
    except Exception as e:
        print(f"ERROR: Authentication failed: {e}")
        sys.exit(1)

    # --- 2. LOAD GEOJSON ---
    with open(args.aoi_geojson, 'r') as f:
        geojson = json.load(f)
    if geojson.get("type") == "FeatureCollection":
        geom = shape(geojson["features"][0]["geometry"])
    else:
        geom = shape(geojson)

    start_dt = datetime.strptime(args.start, "%Y%m%d")
    end_dt   = datetime.strptime(args.end, "%Y%m%d")

    start_iso = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso   = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"DEBUG: ASF search from {start_iso} to {end_iso}")

    # --- 3. ASF SEARCH ---
    try:
        results = asf.geo_search(
            platform=[asf.PLATFORM.SENTINEL1],
            processingLevel=asf.PRODUCT_TYPE.SLC,
            beamMode=asf.BEAMMODE.IW,
            intersectsWith=geom.wkt,
            start=start_iso,
            end=end_iso
        )
    except Exception as e:
        print(f"ERROR: Search failed: {e}")
        sys.exit(1)

    if len(results) < 2:
        print(f"ERROR: Only {len(results)} scenes found. Need ≥2.")
        sys.exit(1)

    print(f"DEBUG: Found {len(results)} scenes total.")

    # --- 4. FILTER BY ORBIT (CRITICAL FOR INSAR) ---
    best_orbit = pick_best_orbit(results)
    if best_orbit is None:
        print("ERROR: No relativeOrbit values found.")
        sys.exit(1)

    print(f"DEBUG: Selected relative orbit {best_orbit}")

    same_orbit = [s for s in results if get_relative_orbit(s) == best_orbit]
    if len(same_orbit) < 2:
        print(f"ERROR: Not enough scenes on orbit {best_orbit}")
        sys.exit(1)

    print(f"DEBUG: {len(same_orbit)} scenes on orbit {best_orbit}")

    # --- 5. CHOOSE BEST PAIR ---
    pair = select_best_pair(same_orbit, start_dt, end_dt)
    if len(pair) < 2 or None in pair:
        print("ERROR: Could not determine 2-scene pair.")
        sys.exit(1)

    print("Selected scenes:")
    for s in pair:
        print(f"- {s.properties['fileName']} (Start: {s.properties['startTime']})")

    # --- 6. DOWNLOAD + UNZIP ---
    os.makedirs(args.outdir, exist_ok=True)

    for scene in pair:
        zip_path = os.path.join(args.outdir, scene.properties["fileName"])
        print(f"DEBUG: Downloading {zip_path}")

        try:
            scene.download(path=args.outdir, session=session)
            unzip_and_cleanup(zip_path, args.outdir)
        except Exception as e:
            print(f"ERROR downloading {scene.properties['fileName']}: {e}")
            sys.exit(1)

    print("\nSUCCESS: All scenes downloaded & extracted.")


if __name__ == "__main__":
    main()