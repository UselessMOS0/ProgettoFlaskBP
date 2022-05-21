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
import random as rnd

#! ROUTE DEL LOGIN E DELLA REGISTRAZIONE ROUTE DEL LOGIN E DELLA REGISTRAZIONE 
#! ROUTE DEL LOGIN E DELLA REGISTRAZIONE ROUTE DEL LOGIN E DELLA REGISTRAZIONE 

credenziali = pd.read_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv')
mondo =  gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')).to_crs(epsg=4326)
regioni = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/Regioni.zip").to_crs(epsg=4326)
province = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/Province.zip").to_crs(epsg=4326)
comuni = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/Comuni.zip")
popolazione = pd.read_csv("/workspace/ProgettoFlaskBP/static/Files/popolazione.csv")
covid = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv")

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
    '''
    m = folium.Map(location=[41,12], zoom_start=6.4)

    for reg in regioni.DEN_REG.tolist():
        url = str(url_for("inforeg", regione=reg))
        folium.Marker([regioni[regioni.DEN_REG == reg].centroid.y,regioni[regioni.DEN_REG == reg].centroid.x], popup=f"<a href={url}>{reg}</a>").add_to(m)
'''

    folinfo = folium.Map(location=[41,12], max_bounds=True, zoom_start=7 , min_zoom=4)
    

    for _, r in regioni.iterrows():
        url = str(url_for("inforeg", regione=r['DEN_REG']))
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.0000000000000000000000000000000000000000000000001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                        style_function=lambda x: {'fillColor': 'orange'})
        folium.Popup(f"<a href={url}>{r['DEN_REG']}</a>"
        ).add_to(geo_j)
        geo_j.add_to(folinfo)
    
    return folinfo._repr_html_()



@app.route("/info/<regione>", methods=["GET"])
def inforeg(regione):
    return render_template("info.html", regione=regione)

#?--------------------------------------------------------------------
#?--------------------------------------------------------------------


#? ROUTE MINIGIOCO MONDO ROUTE MINIGIOCO MONDO
#? ROUTE MINIGIOCO MONDO ROUTE MINIGIOCO MONDO


@app.route("/game", methods=["GET"])
def game():
    return render_template("mod.html")

@app.route("/game/mondo", methods=["GET"])
def gamemondo():
    rndpaese = rnd.randrange(len(mondo)-1)
    rndpaese = mondo[mondo.index == rndpaese].name.to_string(index=False)

    folmondo = folium.Map(location=[19.14,-12.56], max_bounds=True, zoom_start=3 , min_zoom=2.8, tiles='stamenwatercolor')
    

    for _, r in mondo.iterrows():
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.0000000000000000000000000000000000000000000000001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j)
        folium.Popup(f"<form action='/game/mondo/conferma' method='POST'> <input type='hidden' name='paese' value='{r['name']}' > <input type='hidden' name='random' value='{rndpaese}' > <input type='submit' value='Conferma' style='font-family: sans-serif;border-radius: 10px;height: 35px;width: 100px;font-size: 18px;font-weight: bold;'> </form>"
        ).add_to(geo_j)
        geo_j.add_to(folmondo)

    return render_template("game.html",titolo = "MINIGIOCO SUGLI STATI DEL MONDO" , map = folmondo._repr_html_(),indovina = "Indovina lo stato:" , rndnome = rndpaese)

@app.route("/game/mondo/conferma", methods=["POST"])
def conferma_mondo():
    paese = request.form["paese"]
    random = request.form["random"]
    risultato = "No, la risposta è sbagliata"
    immagine = "/static/img/errore.png"
    if paese == random:
        risultato = "La risposta è corretta"
        immagine = "/static/img/giusto.png"
    return render_template("conferma.html", risposta=paese, risultato= risultato, immagine = immagine)


#?--------------------------------------------------------------------
#?--------------------------------------------------------------------


#? ROUTE MINIGIOCO PROVINCE ROUTE MINIGIOCO PROVINCE  
#? ROUTE MINIGIOCO PROVINCE ROUTE MINIGIOCO PROVINCE  

@app.route("/game/province", methods=["GET"])
def gameprovince():
    rndprov = rnd.randrange(len(province)-1)
    rndprov = province[province.index == rndprov].DEN_UTS.to_string(index=False)
    
    folprov = folium.Map(location=[41,12], zoom_start=6.4, max_bounds=True, tiles='stamenwatercolor')
    

    for _, r in province.iterrows():
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.0000000000000000000000000000000000000000000000001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j)
        folium.Popup(f"<form action='/game/province/conferma' method='POST'> <input type='hidden' name='provincia' value='{r['DEN_UTS']}' > <input type='hidden' name='random' value='{rndprov}' > <input type='submit' value='Conferma' style='font-family: sans-serif;border-radius: 10px;height: 35px;width: 100px;font-size: 18px;font-weight: bold;'> </form>"
        ).add_to(geo_j)
        geo_j.add_to(folprov)

    return render_template("game.html",titolo = "MINIGIOCO SULLE PROVINCE" , map = folprov._repr_html_(), indovina = "Indovina la provincia:", rndnome = rndprov)

@app.route("/game/province/conferma", methods=["POST"])
def conferma_province():
    provincia = request.form["provincia"]
    print(provincia)
    random = request.form["random"]
    risultato = "No, la risposta è sbagliata"
    immagine = "/static/img/errore.png"
    if provincia == random:
        risultato = "La risposta è corretta"
        immagine = "/static/img/giusto.png"
    return render_template("conferma.html", risposta=provincia, risultato=risultato, immagine= immagine)


#?--------------------------------------------------------------------
#?--------------------------------------------------------------------



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)