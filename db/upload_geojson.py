import json
import os
import subprocess
import time
from typing import *
import jsonschema
import geojson
import psycopg2
import psycopg2.sql
import psycopg2._psycopg
import shapely

def get_env_dict() -> Dict[str, str]:
    """
    Get a dict of required env vars, raise an error if any are missing.
    """

    required_env_vars = [
        'POSTGRES_DB',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'DB_HOST',
        'DB_PORT',
    ]
    missing_varnames = []
    env_dict = {}
    for varname in required_env_vars:
        if var := os.getenv(varname):
            env_dict[varname] = var
        else:
            missing_varnames.append(varname)

    if len(missing_varnames) > 0:
        raise ValueError(f'Missing required env vars: {missing_varnames}.')

    return env_dict


def start_db() -> subprocess.Popen:
    """
    Start the PostgreSQL database and return the process.
    """
    return subprocess.Popen(["docker-entrypoint.sh", "postgres"])


def wait_for_db(db, user, pw, host, port) -> psycopg2._psycopg.connection:
    """
    Wait for database to spin up and return a connection.
    """

    while True:
        try:
            subprocess.run(
                ["pg_isready", "-h", host, "-p", port, "-U", user],
                check=True,
            )
            print("PostgreSQL is up - executing commands")
            break
        except subprocess.CalledProcessError:
            print("PostgreSQL is unavailable - sleeping")
            time.sleep(1)
        except FileNotFoundError as e:
            raise RuntimeError(
                'Please make sure you are running this script in an environment with PostgreSQL installed!'
            ) from e

    connection = psycopg2.connect(
        dbname=db,
        user=user,
        password=pw,
        host=host,
        port=port,
    )
    connection.autocommit = True
    return connection


def init_db(connection, db, user, pw) -> None:
    """
    Initialize the database with a `geo_features` table if it doesn't exist, else do nothing.
    """

    with connection.cursor() as cursor:
        create_user = psycopg2.sql.SQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = {user_literal}) THEN
                    CREATE ROLE {user} WITH LOGIN PASSWORD {pw_literal};
                    ALTER ROLE {user} CREATEDB;
                END IF;
            END
            $$;
            """
        ).format(
            user=psycopg2.sql.Identifier(user),
            user_literal=psycopg2.sql.Literal(user),
            pw_literal=psycopg2.sql.Literal(pw),
        )
        create_db = psycopg2.sql.SQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_database WHERE datname = {db_literal}) THEN
                    CREATE DATABASE {db};
                    GRANT ALL PRIVILEGES ON DATABASE {db} TO {user};
                END IF;
            END
            $$;
            """
        ).format(
            user=psycopg2.sql.Identifier(user),
            db=psycopg2.sql.Identifier(db),
            db_literal=psycopg2.sql.Literal(db),
        )
        cursor.execute(create_user)
        cursor.execute(create_db)

        # check if the table 'geo_features' exists
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'geo_features'
            );
            """
        )
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            print("Table 'geo_features' doesn't exist yet! Creating a new one...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS feature_collection (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    coordinate_reference_system TEXT,
                    properties JSONB,
                    geometry GEOMETRY(Geometry, 4326)
                );
                """
            )


def validate_geojson_format(geojson_data: Dict[str, Any], filename: str) -> None:
    """
    Raise a validation error if the given geojson data is incorrectly formatted.
    """

    try:
        # validate the file's geojson format (we only expect FeatureCollection objects for now..)
        jsonschema.validate(instance=geojson_data, schema={
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["FeatureCollection"]
                },
                "features": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["Feature"]
                            },
                            "geometry": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": [
                                            "Point", "LineString", "Polygon",
                                            "MultiPoint", "MultiLineString", "MultiPolygon",
                                            "GeometryCollection"
                                        ]
                                    },
                                    "coordinates": {
                                        "type": "array",
                                    }
                                },
                                "required": ["type", "coordinates"]
                            },
                            "properties": {
                                "type": "object"
                            }
                        },
                        "required": ["type", "geometry"]
                    }
                }
            },
            "required": ["type", "features"]
        })
    except jsonschema.exceptions.ValidationError as e:
        raise jsonschema.exceptions.ValidationError(
            f"Invalid geojson formatting in {filename}: {e.message}"
        ) from e


def validate_feature_geometry(geometry: Dict[str, Any], filename: str) -> None:
    """
    Raise a validation error if the geometry shape is invalid.
    """

    geom_shape = shapely.geometry.shape(geometry)
    if not shapely.is_valid(geom_shape):
        reason = shapely.is_valid_reason(geom_shape)
        raise shapely.errors.ShapelyError(
            f"Invalid geojson geometry in {filename}: {reason}."
        )


def geojson_file_data(geojson_dir: str) -> Iterable[Dict[str, Any]]:
    """
    A generator that produces geojson
    """


