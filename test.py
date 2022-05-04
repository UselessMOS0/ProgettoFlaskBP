
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


regioni = gpd.read_file("/workspace/ProgettoFlaskBP/static/Files/Regioni.zip").to_crs(3857)

for reg in regioni.DEN_REG.tolist():
    print(regioni[regioni.DEN_REG == reg].geometry.centroid.x)
    print(regioni[regioni.DEN_REG == reg].geometry.centroid.y)

print(regioni)
