from shiny import App, render, ui
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget
from datetime import datetime
from ipywidgets import widgets, interactive, Output
import seaborn as sns

df1 = pd.read_csv("data/all_apartments.csv")
df1['Price per Bed'] = df1['Price per Bed'].astype('int')
df1['# Beds'] = df1['# Beds'].astype('int')
df2 = pd.read_csv('data/all_nuisance_complaints.csv')

app_ui = ui.page_fluid(
    ui.panel_title("Nuisance Complaints (Urbana) & Apartments (CU)"),
    ui.navset_pill(
        ui.nav_panel("# of Beds vs. Price per Bed", output_widget("bar_chart")),
        ui.nav_panel("Disposition Categories for Nuisances", output_widget("pie_chart")),
        ui.nav_panel("Map of Apartments (CU) and Nuisance Complaints (Urbana)",
                    ui.input_slider("price_per_bed", "Price per Bed", 
                        min=df1['Price per Bed'].min(), max=df1['Price per Bed'].max(),
                        value=[df1['Price per Bed'].min(), df1['Price per Bed'].max()]),
                    ui.input_slider("num_beds", "Number of Beds", 
                        min=df1['# Beds'].min(), max=df1['# Beds'].max(),
                        value=[df1['# Beds'].min(), df1['# Beds'].max()]),
                    output_widget("mapped", width="100%", height="1000px")),
        id="tab",
    )
)

def server(input, output, session):
    @render_widget
    def mapped():
        price_range = input.price_per_bed()
        bed_range = input.num_beds()

        filtered_df1 = df1[
            (df1['Price per Bed'] >= price_range[0]) & 
            (df1['Price per Bed'] <= price_range[1])
        ]

        filtered_df1 = filtered_df1[
            (filtered_df1['# Beds'] >= bed_range[0]) & 
            (filtered_df1['# Beds'] <= bed_range[1])
        ]

        fig = px.scatter_mapbox(filtered_df1, lat='Latitude', lon='Longitude',
                                hover_name='Address', hover_data=['Price per Bed', '# Beds'],
                                zoom=10, color_discrete_sequence=['violet'], opacity=0.1)
        
        # Update marker size for df1
        fig.update_traces(marker=dict(size=12, opacity=0.7))
        
        # Add trace for the second dataset
        fig.add_scattermapbox(
            lat=df2['Latitude'], lon=df2['Longitude'],
            mode='markers',
            hoverinfo='text',
            hovertext=df2['Type of Complaint'],
            marker=dict(size=8, color='darkseagreen', opacity=0.1),  # Update marker size for df2
            name='Complaints'
        )
        
        
        # Update layout
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
        
        return fig
    @render_widget
    def bar_chart():
        fig = go.Figure(data=go.Scatter(x=df1['# Beds'],
                                y=df1['Price per Bed'],
                                mode='markers',
                                marker_color='darkseagreen'),)

        fig.update_layout(
                        xaxis_title='# of Beds',
                        yaxis_title='Price per Bed ($)',
                        autosize=False,
                        width=1000,
                        height=600,
                        margin=dict(l=50, r=50, b=100, t=100, pad=4),
                        paper_bgcolor="LightSteelBlue",)
        return fig
    @render_widget
    def pie_chart():
        disposition_counts = df2['Disposition'].value_counts()
        colorblind_palette = sns.color_palette("colorblind", len(disposition_counts))

        fig = go.Figure(data=go.Pie(labels=disposition_counts.index,
                                    values=disposition_counts,
                                    textinfo='label+percent',
                                    insidetextorientation='radial',
                                    marker=dict(colors=colorblind_palette.as_hex())))

        fig.update_layout(autosize=False,
                        width=1000,
                        height=600,
                        margin=dict(l=50, r=50, b=100, t=100, pad=4),
                        paper_bgcolor="LightSteelBlue",)
        return fig

app = App(app_ui, server)