def geojson_features(geojson_dir: str) -> Iterable[Dict[str, Any]]:
    """
    A generator of valid geojson features from a directory containing .geojson files.
    """

    filenames = [x for x in os.listdir(geojson_dir) if x.endswith(".geojson")]
    for filename in filenames:
        with open(os.path.join(geojson_dir, filename)) as file:
            # open every geojson file in the specified directory

            print(f'Scanning {filename} for geojson features..')
            geojson = json.load(file)

            try:
                validate_geojson_format(geojson, filename)
            except jsonschema.exceptions.ValidationError as e:
                print(str(e))
                continue

            for feature in geojson["features"]:
                #geometry = feature['geometry']
                #try:
                #    validate_feature_geometry(geometry, filename)
                #except shapely.errors.ShapelyError as e:
                #    #if "Self-intersection" not in str(e):
                #        # suppress errors about shapes intersecting with
                #        # themselves, this is probably okay..
                #    print(str(e))

                yield feature


db, user, pw, host, port = get_env_dict().values()
db_process = start_db()
connection = wait_for_db(db, user, pw, host, port)
init_db(connection, db, user, pw)
for feature in geojson_features('/geojson'):
    pass
print(f'Done!')
db_process.wait()  # stop automatic shutdown

exit(0)


# Start PostgreSQL process in the background
subprocess.Popen(["docker-entrypoint.sh", "postgres"])

# Wait for PostgreSQL to be ready
wait_for_postgres()

# Create user and database if they do not exist
create_user_and_db()

# Load GeoJSON data if needed
load_geojson_if_needed()


class NoGeoFeatures(Exception):
    """
    Raised when a geoJSON file is loaded but does not contain
    a 'features' key at the top-level.
    """

    def __init__(self, filename):
        super().__init__(f"The geojson file {filename} is missing a 'features' key.")


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
        super().__init__(
            f"The file {filename} contains a geoJSON feature that is missing the 'properties' key."
        )


class NoGeometry(BadGeoFeature):
    """
    Raised when a geoJSON feature is missing the 'geometry' key.
    """

    def __init__(self, filename):
        super().__init__(
            f"The file {filename} contains a geoJSON feature that is missing the 'geometry' key."
        )


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
        super().__init__(
            f"The file {filename} contains geoJSON feature geometry that is missing the 'coordinates' key. {properties}"
        )


class InvalidCoordinateDimensions(BadGeometry):
    """
    Raised when a geoJSON feature's geometry's coordinates are not 2-dimensional.
    """

    def __init__(self, filename, num_dimensions):
        super().__init__(
            f"The file {filename} contains a geoJSON feature with geometry coordinates containing {num_dimensions} dimensions, but 2 were expected."
        )


class NonNumericCoordinates(BadGeometry):
    """
    Raised when a geoJSON feature's geometry's coordinates contain one or more
    non-numeric values.
    """

    def __init__(self, filename, coordinates):
        super().__init__(
            f"The file {filename} contains a geoJSON feature with geometry coordinates '{coordinates}' containing non-numeric coordinate values."
        )


def file_to_geojson(file) -> dict:
    """
    Read the contents of a geojson file into a Python dictionary and return it,
    or raise if the contents of the file do not match a subset of the geojson spec.
    """




    print(f"Uploading {file.name}...")
    data = json.load(file)
    if "features" not in data:
        raise NoGeoFeatures(file.name)

    for feature in data["features"]:

        if "properties" not in feature:
            raise NoProperties(file.name)

        if "geometry" not in feature:
            raise NoGeometry(file.name)

        geometry = feature["geometry"]
        if "coordinates" not in geometry:
            raise NoCoordinates(file.name, feature["properties"])

        coordinates = geometry["coordinates"]
        if isinstance(
            coordinates[0], list
        ):  # Handle nested coordinates (e.g., LineString, Polygon)
            coordinates = [coord[:2] for coord in coordinates]
        else:
            coordinates = coordinates[:2]  # Strip Z dimension

        if not all(isinstance(coord, (Number, list)) for coord in coordinates):
            raise NonNumericCoordinates(file.name, coordinates)

        geometry["coordinates"] = coordinates

    return data


def get_geojson_filenames():
    """
    Get a list of all geojson filenames in the geojson directory.
    """
    return [x for x in os.listdir(GEOJSON_DIR) if x.endswith(".geojson")]


conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
)


cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS geo_features (
    id SERIAL PRIMARY KEY,
    name TEXT,
    properties JSONB,
    geometry GEOMETRY(Geometry, 4326)
);
"""
)


for filename in get_geojson_filenames():
    with open(os.path.join(GEOJSON_DIR, filename)) as file:
        try:
            data = file_to_geojson(file)
            for feature in data["features"]:
                properties_str = json.dumps(feature["properties"])
                geometry_str = geojson.dumps(feature["geometry"])
                cursor.execute(
                    """
                INSERT INTO geo_features (name, properties, geometry)
                VALUES (%s, %s, ST_GeomFromGeoJSON(%s))
                """,
                    (filename, properties_str, geometry_str),
                )
        except Exception as e:
            print(f"ERROR processing file {filename}: {str(e)}")
            continue


conn.commit()
cursor.close()
conn.close()
exit(0)
