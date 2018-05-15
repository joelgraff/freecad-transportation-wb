# -*- coding: utf-8 -*-

''' 
    TransverseMercator:
    "author": "Vladimir Elistratov <vladimir.elistratov@gmail.com> and gtoonstra",
    "wiki_url": "https://github.com/vvoovv/blender-geo/wiki/Import-OpenStreetMap-(.osm)",
    "tracker_url": "https://github.com/vvoovv/blender-geo/issues",
'''

import FreeCAD
import os
import math

# see conversion formulas at
# http://en.wikipedia.org/wiki/Transverse_Mercator_projection
# and
# http://mathworld.wolfram.com/MercatorProjection.html

class TransverseMercator:
    radius = 6378137
    radius = 6378137000
    
    def __init__(self, **kwargs):
        # setting default values
        self.lat = 0 # in degrees
        self.lon = 0 # in degrees
        self.k = 1.0 # scale factor
        
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])
        self.latInRadians = math.radians(self.lat)
	print "lat in radinans",self.latInRadians

    def fromGeographic(self, lat, lon):
        lat = math.radians(lat)
        lon = math.radians(lon-self.lon)
        B = math.sin(lon) * math.cos(lat)
        x = 0.5 * self.k * self.radius * math.log((1+B)/(1-B))
        y = self.k * self.radius * ( math.atan(math.tan(lat)/math.cos(lon)) - self.latInRadians )
        return (x,y)

    def toGeographic(self, x, y):
        x = x/(self.k * self.radius)
        y = y/(self.k * self.radius)
        D = y + self.latInRadians
        lon = math.atan(math.sinh(x)/math.cos(D))
        lat = math.asin(math.sin(D)/math.cosh(x))
#        print(x,y,lat,lon)

        lon = self.lon + math.degrees(lon)
        lat = math.degrees(lat)
        return (lat, lon)





def getpos(latc,lonc,lat,lon):
    '''calculate the xy position for lat lon relative to latc,lonc'''

    tm=TransverseMercator()
    tm.lat=latc
    tm.lon=lonc
    tm.latInRadians = math.radians(latc)

    center=tm.fromGeographic(latc,lonc)

    ll=tm.fromGeographic(lat,lon)
    pos=FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1])

    print ("Distance between")
    print (latc,lonc)
    print (lat,lon)
    print ( "in km ",pos.Length/1000000)
    #pos *= 0.001
    #pos *= 0.01

    return pos


def getlatlon(latc,lonc,x,y):

    tm=TransverseMercator()
    tm.lat=latc
    tm.lon=lonc
    tm.latInRadians = math.radians(latc)

    lat,lon=tm.toGeographic(x,y)

    return lat,lon

'''
v=getpos(51.0,15.0,52.0,15.0)
v2  = v*0.000001
print v2

getlatlon(51.0,15.0,v.x,v.y)
'''
