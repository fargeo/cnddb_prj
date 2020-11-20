SET CLIENT_ENCODING TO UTF8;
SET STANDARD_CONFORMING_STRINGS TO ON;
BEGIN;

INSERT INTO map_sources(name, source)
VALUES ('observation-source', '{
    "data": "/geojson?nodeids=df79c02a-033f-11eb-9978-02e99e44e93e&include_geojson_link=true",
    "type": "geojson"
}');