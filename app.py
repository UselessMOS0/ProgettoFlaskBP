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
df_quiz = pd.read_csv("/workspace/ProgettoFlaskBP/static/Files/quiz.csv")
lista = []
giuste = 0 
sbagliate = 0 
contatore = 1

#? ROUTE
#? ROUTE HOME PAGE

@app.route("/", methods=["GET"])
def home_page():
    return render_template("homePage.html")

#!--------------------------------------------------------------------
#!--------------------------------------------------------------------


#? ROUTE LOGIN E REG ROUTE LOGIN E REG
#? ROUTE LOGIN E REG ROUTE LOGIN E REG

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form['Username']
        password = request.form['Password']
        
        for index,c in credenziali.iterrows():
            if username == c["Username"] and password == c["Password"]:
                session['username'] = username
                return redirect(url_for('home'))  
            
        return render_template("errore.html")
        #return redirect(url_for('login'))
            
@app.route("/registrazione", methods=['GET','POST'])
def registrazione():
    if request.method == 'GET':
        return render_template("registrazione.html")

    elif request.method == "POST":
        email = request.form['Email']
        username = request.form['Username'].replace(" ", "")
        password = request.form['Password']

        global credenziali

        if username in credenziali["Username"].tolist():
            return redirect(url_for("registrazione"))
        else:
            utente = {"Email":email,"Username": username,"Password":password,"Points":'0'}
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

@app.route("/home", methods=["GET"])
def home():
    global contatore, lista, giuste, sbagliate
    lista = []
    contatore = 1
    giuste = 0 
    sbagliate = 0 
    if not session.get('username'):
        return redirect(url_for('login'))

    credenziali = pd.read_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv')
    for index,c in credenziali.iterrows():
        if session['username'] == c.Username:
            session['points'] = int(c.Points)

    return render_template("home.html",username = session['username'],points = session['points'])

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
    if not session.get('username'):
        return redirect(url_for('login'))
#   global popolazione_reg, reg, regioneUtente, province_reg, covid_reg
    global reg, regioneUtente, province_reg
    print(regioni)
    reg = regione
    regioneUtente = regioni[regioni["DEN_REG"] == reg]
    perimetro = round(regioneUtente.geometry.length,3)
    area = round(regioneUtente["Shape_Area"] / 10**9,3)
    province_reg = province[province.within(regioneUtente.geometry.squeeze())]
    popolazione_reg = popolazione[popolazione["Regione"] == reg]
    covid_reg = covid[covid["denominazione_regione"] == reg]
    return render_template("info.html", regione=regione, perimetro=perimetro.values[0], area=area.values[0] ,province=province_reg['DEN_UTS'].tolist(), popolazione = popolazione_reg["Popolazione_totale"].values[0], covid = covid_reg["casi_testati"].values[0],username = session['username'],points = session['points'])


@app.route("/regione.png", methods=["GET"])
def regione_png():
    fig, ax = plt.subplots(figsize = (10,6))

    regioneUtente.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor="k")
    province_reg.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor="k")
    contextily.add_basemap(ax=ax)   

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

'''
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    result = output.getvalue()
    plt.close(fig)
    return Response(result, mimetype='image/png') '''

'''
@app.route("/popolazione.png", methods=["GET"])
def popolazione_png():
    fig, ax = plt.subplots(figsize = (12,8))

    posizione = popolazione[popolazione["Regione"] == reg].index.values[0]
    ax.bar(popolazione["Regione"], popolazione["Popolazione_totale"])[posizione].set_color("r")
    fig.autofmt_xdate(rotation=45)
    
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

''' 


@app.route("/grafici.png", methods=["GET"])
def grafici_png():
    fig, (ax1,ax2) = plt.subplots(1,2,figsize = (20,8))

    posizione_pop = popolazione[popolazione["Regione"] == reg].index.values[0]
    ax1.bar(popolazione["Regione"], popolazione["Popolazione_totale"])[posizione_pop].set_color("r")
    posizione_cov = covid[covid["denominazione_regione"] == reg].index.values[0]
    ax2.bar(covid["denominazione_regione"], covid["casi_testati"])[posizione_cov].set_color("r")
    fig.autofmt_xdate(rotation=45)
    
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
    
'''
@app.route("/covid.png", methods=["GET"])
def covid_png():
    fig, ax = plt.subplots(figsize = (12,8))

    posizione = covid[covid["denominazione_regione"] == reg].index.values[0]
    ax.bar(covid["denominazione_regione"], covid["casi_testati"])[posizione].set_color("r")
    fig.autofmt_xdate(rotation=45)
    
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')   
'''
#?--------------------------------------------------------------------
#?--------------------------------------------------------------------


#? ROUTE MINIGIOCO MONDO ROUTE MINIGIOCO MONDO
#? ROUTE MINIGIOCO MONDO ROUTE MINIGIOCO MONDO


