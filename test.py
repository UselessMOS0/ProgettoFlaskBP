
import io
import pandas as pd
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

popolazione = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/bilancio_demografico_regioni.zip")
popolazione = popolazione.filter(["Regione","Popolazione al 1° gennaio - Maschi", "Popolazione al 1° gennaio - Femmine"])
print(popolazione)

popolazione["Popolazione al 1° gennaio - Maschi"] = popolazione["Popolazione al 1° gennaio - Maschi"].astype(float)
popolazione["Popolazione al 1° gennaio - Femmine"] = popolazione["Popolazione al 1° gennaio - Femmine"].astype(float)
popolazione["Popolazione_totale"] = popolazione["Popolazione al 1° gennaio - Maschi"] + popolazione["Popolazione al 1° gennaio - Femmine"]
popolazione = popolazione.dropna()
popolazione["Popolazione_totale"] = popolazione["Popolazione_totale"].astype(int)
print(popolazione)


