# use official PostGIS image
FROM postgis/postgis:16-3.4

# install python and dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install psycopg2-binary geojson shapely

# copy entrypoint, upload script, and geojson into image
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY upload_geojson.py /usr/local/bin/upload_geojson.py
COPY geojson /geojson
RUN chmod +x /usr/local/bin/upload_geojson.py /usr/local/bin/entrypoint.sh

# set entrypoint and start postgres
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["postgres"]