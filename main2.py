from kivy.lang import Builder
from plyer import gps
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import mainthread
from kivy.utils import platform
from math import radians, sin, asin, cos, sqrt
from kivy_garden.mapview import MapView, MapMarker
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class GpsTest(App):


    def init(self):
        self.distance_travelled = ""
        self.previous_coords = ()
        self.distance = 0
        

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
        self.init()
        self.gps_status_label = Label(text="")

        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status_label.text = 'GPS is not implemented for your platform'

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()


        layout = BoxLayout(orientation="vertical")

        self.mapview = MapView(lat=0, lon=0, zoom=13)
        self.marker = MapMarker(lat=0, lon=0)
        # self.mapview.add_widget(marker)
        self.mapview.add_marker(self.marker)
        layout.add_widget(self.mapview)

        # Define the labels
        self.gps_location_label = Label(text="")
        # self.bind(self.gps_location_label.text, self.gps_location)

        # self.gps_status_label = Label(text="")
        # self.bind(gps_status_label.text, self.gps_status)
        
        self.distance_travelled_label = Label(text=str(self.distance_travelled))
        # self.bind(self.distance_travelled_label.text, self.distance_travelled)

        layout.add_widget(self.gps_location_label)
        layout.add_widget(self.gps_status_label)
        layout.add_widget(self.distance_travelled_label)

        # Define the start/stop button
        self.button = Button(text="Start")
        self.button.bind(on_press=self.button_callback)
        layout.add_widget(self.button)


        return layout
    def button_callback(self, instance):
        if (instance.state == "down"):
            self.start(1000, 0)
        else:
            self.stop()

        



    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)
        return

    def stop(self):
        gps.stop()
        return

    @mainthread
    def on_location(self, **kwargs):
        ##
        if (kwargs['accuracy'] < 40 or kwargs['accuracy'] > 100):
            return
        else:
            self.lat = kwargs['lat']
            self.lon = kwargs['lon']
            if not self.previous_coords:
                self.previous_coords  = (kwargs['lat'], kwargs['lon'])
            self.distance += self.calculate_distance(self.previous_coords, (kwargs['lat'], kwargs['lon']))
            self.distance_travelled_label.text = "Distance"  + str(self.distance)
            self.previous_coords = (kwargs['lat'], kwargs['lon'])
            self.mapview.center_on(kwargs['lat'], kwargs['lon'])
            self.mapview.remove_marker(self.marker)
            self.marker = MapMarker(lat=kwargs['lat'], lon=kwargs['lon'])
            self.mapview.add_marker(self.marker)

            self.gps_location_label = '\n'.join([
                '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_status(self, stype, status):
        self.gps_status_label = 'type={}\n{}'.format(stype, status)

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
