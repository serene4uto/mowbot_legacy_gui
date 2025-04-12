import json
from PyQt5.QtWidgets import (
    QWidget, 
    QVBoxLayout
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from app.utils.logger import logger


class JsPyBridge(QObject):
    """Bridge between Python and JavaScript"""
    signal_tracker_gps_updated = pyqtSignal(str)
    signal_tracker_heading_updated = pyqtSignal(str)
    signal_marks_gps_added = pyqtSignal(str)
    signal_marks_gps_removed = pyqtSignal(str)
    
    @pyqtSlot(str)
    def receive_from_js(self, message):
        """Receive message from JavaScript"""
        logger.debug(f"Received from JS: {message}")
        

class MapViewWidget(QWidget):
    """Map view widget using Leaflet with Bing satellite imagery and OSM fallback"""
    
    def __init__(
            self, 
            parent=None
        ):
        """Initialize the map view widget"""
        super().__init__(parent)  
        # Setup UI
        self._init_ui()
        # Create a bridge for Python-JavaScript communication
        self.jspy_bridge = JsPyBridge()
        # Setup web channel
        self.channel = QWebChannel()
        self.channel.registerObject("jspy_bridge", self.jspy_bridge)
        self.web_view.page().setWebChannel(self.channel)
        # Load the HTML with Leaflet map, Bing layer, waypoints,
        self._load_map()
        
    
    def _init_ui(self):
        layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view, stretch=8)
        self.setLayout(layout)
        
    
    def _load_map(self):
        """Load the Leaflet map HTML with Bing satellite imagery and a fallback to OSM.
           Waypoints are drawn as blue circle markers, and the tracking marker uses a red arrow icon
           that rotates according to the heading."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>GPS Tracker with Bing Satellite</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
            <!-- Include Leaflet, RotatedMarker plugin (from unpkg), and Qt WebChannel -->
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
            <script src="https://unpkg.com/leaflet-rotatedmarker/leaflet.rotatedMarker.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                html, body, #map {
                    height: 100%;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Initialize the map centered at the first waypoint
                var map = L.map('map').setView([37.7749, -122.4194], 19); // max zoom
                
                // Define the tracking marker icon (red arrow)
                var trackingIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                
                // var trackingIcon = L.icon({
                //     iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                //     shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                //     iconSize: [13, 21],
                //     iconAnchor: [6, 21],
                //     popupAnchor: [1, -17],
                //     shadowSize: [21, 21]
                // });

                // Define a custom Bing Maps layer class with quadkey replacement support
                L.BingLayer = L.TileLayer.extend({
                    options: {
                        bingMapsKey: 'AkCDUXwYzM3w36XYcNeT0kNOFhpTiQuwluXkQlFBs1WhFbknP2_2iDBXeL_WzXCc',
                        imagerySet: 'Aerial',
                        culture: 'en-US',
                        minZoom: 1,
                        maxZoom: 19
                    },
                    
                    initialize: function(options) {
                        L.Util.setOptions(this, options);
                        this._url = null;
                        this._loadMetadata();
                    },
                    
                    _loadMetadata: function() {
                        var _this = this;
                        var cbid = '_bing_metadata_' + L.Util.stamp(this);
                        window[cbid] = function(metadata) {
                            _this._metadataLoaded(metadata);
                            delete window[cbid];
                        };
                        
                        var url = "https://dev.virtualearth.net/REST/v1/Imagery/Metadata/" + 
                            this.options.imagerySet + 
                            "?key=" + this.options.bingMapsKey + 
                            "&include=ImageryProviders&jsonp=" + cbid;
                        
                        var script = document.createElement("script");
                        script.type = "text/javascript";
                        script.src = url;
                        script.id = cbid;
                        document.getElementsByTagName("head")[0].appendChild(script);
                    },
                    
                    _metadataLoaded: function(metadata) {
                        console.log("Bing Metadata:", metadata);
                        if (metadata.statusCode !== 200 || !metadata.resourceSets ||
                            metadata.resourceSets.length < 1 || !metadata.resourceSets[0].resources ||
                            metadata.resourceSets[0].resources.length < 1) {
                            console.error("Bing Metadata error:", metadata.statusCode);
                            // Fallback to OSM tile template
                            this._url = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
                            this.options.attribution = '&copy; OpenStreetMap contributors';
                            L.TileLayer.prototype.initialize.call(this, this._url, {
                                subdomains: ['a', 'b', 'c'],
                                minZoom: this.options.minZoom,
                                maxZoom: this.options.maxZoom,
                                attribution: this.options.attribution
                            });
                            this.fire('ready');
                            return;
                        }
                        
                        var resource = metadata.resourceSets[0].resources[0];
                        if (!resource.imageUrl) {
                            console.error("Bing Metadata error: imageUrl is null, falling back to OSM.");
                            this._url = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
                            this.options.attribution = '&copy; OpenStreetMap contributors';
                            L.TileLayer.prototype.initialize.call(this, this._url, {
                                subdomains: ['a', 'b', 'c'],
                                minZoom: this.options.minZoom,
                                maxZoom: this.options.maxZoom,
                                attribution: this.options.attribution
                            });
                            this.fire('ready');
                            return;
                        }
                        
                        // Replace placeholders in the imageUrl
                        this._url = resource.imageUrl.replace('{culture}', this.options.culture)
                                                     .replace('{s}', '{subdomain}');
                        // Use the correct subdomains with 't' prefix
                        var subdomains = ['t0', 't1', 't2', 't3'];
                        this.options.attribution = "";
                        var providers = resource.imageryProviders || [];
                        for (var i = 0; i < providers.length; i++) {
                            this.options.attribution += providers[i].attribution + ' ';
                        }
                        // Signal that the layer is ready and initialize it with the valid URL
                        this.fire('ready');
                        L.TileLayer.prototype.initialize.call(this, this._url, {
                            subdomains: subdomains,
                            minZoom: this.options.minZoom,
                            maxZoom: this.options.maxZoom,
                            attribution: this.options.attribution
                        });
                    },
                    
                    // Override getTileUrl to compute and replace the {quadkey} placeholder
                    getTileUrl: function(tilePoint) {
                        if (!this._url) {
                            // Until metadata is loaded, return an empty URL
                            return "";
                        }
                        var zoom = this._getZoomForUrl();
                        var quadKey = tileXYToQuadKey(tilePoint.x, tilePoint.y, zoom);
                        return L.Util.template(this._url, {
                            subdomain: this.options.subdomains[tilePoint.x % this.options.subdomains.length],
                            quadkey: quadKey
                        });
                    }
                });
                
                // Helper function to calculate the quadkey
                function tileXYToQuadKey(x, y, zoom) {
                    var quadKey = "";
                    for (var i = zoom; i > 0; i--) {
                        var digit = 0;
                        var mask = 1 << (i - 1);
                        if ((x & mask) !== 0) {
                            digit += 1;
                        }
                        if ((y & mask) !== 0) {
                            digit += 2;
                        }
                        quadKey += digit;
                    }
                    return quadKey;
                }
                
                // Factory function to create a BingLayer instance
                L.bingLayer = function(options) {
                    return new L.BingLayer(options);
                };
                
                // Create the Bing layer but do not add it to the map immediately.
                var bingApiKey = 'AkCDUXwYzM3w36XYcNeT0kNOFhpTiQuwluXkQlFBs1WhFbknP2_2iDBXeL_WzXCc';
                var bingLayer = L.bingLayer({
                    bingMapsKey: bingApiKey,
                    imagerySet: 'Aerial',
                    maxZoom: 19
                });
                
                // When the Bing layer signals that it is ready, add it to the map.
                bingLayer.on('ready', function() {
                    bingLayer.addTo(map);
                });
                
                // Also add an OSM layer as a fallback and for layer control.
                var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors'
                });
                
                var baseMaps = {
                    "Bing Satellite": bingLayer,
                    "OpenStreetMap": osmLayer
                };
                L.control.layers(baseMaps).addTo(map);
                
                // Create the tracking marker using the custom red icon and enable rotation.
                // Note: With the rotated marker plugin loaded, the marker now has setRotationAngle().
                var trackMarker = L.marker([37.7749, -122.4194], { 
                    icon: trackingIcon, rotationAngle: 0 
                }).addTo(map);
                
                // Track line for dynamic updates
                var trackLine = L.polyline([], {color: 'red', weight: 3, opacity: 0.7}).addTo(map);
                var trackPoints = [];
                
                // Create a layer group to hold markers.
                var markersGroup = L.layerGroup().addTo(map);

                // Connect to Qt WebChannel
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    var jspy_bridge = channel.objects.jspy_bridge;
                    
                    // Listen for position updates from Python
                    jspy_bridge.signal_tracker_gps_updated.connect(function(positionJson) {
                        var position = JSON.parse(positionJson);
                        trackMarker.setLatLng([position.latitude, position.longitude]);

                        // trackPoints.push([position.latitude, position.longitude]);
                        // trackLine.setLatLngs(trackPoints);
                        map.panTo([position.latitude, position.longitude]);
                        
                        // Send an acknowledgment back to Python
                        // jspy_bridge.receive_from_js("Position updated");
                    });
                    
                    // Listen for heading updates from Python
                    jspy_bridge.signal_tracker_heading_updated.connect(function(headingJson) {
                        var heading = JSON.parse(headingJson);
                        trackMarker.setRotationAngle(heading.heading);
                    });
                    
                    // Listen for GPS mark addition request from Python
                    jspy_bridge.signal_marks_gps_added.connect(function(positionJson) {
                        var position = JSON.parse(positionJson);
                        var markerPoint = L.circleMarker([position.latitude, position.longitude], {
                            radius: 0.25,              // Radius in pixels 
                            color: 'red',           // Stroke color of the circle
                            fillColor: 'red',       // Fill color
                            fillOpacity: 1          // Fully opaque
                        });
                        markersGroup.addLayer(markerPoint);
                    });
                    
                    // Listen for GPS mark removal request from Python
                    jspy_bridge.signal_marks_gps_removed.connect(function(positionJson) {
                        var position = JSON.parse(positionJson);
                        
                        // find the marker with the same position and remove it
                        markersGroup.eachLayer(function(layer) {
                            if (layer.getLatLng().lat === position.latitude && layer.getLatLng().lng === position.longitude) {
                                markersGroup.removeLayer(layer);
                            }
                        });
                    });
                    
                    // Function to clear all markers (called from Python)
                    window.clearMarkers = function() {
                        markersGroup.clearLayers();
                    };
                    
                    // Function to clear track (called from Python)
                    // window.clearTrack = function() {
                    //     trackPoints = [];
                    //     trackLine.setLatLngs([]);
                    // };
                });
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
        

    def update_gps_position(self, latitude, longitude):
        """Update the GPS position and send it to the JavaScript side"""
        self.jspy_bridge.signal_tracker_gps_updated.emit(json.dumps({
            'latitude': latitude,
            'longitude': longitude,
        }))
        
    
    def update_heading(self, heading):
        """Update the heading and send it to the JavaScript side"""
        self.jspy_bridge.signal_tracker_heading_updated.emit(json.dumps({
            'heading': heading,
        }))
        
        
    def add_gps_position_mark(self, latitude, longitude):
        """Request to add a GPS position mark"""
        self.jspy_bridge.signal_marks_gps_added.emit(json.dumps({
            'latitude': latitude,
            'longitude': longitude,
        }))
        logger.debug("Request to add GPS position mark sent")
        
        
    def remove_gps_position_mark(self, latitude, longitude):
        """Request to clear the GPS position mark"""
        self.jspy_bridge.signal_marks_gps_removed.emit(json.dumps({
            'latitude': latitude,
            'longitude': longitude,
        }))
        logger.debug("Request to clear GPS position mark sent")
        
        
    def reset(self):
        """Reset the map view"""
        # Clear all markers
        self.web_view.page().runJavaScript("clearMarkers();")
        logger.debug("Map view reset")
        
        
        
        
    
