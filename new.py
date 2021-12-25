import glob
import json
import os
from datetime import datetime

import requests
from flask import Flask, Response, abort, render_template, request

app = Flask(__name__)

host = ['http://192.168.1.117:5000/'] if os.name == 'nt' else ['https://jadwalshalat.glitch.me/', 'https://jdwlshalat.herokuapp.com/']


def get_kabid(kabko=None):
    with open('static/kabko.json') as f:
        data = json.load(f)
    if kabko is not None:
        for x in data:
            if x['lokasi'] == kabko.upper():
                return x['id']
    else:
        kab = []
        for x in data:
            kab.append(x['lokasi'].title())
        return sorted(kab)


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html'), 403


@app.route('/_process_data/<kab>/<thn>/<bln>/<tgl>')
def process_data(kab, thn, bln, tgl):
    if request.referrer not in host:
        abort(403)
    html = ''
    kabid = get_kabid(kab)
    nbln = f"0{str(datetime.strptime(bln, '%B').month)}" if len(str(datetime.strptime(
        bln, '%B').month)) == 1 else str(datetime.strptime(bln, '%B').month)
    data = requests.get(
        f"https://api.myquran.com/v1/sholat/jadwal/{kabid}/{thn}/{nbln}").json()

    if not data['status']:
        return Response('null', mimetype='text/plain')

    #v = data["data"]["jadwal"]
    for v in data["data"]["jadwal"]:
        div = '4" id="currentjdwl">' if v["date"].split('-')[2] == tgl else '1">'
        sjd = '<div class="col s12 m6 l6"><div class="jadwalshalat card z-depth-' + div + '<div class="card-content"><div class="bold margin-b-10">' + \
            v["tanggal"] + \
            '</div><div class="row"><div class="col s4 m4 l4 valign-wrapper"><i class="icon icon-imsak"></i><div class="waktushalat"><span class="title lime-text text-darken-4">IMSAK </span><span class="waktu bold">' + \
            v["imsak"] + \
            '</span></div></div><div class="col s4 m4 l4 valign-wrapper"><i class="icon icon-subuh"></i><div class="waktushalat"><span class="title lime-text text-darken-4">SUBUH </span><span class="waktu bold">' + \
            v["subuh"] + \
            '</span></div></div><div class="col s4 m4 l4 valign-wrapper"><i class="icon icon-terbit"></i><div class="waktushalat"><span class="title lime-text text-darken-4">TERBIT </span><span class="waktu bold">' + \
            v["terbit"] + \
            '</span></div></div><div class="col s4 m4 l4 valign-wrapper"><i class="icon icon-dhuha"></i><div class="waktushalat"><span class="title lime-text text-darken-4">DUHA </span><span class="waktu bold">' + \
            v["dhuha"] + \
            '</span></div></div><div class="col s4 m4 l4 valign-wrapper"><i class="icon icon-dzuhur"></i><div class="waktushalat"><span class="title lime-text text-darken-4">ZUHUR </span><span class="waktu bold">' + \
            v["dzuhur"] + \
            '</span></div></div><div class="col s4 m4 l4 valign-wrapper"><i class="icon icon-ashar"></i><div class="waktushalat"><span class="title lime-text text-darken-4">ASAR </span><span class="waktu bold">' + \
            v["ashar"] + \
            '</span></div></div><div class="col s4 m4 l4 valign-wrapper"><i class="icon icon-maghrib"></i><div class="waktushalat"><span class="title lime-text text-darken-4">MAGRIB </span><span class="waktu bold">' + \
            v["maghrib"] + \
            '</span></div></div><div class="col s4 m4 l4 valign-wrapper"><i class="icon icon-isya"></i><div class="waktushalat"><span class="title lime-text text-darken-4">ISYA\' </span><span class="waktu bold">' + \
            v["isya"] + \
            '</span></div></div></div></div></div></div> '
        html += sjd
    return Response(html, mimetype='text/plain')


@app.route('/')
def index():
    return render_template('new.html',
                           kabko=get_kabid())


if __name__ == '__main__':
    app.run(debug=True) #ssl_context='adhoc'
