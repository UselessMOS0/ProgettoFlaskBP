from flask import Flask, render_template, request, Response, redirect, url_for, make_response, session 
from flask_session import Session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

import io
import pandas as pd
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import folium

#! ROUTE DEL LOGIN E DELLA REGISTRAZIONE ROUTE DEL LOGIN E DELLA REGISTRAZIONE 
#! ROUTE DEL LOGIN E DELLA REGISTRAZIONE ROUTE DEL LOGIN E DELLA REGISTRAZIONE 

credenziali = pd.read_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv')
regioni = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/Regioni.zip").to_crs(epsg=4326)
province = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/Province.zip")
comuni = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/Comuni.zip")
popolazione = pd.read_csv("/workspace/ProgettoFlaskBP/static/Files/popolazione.csv")
covid = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv")

print(regioni)


print(popolazione)
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form['Username']
        password = request.form['Password']
        print('username =',username ,'password =', password)
        print(credenziali)

        for index,c in credenziali.iterrows():
            if username == c["Username"] and password == c["Password"]:
                session['username'] = username
                return redirect(url_for('home'))  
            
        return redirect(url_for('login'))
            

@app.route("/registrazione", methods=['GET','POST'])
def registrazione():
    if request.method == 'GET':
        return render_template("registrazione.html")
    elif request.method == "POST":
        global credenziali
        username = request.form['Username'].replace(" ", "")
        password = request.form['Password']

        if username in credenziali["Username"].tolist():
            return redirect(url_for("registrazione"))
        else:
            utente = {"Username": username,"Password":password}
            credenziali = credenziali.append(utente,ignore_index=True)
            credenziali.to_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv',index=False)      
            return redirect(url_for('login'))

#!--------------------------------------------------------------------
#!--------------------------------------------------------------------

#! ROUTE DEL LOGOUT
#! ROUTE DEL LOGOUT

@app.route("/logout")
def logout():
    session["username"] = None
    return redirect(url_for('home'))

#!--------------------------------------------------------------------
#!--------------------------------------------------------------------

#? ROUTE HOME DEL SITO 
#? ROUTE HOME DEL SITO

@app.route("/", methods=["GET"])
def home():
    if not session.get('username'):
        return redirect(url_for('login'))

    return render_template("home.html",username = session['username'])

#?--------------------------------------------------------------------
#?--------------------------------------------------------------------


# ROUTE RICERCA INFORMAZIONI ROUTE RICERCA INFORMAZIONI
# ROUTE RICERCA INFORMAZIONI ROUTE RICERCA INFORMAZIONI



@app.route("/info", methods=["GET"])
def info():
    if not session.get('username'):
        return redirect(url_for('login'))
    
    m = folium.Map(location=[41,12], zoom_start=6.4)

    for reg in regioni.DEN_REG.tolist():
        folium.Marker([regioni[regioni.DEN_REG == reg].centroid.y,regioni[regioni.DEN_REG == reg].centroid.x], popup=reg).add_to(m)

    
    return m._repr_html_()


#?--------------------------------------------------------------------
#?--------------------------------------------------------------------

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)