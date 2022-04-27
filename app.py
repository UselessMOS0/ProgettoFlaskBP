from flask import Flask, render_template, request, Response, redirect, url_for, make_response, set_cookie
app = Flask(__name__)

import io
import pandas as pd
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ROUTE DEL LOGIN E DELLA REGISTRAZIONE ROUTE DEL LOGIN E DELLA REGISTRAZIONE 
# ROUTE DEL LOGIN E DELLA REGISTRAZIONE ROUTE DEL LOGIN E DELLA REGISTRAZIONE 

credenziali = pd.read_csv('/workspace/ProgettoFlaskBP/static/csv/credenziali.csv')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['Username']
        password = request.form['Password']

        if username in credenziali.Username and password == credenziali[credenziali]:
            resp = make_response(render_template('home.html'))
            resp.set_cookie('username',username)
            resp.set_cookie('password',password)

@app.route("/registrazione", methods=['GET','POST'])
def registrazione():
    if request.method == 'GET':
     return render_template("registrazione.html")

#--------------------------------------------------------------------
#--------------------------------------------------------------------

# ROUTE HOME DEL SITO 
# ROUTE HOME DEL SITO

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

#--------------------------------------------------------------------
#--------------------------------------------------------------------

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)