import glob
import json
import os
from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from flask import (Flask, Response, abort, jsonify, redirect, render_template,
                   request)

app = Flask(__name__)

host = 'http://192.168.1.27:5000/'if os.name == 'nt' else 'https://jadwalshalat.glitch.me/'


def month_year():
    nmo = datetime.now()
    nye = datetime.now().year
    months = [(nmo + relativedelta(months=i)).strftime('%B')
              for i in range(12)]
    years = [str(nye + i) for i in range(10)]
    return months, years


def get_provinsi():
    splitter = '\\' if os.name == 'nt' else '/'
    provinsi = []
    for x in glob.glob("provinsi/*.json"):
        provinsi.append(x.split(splitter)[1].split('.')[0].title())
    provinsi = sorted(provinsi)
    provinsi.insert(0, 'Pilih Provinsi')
    return provinsi


def get_kabid(prov, kabko=None):
    kab = []
    if prov.upper() == 'PILIH PROVINSI':
        kab.append('Pilih Kabupaten')
        return kab
    elif kabko is None:
        with open(f"provinsi/{prov.upper()}.json") as f:
            data = json.load(f)
        for x in data:
            kab.append(x['lokasi'].title())
        return kab
    else:
        with open(f"provinsi/{prov.upper()}.json") as f:
            data = json.load(f)
        for x in data:
            if x['lokasi'] == kabko.upper():
                return x['id']


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html'), 403


@app.route('/_update_dropdown')
def update_dropdown():
    if request.referrer != host:
        abort(403)
    # if request.referrer != 'https://jadwalshalat.glitch.me/':
    # abort(403)
    # the value of the first dropdown (selected by the user)
    selprov = request.args.get('selprov', type=str)
    # get values for the second dropdown
    updated_values = get_kabid(selprov)

    # create the value sin the dropdown as a html string
    html_string_selected = ''
    for entry in updated_values:
        html_string_selected += '<option value="{}">{}</option>'.format(
            entry, entry)

    return jsonify(html_string_selected=html_string_selected)


@app.route('/_process_data/<prov>/<kab>/<thn>/<bln>')
def process_data(prov, kab, thn, bln):
    if request.referrer != host:
        abort(403)
    htm = ''
    kabid = get_kabid(prov, kab)
    nbln = f"0{str(datetime.strptime(bln, '%B').month)}" if len(str(datetime.strptime(
        bln, '%B').month)) == 1 else str(datetime.strptime(bln, '%B').month)
    resp = requests.get(
        f"https://api.myquran.com/v1/sholat/jadwal/{kabid}/{thn}/{nbln}")
    data = resp.json()
    if not data['status']:
        return Response('null', mimetype='text/plain')
    jdwl = data["data"]["jadwal"]
    for v in jdwl:
        sjd = '<div class="col s12 m6 l6"><div class="jadwalshalat card z-depth-3"><div class="card-content"><div class="bold margin-b-10">' + \
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
        htm += sjd
    return Response(htm, mimetype='text/plain')


@app.route('/')
def index():
    """
    Initialize the dropdown menues
    """
    provinsi = get_provinsi()
    kab = get_kabid(provinsi[0])
    month, year = month_year()

    return render_template('new.html',
                           bulan=month,
                           tahun=year,
                           province=provinsi,
                           kabko=kab)


@app.route('/test')
def test():
    return render_template('anu.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
