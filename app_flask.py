from flask import Flask, request, jsonify, render_template
from cassandra.cluster import Cluster
import json
import requests
import requests_cache
from datetime import datetime

cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()
requests_cache.install_cache('covid19_api_cache', backend='sqlite', expire_after=36000)
app = Flask(__name__)

covid_url_summary = 'https://api.covid19api.com/summary'
covid_url_country = 'https://api.covid19api.com/countries'

@app.route('/', methods =['GET'])
def home():
    Key = 'Global'
    rows = session.execute("""Select * from covid19.global WHERE Key = '{}'""".format(Key))
    r = rows.one()
    return render_template("index.html", Global_NewConfirmed = r.newconfirmed, Global_NewDeaths = r.newdeaths, Global_NewRecovered = r.newrecovered, Global_TotalConfirmed = r.totalconfirmed, Global_TotalDeaths = r.totaldeaths, Global_TotalRecovered = r.totalrecovered, TimeStamp=r.timestamp)

@app.route('/LoadDatabase', methods=['GET','PUT'])
def load():
    resp = requests.get(covid_url_summary)
    if resp.ok:
        response = resp.json()

        #extracting the relevant variables from the json
        for i in range(0,len(response['Countries'])):

            Countries_data = response['Countries'][i]
            if str(Countries_data['Country']) != "":
                Country = Countries_data['Slug']
                NewConfirmed = Countries_data['NewConfirmed']
                TotalConfirmed = Countries_data['TotalConfirmed']
                NewDeaths = Countries_data['NewDeaths']
                TotalDeaths = Countries_data['TotalDeaths']
                NewRecovered = Countries_data['NewRecovered']
                TotalRecovered = Countries_data['TotalRecovered']

                #storing the data into the sql table
                sql = "UPDATE COVID19.summary SET NewConfirmed= {}, TotalConfirmed= {}, NewDeaths= {}, TotalDeaths= {},NewRecovered= {},TotalRecovered= {} WHERE Country= '{}'"
                sql = sql.format(int(NewConfirmed), int(TotalConfirmed), int(NewDeaths), int(TotalDeaths), int(NewRecovered), int(TotalRecovered), Country)
                session.execute(sql)

        dateTimeObj = datetime.now()
        TimeStamp = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")
        Global_data = response['Global']
        Country_global = 'Global'
        NewConfirmed_global = Global_data['NewConfirmed']
        TotalConfirmed_global = Global_data['TotalConfirmed']
        TotalDeaths_global = Global_data['TotalConfirmed']
        NewDeaths_global = Global_data['NewDeaths']
        TotalDeaths_global = Global_data['TotalDeaths']
        NewRecovered_global = Global_data['NewRecovered']
        TotalRecovered_global = Global_data['TotalRecovered']

        #storing the data into the sql table
        sql = "UPDATE COVID19.global SET NewConfirmed= {}, TotalConfirmed= {}, NewDeaths= {}, TotalDeaths= {},NewRecovered= {},TotalRecovered= {}, TimeStamp='{}' WHERE Key= '{}'"
        sql = sql.format(int(NewConfirmed_global), int(TotalConfirmed_global), int(NewDeaths_global), int(TotalDeaths_global), int(NewRecovered_global), int(TotalRecovered_global), TimeStamp, Country_global)
        session.execute(sql)

    else:
        print(resp.reason)
    return('<h1> The database has been loaded<h1>. <p> <a href = "/summary/country"> Click here</a> to view the records<p>'), 200

@app.route('/external')
def external():
    resp = requests.get(covid_url_summary)
    if resp.ok:
        response = resp.json()
    else:
        print(resp.reason)

    #structuring html string
    data = """<table style="width:100%">
                <tr>
                    <th>Country</th>
                    <th>New Confirmed</th>
                    <th>Total Confirmed</th>
                    <th>New Deaths</th>
                    <th>Total Deaths</th>
                    <th>New Recovered</th>
                    <th>Total Recovered</th>
                </tr>
                """
    #extracting the relevant variables from the json
    for i in range(0,len(response['Countries'])):

        Countries_data = response['Countries'][i]
        if str(Countries_data['Country']) != "":

            Country = Countries_data['Slug']
            NewConfirmed = Countries_data['NewConfirmed']
            TotalConfirmed = Countries_data['TotalConfirmed']
            NewDeaths = Countries_data['NewDeaths']
            TotalDeaths = Countries_data['TotalDeaths']
            NewRecovered = Countries_data['NewRecovered']
            TotalRecovered = Countries_data['TotalRecovered']


            #outputting data in a table
            data += "<tr>\n"
            data += "<td align=\"center\">" + Country + "</td>\n"
            data += "<td align=\"center\">" + str(NewConfirmed) + "</td>\n"
            data += "<td align=\"center\">" + str(TotalConfirmed) + "</td>\n"
            data += "<td align=\"center\">" + str(NewDeaths) + "</td>\n"
            data += "<td align=\"center\">" + str(TotalDeaths) + "</td>\n"
            data += "<td align=\"center\">" + str(NewRecovered) + "</td>\n"
            data += "<td align=\"center\">" + str(TotalRecovered) + "</td>\n"
            data += "</tr>\n"

    data += "</table>"
    return data

