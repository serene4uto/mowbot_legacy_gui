import sys
import json
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QShortcut
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QKeySequence

# Interceptor to set a valid Referer header for Bing Maps requests
class BingRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if "dev.virtualearth.net" in url:
            # Set the Referer header to something Bing accepts.
            info.setHttpHeader(b"Referer", b"https://www.bing.com")

class GPSBridge(QObject):
    """Bridge between Python and JavaScript for GPS updates"""
    positionChanged = pyqtSignal(str)
    
    @pyqtSlot(str)
    def receive_from_js(self, message):
        print(f"Message from JS: {message}")

class GPSSimulator:
    """Simulates GPS data by iterating through predefined waypoints and calculates heading for orientation"""
    def __init__(self):
        # Define waypoints
        self.waypoints = [
            {'latitude': 37.7749, 'longitude': -122.4194},
            {'latitude': 37.7759, 'longitude': -122.4184},
            {'latitude': 37.7769, 'longitude': -122.4174},
            {'latitude': 37.7779, 'longitude': -122.4164}
        ]
        self.current_index = 0
        # Start at the first waypoint
        self.latitude = self.waypoints[0]['latitude']
        self.longitude = self.waypoints[0]['longitude']
        self.speed = 0
        self.tracking = False
        self.heading = 0  # in degrees
        
    def start_tracking(self):
        self.tracking = True
        
    def stop_tracking(self):
        self.tracking = False

    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        # Calculate bearing between two points in degrees.
        dLon = math.radians(lon2 - lon1)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        y = math.sin(dLon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad)*math.sin(lat2_rad) - math.sin(lat1_rad)*math.cos(lat2_rad)*math.cos(dLon)
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360

    def get_position(self):
        if self.tracking:
            previous_lat = self.latitude
            previous_lon = self.longitude
            # Advance to the next waypoint (looping after the last one)
            self.current_index = (self.current_index + 1) % len(self.waypoints)
            waypoint = self.waypoints[self.current_index]
            self.latitude = waypoint['latitude']
            self.longitude = waypoint['longitude']
            self.speed = 3.5  # constant speed for simulation
            self.heading = self.calculate_bearing(previous_lat, previous_lon, self.latitude, self.longitude)
        else:
            self.heading = 0
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'tracking': self.tracking,
            'heading': self.heading
        }

class GPSTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPS Tracker with Bing Satellite Imagery")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize GPS simulator
        self.gps = GPSSimulator()
        
        # Setup UI
        self.init_ui()
        
        # Create a bridge for Python-JavaScript communication
        self.bridge = GPSBridge()
        
        # Setup web channel
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        # Load the HTML with Leaflet map, Bing layer, waypoints,
        # and a tracking marker that rotates based on heading.
        self.load_map()
        
        # Timer for GPS updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1000)  # Update every second

        # Setup F12 shortcut to open developer tools
        self.dev_shortcut = QShortcut(QKeySequence("F12"), self)
        self.dev_shortcut.activated.connect(self.open_dev_tools)
    
    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # Web view for the map
        self.web_view = QWebEngineView()
        
        # Info section
        info_layout = QHBoxLayout()
        self.lat_label = QLabel("Latitude: 0.000000")
        self.lon_label = QLabel("Longitude: 0.000000")
        self.speed_label = QLabel("Speed: 0.0 km/h")
        self.tracking_label = QLabel("Tracking: Off")
        
        info_layout.addWidget(self.lat_label)
        info_layout.addWidget(self.lon_label)
        info_layout.addWidget(self.speed_label)
        info_layout.addWidget(self.tracking_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Tracking")
        self.start_button.clicked.connect(self.start_tracking)
        self.stop_button = QPushButton("Stop Tracking")
        self.stop_button.clicked.connect(self.stop_tracking)
        self.stop_button.setEnabled(False)
        self.clear_button = QPushButton("Clear Track")
        self.clear_button.clicked.connect(self.clear_track)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        
        layout.addWidget(self.web_view, stretch=8)
        layout.addLayout(info_layout)
        layout.addLayout(button_layout)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
    
    def load_map(self):
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
            <script src="https://unpkg.com/leaflet-rotatedmarker@0.2.0/leaflet.rotatedMarker.min.js"></script>
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
                var map = L.map('map').setView([37.7749, -122.4194], 15);
                
                // Define the tracking marker icon (red arrow)
                var trackingIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                
                // Define waypoints (blue circle markers) array
                var waypoints = [
                    [37.7749, -122.4194],
                    [37.7759, -122.4184],
                    [37.7769, -122.4174],
                    [37.7779, -122.4164]
                ];
                // Add blue circle markers for each waypoint with a popup label
                for (var i = 0; i < waypoints.length; i++) {
                    L.circleMarker(waypoints[i], {radius: 6, color: 'blue', fillColor: 'blue', fillOpacity: 1})
                        .addTo(map)
                        .bindPopup("Waypoint " + (i+1));
                }
                // Connect waypoints with a dashed polyline
                L.polyline(waypoints, {color: 'blue', weight: 2, dashArray: '5, 5'}).addTo(map);
                
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
                var marker = L.marker([37.7749, -122.4194], { icon: trackingIcon, rotationAngle: 0 }).addTo(map);
                
                // Track line for dynamic updates
                var trackLine = L.polyline([], {color: 'red', weight: 3, opacity: 0.7}).addTo(map);
                var trackPoints = [];
                
                // Connect to Qt WebChannel
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    var bridge = channel.objects.bridge;
                    
                    // Listen for position updates from Python
                    bridge.positionChanged.connect(function(positionJson) {
                        var position = JSON.parse(positionJson);
                        marker.setLatLng([position.latitude, position.longitude]);
                        marker.setRotationAngle(position.heading);
                        if (position.tracking) {
                            trackPoints.push([position.latitude, position.longitude]);
                            trackLine.setLatLngs(trackPoints);
                            map.panTo([position.latitude, position.longitude]);
                        }
                        // Send an acknowledgment back to Python
                        bridge.receive_from_js("Position updated");
                    });
                    
                    // Function to clear track (called from Python)
                    window.clearTrack = function() {
                        trackPoints = [];
                        trackLine.setLatLngs([]);
                    };
                });
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
    
    def update_position(self):
        """Get current position and send to JavaScript"""
        position = self.gps.get_position()
        self.lat_label.setText(f"Latitude: {position['latitude']:.6f}")
        self.lon_label.setText(f"Longitude: {position['longitude']:.6f}")
        self.speed_label.setText(f"Speed: {position['speed']:.1f} km/h")
        self.bridge.positionChanged.emit(json.dumps(position))
    
    def start_tracking(self):
        self.gps.start_tracking()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.tracking_label.setText("Tracking: On")
    
    def stop_tracking(self):
        self.gps.stop_tracking()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.tracking_label.setText("Tracking: Off")
    
    def clear_track(self):
        """Execute JavaScript to clear the dynamic track"""
        self.web_view.page().runJavaScript("clearTrack();")
    
    def open_dev_tools(self):
        """Open the developer tools window for the web view."""
        self.dev_view = QWebEngineView()
        self.dev_view.setWindowTitle("Dev Tools")
        self.web_view.page().setDevToolsPage(self.dev_view.page())
        self.dev_view.show()
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Install the request interceptor on the default profile using the thread-safe setter.
    profile = QWebEngineProfile.defaultProfile()
    # profile.setUrlRequestInterceptor(BingRequestInterceptor())
    tracker = GPSTracker()
    tracker.show()
    sys.exit(app.exec_())
