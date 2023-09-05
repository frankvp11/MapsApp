from kivy.lang import Builder
from plyer import gps
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import mainthread
from kivy.utils import platform
from math import radians, sin, asin, cos, sqrt
from kivy_garden.mapview import MapView

kv = '''

BoxLayout:
    orientation: 'vertical'

    #:import MapSource kivy_garden.mapview.MapSource
    MapView:
        
        lat:  43.266660
        lon:  -79.918103
        zoom: 13
        MapMarkerPopup:
            lat: app.lat
            lon: app.lon
            popup_size: dp(230), dp(130)


    Label:
        text: app.gps_location

    Label:
        text: app.gps_status
    Label:
        text: app.distance_travelled
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        padding: '4dp'

        ToggleButton:
            text: 'Start' if self.state == 'normal' else 'Stop'
            on_state:
                app.start(1000, 0) if self.state == 'down' else \
                app.stop()
'''


class GpsTest(App):

    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')
    distance_travelled = StringProperty()
    lat = NumericProperty(0)
    distance = 0.0
    lon = NumericProperty(0)
    previous_coords = ()
    coordinates = []
    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)


    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

        return Builder.load_string(kv)

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        ##
        if (kwargs['accuracy'] < 20 or kwargs['accuracy'] > 100):
            return
        else:
            self.lat = kwargs['lat']
            self.lon = kwargs['lon']
            # self.mapview.center_on(self.lat, self.lon)
            # self.mapview.remove_marker()
            # self.mapview.add_marker(self.lat, self.lon)
            if not self.previous_coords:
                self.previous_coords  = (kwargs['lat'], kwargs['lon'])
            self.distance += self.calculate_distance(self.previous_coords, (kwargs['lat'], kwargs['lon']))
            self.distance_travelled = "Distance"  + str(self.distance)
            self.previous_coords = (kwargs['lat'], kwargs['lon'])
            ##
            self.gps_location = '\n'.join([
                '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(1000, 0)
        pass

    def calculate_distance(self, coord1, coord2):
        lon1, lat1, lon2, lat2 = map(radians, [coord1[0], coord1[1], coord2[0], coord2[1]])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371*1000 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        return c * r

if __name__ == '__main__':
    GpsTest().run()
