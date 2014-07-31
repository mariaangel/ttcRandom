# ************************************************
#
# ** NAME - TTC departure times
# **
# ** author   M. Angel Marquez-Andrade
# ** date     30 July 2014
# ** purpose  Retrieving live data on the
#             current position of TTC vehicles
#             closest to the current user to
#             return approximate departure times
#             at a specific stop, based on data
#             from myttc.ca and Nextbus.com
#
# ************************************************




from flask import Flask, render_template, request, jsonify
from urllib.request import urlopen
from json import loads
from xml.dom.minidom import parse
import random

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('welcome.html')

torontoLocations = [(43.766535,-79.493961),(43.774112, -79.500924),(43.749335, -79.462011),(43.786212, -79.474715)]

#return the TTC stops closest to the user
@app.route('/getStops')
def getStops():

    if 'lat' in request.args and 'lon' in request.args:
        apiUrl = 'http://myttc.ca/near/'
        apiParam = request.args['lat'] + ',' + request.args['lon']
        outputFormat = '.json'
        response = urlopen(apiUrl + apiParam + outputFormat)
        decoded = decode(response)
        dicJson = {}
        if decoded['locations']:
            decoded = decoded['locations'][0]['stops']
            for stop in decoded:
                dicJson[stop['uri']] = [stop['lat'], stop['lng']]
            return jsonify( dicJson )
        else:
            location = random.choice(torontoLocations);
            apiParam = str(location[0]) + ',' + str(location[1])
            response = urlopen(apiUrl + apiParam + outputFormat)
            decoded = decode(response)
            decoded = decoded['locations'][0]['stops']
            for stop in decoded:
                dicJson[stop['uri']] = [stop['lat'], stop['lng']]
            return jsonify( dicJson )
    else:
        return jsonify( { "error": "Cannot get stops from myttc.ca" } )

#return departure times at the stop
@app.route('/getDeparture', methods=['POST'])
def getDeparture():
    if request.method == 'POST':
        s = request.form['stop']
        lat = float(request.form[s])

        # Get buses that stop at this location (to associate myttc.ca and Nextbus.com)
        apiUrl = 'http://myttc.ca/'
        apiParam = s
        outputFormat = '.json'
        response = urlopen(apiUrl + apiParam + outputFormat)
        decoded = decode(response)
        decoded = decoded['stops'][0]['routes'][0]['uri']
        vehicle = decoded.split('_')

        # Get id of the stop according to Nextbus.com
        apiUrl = 'http://webservices.nextbus.com/service/publicXMLFeed?'
        apiParam = 'command=routeConfig&a=ttc&r=' + vehicle[0]
        response = urlopen(apiUrl + apiParam)
        xmldoc = parse(response)
        itemlist = xmldoc.getElementsByTagName('stop')
        minStop = itemlist[0].getAttribute('stopId')
        minSub = abs(lat - float(itemlist[0].getAttribute('lat')))
        for stop in itemlist:
            if stop.getAttribute('lat') and abs(lat - float(stop.getAttribute('lat'))) < minSub:
                minStop = stop.getAttribute('stopId')
                minSub = abs(lat - float(stop.getAttribute('lat')))

        #Get list of departures at that stop
        apiParam = 'command=predictions&a=ttc&stopId=' + minStop
        response = urlopen(apiUrl + apiParam)
        xmldoc = parse(response)
        itemlist = xmldoc.getElementsByTagName('direction')
        departures = {}
        if itemlist:
            for bus in itemlist:
                title = bus.getAttribute('title')
                departures[title] = []
                predictions = bus.getElementsByTagName('prediction')
                for p in predictions:
                    departures[title].append(p.getAttribute('minutes'))
        else:
            return render_template( 'departure.html', error='No buses at this stop' )
        return render_template( 'departure.html', d=departures )

def decode(r):
    charset = r.info().get_param('charset', 'utf8')
    data = r.read()
    decoded = loads(data.decode(charset))
    return decoded

