from sectional.models import CategorySectional
from sectional.models import Configuration, Color
from sectional.services import DataService

from flask import Flask, jsonify, send_from_directory, request, abort
from enum import Enum
from datetime import datetime
import json

sectional = CategorySectional()

app = Flask(__name__, static_url_path='')
configuration = Configuration()


@app.route('/<path:path>.js', methods=['GET'])
def static_proxy(path):
    print("static_proxy", path)
    return send_from_directory('html', "{}.js".format(path))


@app.route('/')
def root():
    print("root")
    return send_from_directory('html', 'index.html')


@app.route('/<path>')
def other_path(path):
    print("path {}".format(path))
    return send_from_directory('html', 'index.html')


def json_default(obj):
    if ('to_json' in dir(obj)):
        return obj.to_json()

    if (type(obj) is datetime):
        return obj.isoformat()

    if (isinstance(obj, Enum)):
        return obj.value


@app.route('/api/airports')
def airports():
    return json.dumps(sectional.airports, default=json_default)

@app.route('/api/pixelcount', methods=['POST'])
def set_led_count():
    print(request.json)
    configuration.pixelcount = int(request.json['pixelcount'])
    configuration.save_config()
    return jsonify({'pixelcount': configuration.pixelcount})

@app.route('/api/pixelcount', methods=['GET'])
def get_led_count():
    return jsonify({'pixelcount': configuration.pixelcount})

@app.route('/api/selftest', methods=['POST'])
def run_self_test():
    sectional.run_self_test()
    return jsonify({'status': 'OK'})

@app.route('/api/pixel/<index>', methods=['GET'])
def get_airport_for_pixel(index):
    icao_airport_code = configuration.get_airport_for_pixel(index)
    return jsonify({ 'icao_airport_code': icao_airport_code })

@app.route('/api/pixel/<index>', methods=['POST'])
def set_airport_for_pixel(index): 
    icao_airport_code = request.json['icao_airport_code']
    configuration.set_airport_for_pixel(index, icao_airport_code)
    configuration.save_config()
    return jsonify({ 'icao_airport_code': icao_airport_code })

@app.route('/api/setpixel/<index>', methods=['POST'])
def set_led(index):
    color = Color(request.json['color'])
    sectional.set_led(int(index), color)
    return jsonify({'pixel_index': index, 'color': color.rgb})

@app.route('/api/clearpixels', methods=['POST'])
def clear_pixels():
    for idx in range(configuration.pixelcount):
        sectional.set_led(int(idx), Color.BLACK())
    return jsonify({'status': 'OK'})

@app.route('/api/setup_complete', methods=['POST'])
def setup_complete(): 
    setup_complete = request.json['setup_complete']
    configuration.setup_complete(setup_complete)
    configuration.save_config()
    sectional.start()

@app.route('/api/metar/<airport>', methods=['GET'])
def get_metar(airport):
    try:
        metar = DataService.obtain_metars([airport])
        if (len(metar) > 0):
            return jsonify({ 'metar': metar[0].metar, 'icao_airport_code': airport })
        else:
            return jsonify({ 'status': 'ERROR', 'message': 'METAR could not be obained for {}'.format(airport)}), 404
    except Exception:
            return jsonify({ 'status': 'ERROR', 'message': 'METAR could not be obained for {}'.format(airport)}), 500

@app.route('/api/refreshmetars', methods=['POST'])
def refresh_metars():
    sectional.refresh_metars()
    return jsonify({"status": "OK"})

@app.route('/api/refreshsunrise', methods=['POST'])
def refresh_sunrise():
    sectional.refresh_sunrise()
    return jsonify({"status": "OK"})

@app.route('/api/airportsearch', methods=['GET'])
def airport_search():
    q = request.args['q']
    airports = DataService.airportsearch(q)
    return jsonify(airports)
