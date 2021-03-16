define([
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'mapbox-gl',
    'geojson-extent',
    'viewmodels/card-component',
    'viewmodels/map-editor',
    'viewmodels/map-filter',
    'views/components/cards/related-resources-map',
    'views/components/cards/select-related-feature-layers',
    'text!templates/views/components/cards/external-resource-data-preview-popup.htm',
    'views/components/external-resource-data-preview/external-resource-data-preview',

], function($, arches, ko, koMapping, mapboxgl, geojsonExtent, CardComponentViewModel, MapEditorViewModel, MapFilterViewModel, RelatedResourcesMapCard, selectFeatureLayersFactory, popupTemplate) {
    /* 
        Used to connect the external-resource-data-preview component 
        with the related-resources-map-card
    */ 
    var viewModel = function(params) {
        var self = this;
        ko.utils.extend(self, new RelatedResourcesMapCard(params));

        this.draw = params.draw;
        this.map = ko.observable(params.map);

        this.additionalRelatedResourceContent = ko.observable(true);

        this.fileData = ko.observable();
        this.fileData.subscribe(function(fileData) {
            if (!self.draw) {
                self.draw = params.draw;
            }
            if (!ko.unwrap(self.map)) {
                self.map(params.map);
            }
            self.updateMap(fileData)
        });

        this.selectData = function(uncreatedResourceData) {
            if (self.popup) {
                self.popup.remove()
                self.popup = undefined;
            }

            var map = self.map();
            
            var feature = _.find(
                map.queryRenderedFeatures(),
                function(feature) { return feature.properties.id === uncreatedResourceData.row_id; }
            );

            var selectData = function(feature) {
                feature.id = feature.properties.id;
        
                self.draw.changeMode('simple_select', {
                    featureIds: [feature.id]
                });

                self.popup = new mapboxgl.Popup()
                    .setLngLat(uncreatedResourceData.location_data.features[0].geometry.coordinates)
                    .setHTML(popupTemplate)
                    .addTo(map);
                ko.applyBindingsToDescendants(
                    uncreatedResourceData,
                    self.popup._content
                );

                if (map.getStyle()) {
                    map.setFeatureState(feature, { selected: true });
                }

                self.popup.on('close', function() {
                    if (map.getStyle()) map.setFeatureState(feature, { selected: false });
                    self.popup = undefined;
                });
            };

            if (feature) {
                selectData(feature)
            }
            else {
                /* feature not in viewport */ 
                self.loading(true);

                /* fitBounds can be considered async, so we need a listener */ 
                map.once("moveend", function() {
                    var feature = _.find(
                        map.queryRenderedFeatures(),
                        function(feature) { return feature.properties.id === uncreatedResourceData.row_id; }
                    );

                    if (feature) { selectData(feature); }

                    self.loading(false);
                });

                map.fitBounds(
                    geojsonExtent(uncreatedResourceData.location_data),
                    { 
                        padding: { top: 20, right: 560, bottom: 240, left: 120 },
                        linear: true,
                    }
                )
            }
        };

        this.updateMap = function(fileData) {
            if (self.draw) {
                self.draw.deleteAll();

                var bounds = new mapboxgl.LngLatBounds();
        
                fileData.forEach(function(fileDatum) {
                    fileDatum.data.forEach(function(parsedRow) {
                        if (parsedRow.location_data) {
                            parsedRow.location_data.features.forEach(function(feature) {
                                feature.id = parsedRow.row_id;
                                self.draw.add(feature);
                                bounds.extend(feature.geometry.coordinates);
                            });
                        }
                    });
                });
    
                if (fileData.length) {
                    self.map().fitBounds(
                        bounds, 
                        { 
                            padding: { top: 20, right: 560, bottom: 240, left: 120 },
                            linear: true,
                        }
                    );
                }
            }
        }

        self.map.subscribe(function(map) {
            if (!self.draw && params.draw) {
                self.draw = params.draw;
            }

            if (self.fileData()) {
                self.updateMap(self.fileData())
            }

            map.on('click', function(e) {
                var hoverFeature = _.find(
                    map.queryRenderedFeatures(e.point),
                    function(feature) { return feature.properties.id; }
                );

                if (hoverFeature) {
                    hoverFeature.id = hoverFeature.properties.id;

                    var featureData = self.fileData().reduce(function(acc, fileDatum) {
                        acc = fileDatum.data.find(function(parsedRow) {
                            return parsedRow.row_id === hoverFeature.id;
                        });

                        return acc;
                    }, null)

                    if (featureData) {
                        self.popup = new mapboxgl.Popup()
                            .setLngLat(e.lngLat)
                            .setHTML(popupTemplate)
                            .addTo(map);
                        ko.applyBindingsToDescendants(
                            featureData,
                            self.popup._content
                        );
    
                        if (map.getStyle()) {
                            map.setFeatureState(hoverFeature, { selected: true });
                        }
    
                        self.popup.on('close', function() {
                            if (map.getStyle()) map.setFeatureState(hoverFeature, { selected: false });
                            self.popup = undefined;
                        });
                    }
                }
            });
        });
    }

    ko.components.register('external-resource-data-preview-map', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/related-resources-map.htm'
        }
    });

    return viewModel;
});
