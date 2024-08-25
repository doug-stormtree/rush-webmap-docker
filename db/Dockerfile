# use official PostGIS image
FROM postgis/postgis:16-3.4

# install python and dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip install geojson shapely jsonschema psycopg2-binary sqlalchemy geoalchemy2

# copy entrypoint, upload script, and geojson into image
# TODO: Delete entrypoint.sh and rename upload_geojson.py to entrypoint.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY upload_geojson.py /usr/local/bin/upload_geojson.py
COPY geojson /geojson
RUN chmod +x /usr/local/bin/upload_geojson.py /usr/local/bin/entrypoint.sh

# set entrypoint and start postgres
ENTRYPOINT ["python3", "/usr/local/bin/upload_geojson.py"]
CMD ["postgres"]