@app.route("/game", methods=["GET"])
def game():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template("mod.html", username = session['username'],points = session['points'])

@app.route("/game/mondo", methods=["GET"])
def gamemondo():
    if not session.get('username'):
        return redirect(url_for('login'))
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

    return render_template("game.html",titolo = "MINIGIOCO SUGLI STATI DEL MONDO" , map = folmondo._repr_html_(),indovina = "Indovina lo stato:" , rndnome = rndpaese,username = session['username'],points = session['points'])

@app.route("/game/mondo/conferma", methods=["POST"])
def conferma_mondo():
    if not session.get('username'):
        return redirect(url_for('login'))
    paese = request.form["paese"]
    random = request.form["random"]
    risultato = "No, la risposta è sbagliata"
    immagine = "/static/img/errore.png"
    if paese == random:
        risultato = "La risposta è corretta"
        
        session['points'] += 50
        credenziali.loc[credenziali[credenziali['Username']==session['username']].index,'Points'] = session['points']
        credenziali.to_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv',index=False)  

        immagine = "/static/img/giusto.png"
    return render_template("conferma.html", risposta=paese, risultato= risultato, immagine = immagine,username = session['username'],points = session['points'])


#?--------------------------------------------------------------------
#?--------------------------------------------------------------------


#? ROUTE MINIGIOCO PROVINCE ROUTE MINIGIOCO PROVINCE  
#? ROUTE MINIGIOCO PROVINCE ROUTE MINIGIOCO PROVINCE  

@app.route("/game/province", methods=["GET"])
def gameprovince():
    if not session.get('username'):
        return redirect(url_for('login'))
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

    return render_template("game.html",titolo = "MINIGIOCO SULLE PROVINCE" , map = folprov._repr_html_(), indovina = "Indovina la provincia:", rndnome = rndprov,username = session['username'],points = session['points'])

@app.route("/game/province/conferma", methods=["POST"])
def conferma_province():
    if not session.get('username'):
        return redirect(url_for('login'))
    provincia = request.form["provincia"]
    print(provincia)
    random = request.form["random"]
    risultato = "No, la risposta è sbagliata"
    immagine = "/static/img/errore.png"
    if provincia == random:
        risultato = "La risposta è corretta"

        session['points'] += 50
        credenziali.loc[credenziali[credenziali['Username']==session['username']].index,'Points'] = session['points']
        credenziali.to_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv',index=False)  

        immagine = "/static/img/giusto.png"
    return render_template("conferma.html", risposta=provincia, risultato=risultato, immagine= immagine, username = session['username'],points = session['points'])


#?--------------------------------------------------------------------
#?--------------------------------------------------------------------

#? ROUTE QUIZ
#? ROUTE QUIZ 

@app.route("/quiz", methods=["GET"])
def quiz():
    global contatore, lista, giuste, sbagliate

    if contatore > 5:
        session['points'] += giuste * 5
        credenziali.loc[credenziali[credenziali['Username']==session['username']].index,'Points'] = session['points']
        credenziali.to_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv',index=False)  
        return render_template("fine.html", giuste = giuste, sbagliate = sbagliate)
    else:
        rnd_quiz = rnd.randrange(len(df_quiz))
        while rnd_quiz in lista:
            rnd_quiz = rnd.randrange(len(df_quiz))

        lista.append(rnd_quiz)
        print(lista)
        domanda = df_quiz[df_quiz.index == rnd_quiz].Domande.to_string(index=False)
        op1 = df_quiz[df_quiz.index == rnd_quiz].Opzione1.to_string(index=False)
        op2 = df_quiz[df_quiz.index == rnd_quiz].Opzione2.to_string(index=False)
        op3 = df_quiz[df_quiz.index == rnd_quiz].Opzione3.to_string(index=False)
        op4 = df_quiz[df_quiz.index == rnd_quiz].Opzione4.to_string(index=False)
        session["risposta"] = df_quiz[df_quiz.index == rnd_quiz].Risposte.to_string(index=False)
        return render_template("quiz.html", domanda = domanda, opzione1 = op1, opzione2 = op2, opzione3 = op3, opzione4 = op4,numero=contatore)

@app.route("/quiz/controllo",methods=["GET"])
def conferma_risposta():
    global contatore, giuste, sbagliate
    contatore = contatore + 1
    scelta = request.args["scelta"]
    if scelta == session["risposta"]:
        giuste = giuste + 1 
       # session['points'] += 5
       # credenziali.loc[credenziali[credenziali['Username']==session['username']].index,'Points'] = session['points']
       # credenziali.to_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv',index=False)  
        return redirect(url_for("quiz"))
    else:
        sbagliate = sbagliate + 1 
        return redirect(url_for("quiz"))
        

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)