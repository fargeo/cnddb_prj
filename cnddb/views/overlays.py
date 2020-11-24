from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches.app.models import models
from arches.app.views.search import search_results
from django.http import HttpRequest
import json
from django.db import connection
from django.http import Http404, HttpResponse

class MVT_County(View):
    def get(self, request, zoom, x, y):
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT ST_AsMVT(tile, 'ca_counties')
                    FROM (SELECT row_number() over () as id,
                            name,
                            ST_AsMVTGeom(
                                ST_CurveToLine(geom),
                                TileBBox(%s, %s, %s, 4326)) AS geom
                        FROM ca_counties) AS tile""",
                    [zoom, x, y])
            tile = bytes(cursor.fetchone()[0])
            if not len(tile):
                raise Http404()
        return HttpResponse(tile, content_type="application/x-protobuf")

class MVT_Quad(View):
    def get(self, request, zoom, x, y):
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT ST_AsMVT(tile, 'quad24')
                    FROM (SELECT row_number() over () as id,
                            quad24name,
                            ST_AsMVTGeom(
                                ST_CurveToLine(geom),
                                TileBBox(%s, %s, %s, 4326)) AS geom
                        FROM quad24) AS tile""",
                    [zoom, x, y])
            tile = bytes(cursor.fetchone()[0])
            if not len(tile):
                raise Http404()
        return HttpResponse(tile, content_type="application/x-protobuf")
