import psycopg2
import os
import json
import geojson
from numbers import Number

"""
Upload geojson files from a directory to the app's PostgreSQL database.

NOTE: This script does not handle duplicates. If you use this script manually and re-upload
      the same geojson files you will create duplicate entries in the database.
"""

# db connection details
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# script constants
GEOJSON_DIR = os.getenv('GEOJSON_DIR')


class NoGeoFeatures(Exception):
    """
    Raised when a geoJSON file is loaded but does not contain
    a 'features' key at the top-level.
    """
    def __init__(self, filename):
        super().__init__(f'The geojson file {filename} is missing a \'features\' key.')


class BadGeoFeature(Exception):
    """
    Base exception class for when geoJSON feature data is malformed.
    """
    pass


class NoProperties(BadGeoFeature):
    """
    Raised when a geoJSON feature is missing the 'properties' key.
    """
    def __init__(self, filename):
        super().__init__(f'The file {filename} contains a geoJSON feature that is missing the \'properties\' key.')


class NoGeometry(BadGeoFeature):
    """
    Raised when a geoJSON feature is missing the 'geometry' key.
    """
    def __init__(self, filename):
        super().__init__(f'The file {filename} contains a geoJSON feature that is missing the \'geometry\' key.')


class BadGeometry(BadGeoFeature):
    """
    Base exception class for when a geoJSON feature's geometry is malformed.
    """
    pass


class NoCoordinates(BadGeometry):
    """
    Raised when a geoJSON feature's geometry is missing the 'coordinates' key.
    """
    def __init__(self, filename, properties):
        super().__init__(f'The file {filename} contains geoJSON feature geometry that is missing the \'coordinates\' key. {properties}')


class InvalidCoordinateDimensions(BadGeometry):
    """
    Raised when a geoJSON feature's geometry's coordinates are not 2-dimensional.
    """
    def __init__(self, filename, num_dimensions):
        super().__init__(f'The file {filename} contains a geoJSON feature with geometry coordinates containing {num_dimensions} dimensions, but 2 were expected.')


class NonNumericCoordinates(BadGeometry):
    """
    Raised when a geoJSON feature's geometry's coordinates contain one or more
    non-numeric values.
    """
    def __init__(self, filename, coordinates):
        super().__init__(f'The file {filename} contains a geoJSON feature with geometry coordinates \'{coordinates}\' containing non-numeric coordinate values.')


def file_to_geojson(file) -> dict:
    """
    Read the contents of a geojson file into a Python dictionary and return it,
    or raise if the contents of the file do not match a subset of the geojson spec.
    """
    print(f'Uploading {file.name}...')
    data = json.load(file)
    if 'features' not in data:
        raise NoGeoFeatures(file.name)

    for feature in data['features']:

        if 'properties' not in feature:
            raise NoProperties(file.name)

        if 'geometry' not in feature:
            raise NoGeometry(file.name)

        geometry = feature['geometry']
        if 'coordinates' not in geometry:
            raise NoCoordinates(file.name, feature['properties'])

        coordinates = geometry['coordinates']
        if isinstance(coordinates[0], list):  # Handle nested coordinates (e.g., LineString, Polygon)
            coordinates = [coord[:2] for coord in coordinates]
        else:
            coordinates = coordinates[:2]  # Strip Z dimension

        if not all(isinstance(coord, (Number, list)) for coord in coordinates):
            raise NonNumericCoordinates(file.name, coordinates)

        geometry['coordinates'] = coordinates

    return data


def get_geojson_filenames():
    """
    Get a list of all geojson filenames in the geojson directory.
    """
    return [x for x in os.listdir(GEOJSON_DIR) if x.endswith('.geojson')]


conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS geo_features (
    id SERIAL PRIMARY KEY,
    name TEXT,
    properties JSONB,
    geometry GEOMETRY(Geometry, 4326)
);
""")


for filename in get_geojson_filenames():
    with open(os.path.join(GEOJSON_DIR, filename)) as file:
        try:
            data = file_to_geojson(file)
            for feature in data['features']:
                properties_str = json.dumps(feature['properties'])
                geometry_str = geojson.dumps(feature['geometry'])
                cursor.execute("""
                INSERT INTO geo_features (name, properties, geometry)
                VALUES (%s, %s, ST_GeomFromGeoJSON(%s))
                """, (filename, properties_str, geometry_str))
        except Exception as e:
            print(f'ERROR processing file {filename}: {str(e)}')
            continue


conn.commit()
cursor.close()
conn.close()
exit(0)
