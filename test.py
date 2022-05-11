
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


mondo =  gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')).to_crs(epsg=4326)

print(len(mondo))