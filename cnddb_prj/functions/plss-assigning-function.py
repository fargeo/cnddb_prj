 # coding: utf-8

import uuid
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.resource import Resource
from django.contrib.gis.geos import GEOSGeometry
import json
from datetime import datetime
import requests


details = {
    'name': 'plss assigning function',
    'type': 'node',
    'description': "assigning plss id which geometry or centroid intersects with",
    'defaultconfig':{"triggering_nodegroups": ["d4618775-d986-11e9-b40b-acde48001122"],
                     "geom_node_id": "d461ad11-d986-11e9-a45d-acde48001122",
                     "plss_node_id": "d4619c33-d986-11e9-90c7-acde48001122"},
    'classname': 'PLSSAssigning',
    'component': '',
    'functionid': 'd9a01773-6092-4cad-b331-ae725ae8fa88'
}

class PLSSAssigning(BaseFunction):

    def get(self):
        raise NotImplementedError

    def save(self,tile,request):
        """ Finds the PLSS for the centroid of the envelope(extent) of the Geometry,
            and saves that value to the plssid_node_id of the tile
        """
        def get_plss(x, y):
            url = 'https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer/3/query?where=1%3D1&text=&objectIds=&time=&geometry=%7B%22x%22%3A${0}%2C%22y%22%3A${1}%2C%22spatialReference%22%3A%7B%22wkid%22%3A4326%7D%7D&geometryType=esriGeometryPoint&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=false&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&having=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentOnly=false&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&f=pjson&__ncforminfo=i3tgZCqTzeKi1SHp4wmtFEy4aFMLhX9LqrXB77w7F_EgHOvPt67dS7SP50Lm-l5AzS0FNHEkuSP2x-ZKXylvtc9M3OmZpVXm6dXfPYWOOFsU_FwTvJg-ZmM65c-Vz_UoqLzdGaWV9Cb-xEEOhRBT9b5wW1AfqGpf-sDHc1DBUckHvdgksgdEjiSEsYvyhwFIkpwgcY2crkn8XmgBfnjMK0LJKybG1QxlZZJ5OgD1JajNTtA3ENhBLHko30b3hCZvnDL4kupg8u2wTASEfGSll3FrE8elkwn09SJquRRGhVCTyqFvOtygW-flftd_MGikcKmA4FzCMRy2PO15e4PsV31--5DIOMmW3jTv0qaNgBTQVvqxRxPK8o56KKu2tKZp91kLrf692jPCNnA-oJAMF2a03VL2bL0i3qT_Ag4zSxcPBD325O4uH72JNRbcPf6cHo-0ej1h1tI1s62m0RB2gqAEfvptFc4Vd7p0ml1X_fcsqYHz4ukRRvdLId_zrpNht56QrikKHcRCYDVJYGZ3Rifg-QoKarMypeT0VwSP0ySV_jIfBm8-AtWJ0KBw1_WYpZkf7mypLnXRv-24Q9g28dluOARu71fIhSfXuWejPa8aas5ziDK5eEIRFkfaXxDPQqaSkxMwjRjXW4azlcRAZKzEWgrAc6Wwiv8eiB7mEavf7bpschF35-hQWzI3cIft'.format(x, y)
            resp = requests.get(url)
            data = resp.json()

            try:
                plssid = data['features'][0]['attributes']['TWNSHPLAB']
            except (KeyError, IndexError) as e:
                plssid = "not available at this location"

            return plssid

        # First let's check if this call is as a result of an inbound request (user action) or
        # as a result of the complementary BNGPointToGeoJSON function saving a new GeoJson.
        if request is None:
            return

        srid_LatLong = 4326

        geom_node = self.config[u"geom_node_id"]
        plss_node = self.config[u"plss_node_id"]

        geom = tile.data[geom_node]

        if geom != None:

            #Grab a copy of the Geometry collection.
            geoJsFeatures = geom[u'features']

            # Get the first feature as a GeosGeometry.
            geosGeom_union = GEOSGeometry(json.dumps(geoJsFeatures[0]['geometry']))

            # update list.
            geoJsFeatures = geoJsFeatures[1:]

            # loop through list of geoJsFeatures.
            for item in geoJsFeatures:
                # .union seems to generate 'GEOS_ERROR: IllegalArgumentException:'
                # exceptions, but they seem spurious and are automatically ignored.
                geosGeom_union = geosGeom_union.union(GEOSGeometry(json.dumps(item['geometry'])))

            # find the centroid of the envelope for the resultant Geometry Collection.
            centroidPoint = geosGeom_union.envelope.centroid

            # Explicitly declare the SRID for the current lat/long.
            centroidPoint = GEOSGeometry(centroidPoint, srid=srid_LatLong)

            tile.data[plss_node] = get_plss(centroidPoint.x, centroidPoint.y)

        # Save Tile to cement Parent Tile to subsequent bng_output_nodegroup.
        return

    def delete(self,tile,request):
        raise NotImplementedError

    def on_import(self,tile):
        raise NotImplementedError

    def after_function_save(self,tile,request):
        raise NotImplementedError

# if __name__ == "main":
#     GJS = GeoJSONToBNGPoint()
#     GJS.on_import(None,None)