@app.route('/summary/country', methods=['GET'])
def summary_country():
    rows = session.execute("""Select * From covid19.summary""")
    result = []
    for r in rows:
        result.append({"country":r.country,"newconfirmed":r.newconfirmed,"totalconfirmed":r.totalconfirmed,"newdeaths":r.newdeaths,"totaldeaths":r.totaldeaths,"newrecovered":r.newrecovered,"totalrecovered":r.totalrecovered})
    return jsonify(result)

@app.route('/summary/global', methods=['GET'])
def summary_global():
    rows = session.execute("""Select * From covid19.global""")
    result = []
    for r in rows:
        result.append({"key":r.key,"newconfirmed":r.newconfirmed,"totalconfirmed":r.totalconfirmed,"newdeaths":r.newdeaths,"totaldeaths":r.totaldeaths,"newrecovered":r.newrecovered,"totalrecovered":r.totalrecovered})
    return jsonify(result)

@app.route('/summary/countrylist', methods=['GET'])
def country_list():
    resp = requests.get(covid_url_country)
    if resp.ok:
        response = resp.json()
    return jsonify(response)

@app.route('/summary/country/<name>',  methods=['GET'])
def country(name):
    rows = session.execute("""Select * from covid19.summary WHERE Country = '{}'""".format(name))
    r = rows.one()
    return render_template("country.html", Country=r.country, NewConfirmed=r.newconfirmed, NewDeaths=r.newdeaths, NewRecovered=r.newrecovered, TotalConfirmed=r.totalconfirmed, TotalDeaths=r.totaldeaths, TotalRecovered=r.totalrecovered)

@app.route('/summary/country',  methods=['POST'])
def create_country():
    session.execute( """INSERT INTO COVID19.summary(Country,NewConfirmed,TotalConfirmed,NewDeaths,TotalDeaths,NewRecovered,TotalRecovered) VALUES('{}', {}, {}, {},{}, {}, {})""".format(request.json['Country'],int(request.json['NewConfirmed']),int(request.json['TotalConfirmed']),int(request.json['NewDeaths']),int(request.json['TotalDeaths']),int(request.json['NewRecovered']),int(request.json['TotalRecovered'])))
    return jsonify({'message': 'created: /summary/country/{}'.format(request.json['Country'])}), 201

@app.route('/summary/country',  methods=['PUT'])
def update_country():
    session.execute("""UPDATE COVID19.summary SET NewConfirmed= {}, TotalConfirmed= {}, NewDeaths= {}, TotalDeaths= {},NewRecovered= {},TotalRecovered= {} WHERE Country= '{}'""".format(int(request.json['NewConfirmed']),int(request.json['TotalConfirmed']),int(request.json['NewDeaths']),int(request.json['TotalDeaths']),int(request.json['NewRecovered']),int(request.json['TotalRecovered']),request.json['Country']))
    return jsonify({'message': 'updated: /summary/country/{}'.format(request.json['Country'])}), 200

@app.route('/summary/country',  methods=['DELETE'])
def delete_country():
    session.execute("""DELETE FROM COVID19.summary WHERE Country= '{}'""".format(request.json['Country']))
    return jsonify({'message': 'deleted: /summary/country/{}'.format(request.json['Country'])}), 200

@app.route('/summary/global',  methods=['POST'])
def create_global():
    session.execute( """INSERT INTO COVID19.global(Key,NewConfirmed,TotalConfirmed,NewDeaths,TotalDeaths,NewRecovered,TotalRecovered) VALUES('{}', {}, {}, {},{}, {}, {})""".format(request.json['Key'],int(request.json['NewConfirmed']),int(request.json['TotalConfirmed']),int(request.json['NewDeaths']),int(request.json['TotalDeaths']),int(request.json['NewRecovered']),int(request.json['TotalRecovered'])))
    return jsonify({'message': 'created: /summary/global/{}'.format(request.json['Key'])}), 201

@app.route('/summary/global',  methods=['PUT'])
def update_global():
    session.execute("""UPDATE COVID19.global SET NewConfirmed= {}, TotalConfirmed= {}, NewDeaths= {}, TotalDeaths= {},NewRecovered= {},TotalRecovered= {} WHERE Key= '{}'""".format(int(request.json['NewConfirmed']),int(request.json['TotalConfirmed']),int(request.json['NewDeaths']),int(request.json['TotalDeaths']),int(request.json['NewRecovered']),int(request.json['TotalRecovered']),request.json['Key']))
    return jsonify({'message': 'updated: /summary/global/{}'.format(request.json['Key'])}), 200

@app.route('/summary/global',  methods=['DELETE'])
def delete_global():
    session.execute("""DELETE FROM COVID19.global WHERE Key= '{}'""".format(request.json['Key']))
    return jsonify({'message': 'deleted: /summary/global/{}'.format(request.json['Key'])}), 200

if __name__ == "__main__":
    context = ('cert.pem','key.pem')
    app.run(host='0.0.0.0',port=443,ssl_context=context)
