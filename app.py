from shiny import App, render, ui
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget
from datetime import datetime
from ipywidgets import widgets, interactive, Output

df1 = pd.read_csv("data/all_apartments.csv")
df2 = pd.read_csv('data/all_nuisance_complaints.csv')

app_ui = ui.page_fluid(
    ui.panel_title("Nuisance Complaints & Apartments in Urbana"),
    ui.navset_pill(
        ui.nav_panel("Map", output_widget("mapped", width="100%", height="1000px")),
        id="tab",
    )
)

def server(input, output, session):
    @render_widget
    def mapped():
        fig = px.scatter_mapbox(df1, lat='Latitude', lon='Longitude',
                                hover_name='Address', hover_data=['Price per Bed', '# Beds'],
                                zoom=10, color_discrete_sequence=['blue'], opacity=0.7)
        
        # Update marker size for df1
        fig.update_traces(marker=dict(size=12, opacity=0.7))
        
        # Add trace for the second dataset
        fig.add_scattermapbox(
            lat=df2['Latitude'], lon=df2['Longitude'],
            mode='markers',
            hoverinfo='text',
            hovertext=df2['Type of Complaint'],
            marker=dict(size=8, color='red', opacity=0.7),  # Update marker size for df2
            name='Complaints'
        )
        
        # Update layout
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=800)
        
        return fig

app = App(app_ui, server)