import csv
import json
import sys
import traceback
import uuid

from arches.app.utils.response import JSONResponse

from arches.app.views.api import APIBase
from arches.app.models import models
from arches.app.models.concept import get_valueids_from_concept_label
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.models.tile import Tile as TileProxyModel
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.datatypes.concept_types import ConceptListDataType, ConceptDataType


class ExternalResourceDataValidation(APIBase):
    def post(self, request, node_id=None):
        if node_id:
            return self.parse_and_validate_resource(request, node_id)
        else:
            return self.parse_and_validate_resources(request)

    def parse_and_validate_resources(self, request):
        datatype_factory = DataTypeFactory()

        column_name_to_node_data_map = json.loads(
            request.POST.get('column_name_to_node_data_map')
        )

        uploaded_file = request.FILES.get('uploaded_file')
        decoded_file = uploaded_file.read().decode('utf-8').splitlines()

        parsed_rows = []

        for row_dict in csv.DictReader(decoded_file):
            row_data = {}
            parsed_row_data = {}
            errors = {}
            location_data = {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point", 
                        "coordinates": [0, 0]
                    }
                }]
            }

            for key, value in row_dict.items():
                node_data = column_name_to_node_data_map[key]

                if node_data['node_id']:
                    # edge case for converting columns into complex node values
                    if (node_data.get('flag') == 'format_location'):
                        if 'x' in node_data['args']:
                            location_data['features'][0]['geometry']['coordinates'][1] = float(value)
                        if 'y' in node_data['args']:
                            location_data['features'][0]['geometry']['coordinates'][0] = float(value)
                        
                        row_data[node_data['node_id']] = location_data
                        parsed_row_data[node_data['node_id']] = location_data  # should be correct after all iterations
                    else:
                        row_data[node_data['node_id']] = value
                        node_id = node_data['node_id']

                        node = models.Node.objects.get(pk=node_id)
                        datatype = datatype_factory.get_instance(node.datatype)

                        if isinstance(datatype, (ConceptDataType, ConceptListDataType)):
                            value_data = get_valueids_from_concept_label(value)

                            # `get_valueids_from_concept_label` returns a list including concepts 
                            # where the value is a partial match let's filter for the exact value
                            exact_match = None

                            for value_datum in value_data:
                                if value_datum['value'] == value:
                                    exact_match = value_datum

                            if exact_match:
                                value = exact_match['id']  # value_id
                        
                            if isinstance(datatype, ConceptListDataType):
                                value = [value]

                        try:
                            validation_errors = datatype.validate(value, node=node)

                            if validation_errors:
                                errors[node_id] = {
                                    'errors': validation_errors,
                                    'node_id': node_id,
                                    'cell_value': value,
                                }
                        except Exception as e:
                            print(str(e))

                        parsed_row_data[node_id] = value

            parsed_rows.append({
                'row_id': str(uuid.uuid4()),
                'row_data': row_data,
                'location_data': location_data,
                'parsed_data': parsed_row_data,
                'errors': errors,
            })
                
        return JSONResponse({
            'node_ids_to_column_names_map': { v['node_id']:k for k,v in column_name_to_node_data_map.items() },
            'data': parsed_rows
        })

    def parse_and_validate_resource(self, request, node_id):
        # currently not working

        cell_value = json.loads(
            request.POST.get('cell_value')
        )

        datatype_factory = DataTypeFactory()

        node = models.Node.objects.get(pk=node_id)
        datatype = datatype_factory.get_instance(node.datatype)

        errors = []
        
        # GET RID OF TRY AFTER DOMAIN VALUE REFACTOR!
        try:
            validation_errors = datatype.validate(cell_value, node=node)

            if validation_errors:
                errors.append({
                    'errors': validation_errors,
                    'node_id': node_id,
                    'cell_value': cell_value
                })

        except Exception as e:
            print(str(e))

        return JSONResponse({ 'errors': errors })


class ExternalResourceDataCreation(APIBase):
    def post(self, request, graphid=None):
        try:
            body = json.loads(request.body)
            file_data = body['file_data']
            column_name_to_node_data_map = body['column_name_to_node_data_map']

            nodegroup_data = {}

            for node_data in column_name_to_node_data_map.values():
                nodegroup_id = node_data.get('nodegroup_id')

                if nodegroup_id:
                    if not nodegroup_data.get(nodegroup_id):
                        nodegroup_data[nodegroup_id] = []

                    nodegroup_data[nodegroup_id].append(node_data['node_id'])

            for file_datum in file_data:
                for row_data in file_datum['data']:
                    resource_instance = Resource(graph_id=graphid)
                    resource_instance.save()

                    parsed_data = row_data['parsed_data']

                    tile_data = {}

                    for nodegroup_id in nodegroup_data.keys():
                        if not tile_data.get(nodegroup_id):
                            tile_data[nodegroup_id] = {}

                        for node_id in nodegroup_data[nodegroup_id]:
                            tile_data[nodegroup_id][node_id] = parsed_data.get(node_id)

                    for nodegroup_id in tile_data.keys():
                        tile = TileProxyModel(
                            data=tile_data[nodegroup_id],
                            resourceinstance=resource_instance,
                            nodegroup_id=nodegroup_id,
                            # nodegroup_id = 'f7c974a0-29f4-11eb-8487-aae9fe8789ac',  # Related Observations
                        )

                        tile.save()

                    file_datum['created_resources'][row_data['row_id']] = {
                        'resourceinstance_id': str(resource_instance.pk),
                        'row_id': row_data['row_id'],
                        'tile_data': tile_data,
                    }
                    
            return JSONResponse({
                'file_data': file_data,
            }, status=200)
            
        except Exception as e:
            if settings.DEBUG is True:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                formatted = traceback.format_exception(exc_type, exc_value, exc_traceback)
                if len(formatted):
                    for message in formatted:
                        print(message)
            return JSONResponse({"error": "resource data could not be saved: %s" % e}, status=500, reason=e)