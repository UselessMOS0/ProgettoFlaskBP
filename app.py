from flask import Flask, render_template, request, Response, redirect, url_for, make_response, session 
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

credenziali = pd.read_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv')
regioni = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/Regioni.zip")

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['Username']
        password = request.form['Password']
        if username in credenziali.Username and password == credenziali.Password:
            session['username'] = username 
            return redirect(url_for('home'))
            


@app.route("/registrazione", methods=['GET','POST'])
def registrazione():
    if request.method == 'GET':
        return render_template("registrazione.html")
    else:
        username = request.form['Username']
        password = request.form['Password']
        print(username,password)
        utente = {"Username": username,"Password":password}
        print(utente)
        print(credenziali)
        credenziali.append(utente,ignore_index=True)
        credenziali.to_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv',index=False)
        
        return redirect(url_for('login'))
        

#--------------------------------------------------------------------
#--------------------------------------------------------------------

# ROUTE HOME DEL SITO 
# ROUTE HOME DEL SITO

@app.route("/", methods=["GET"])
def home():
    if not session.get('username'):
        return redirect(url_for('login'))

    return render_template("home.html",username = session['username'])

#--------------------------------------------------------------------
#--------------------------------------------------------------------

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)