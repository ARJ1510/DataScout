import streamlit as st
import pandas as pd
import io
import plotly.express as px

@st.cache_data
def generate_basic_stats(_df):
    """Caches the generation of summary statistics and returns them."""
    return _df.describe(include='all').transpose()

def create_categorical_plot(df, col_name):
    """Creates a single Plotly bar chart for a selected categorical column."""
    if df[col_name].nunique() == 0:
        return None
        
    top_10_counts = df[col_name].value_counts().nlargest(10).reset_index()
    top_10_counts.columns = [col_name, 'count']
    fig = px.bar(
        top_10_counts,
        x='count',
        y=col_name,
        orientation='h',
        title=f"Top 10 Value Counts for {col_name}",
        text='count'
    ).update_yaxes(categoryorder="total ascending")
    return fig

def create_numerical_plot(df, col_name):
    """Creates a single Plotly histogram for a selected numerical column."""
    if df[col_name].dropna().empty:
        return None
        
    fig = px.histogram(
        df,
        x=col_name,
        title=f"Distribution of {col_name}",
        marginal="box"
    )
    return fig

@st.cache_data
def generate_correlation_heatmap_fig(_df):
    """
    Caches the correlation calculation and figure generation.
    Returns the Plotly figure object.
    """
    num_df = _df.select_dtypes(include='number')
    if num_df.shape[1] < 2:
        return None 

    corr_matrix = num_df.corr()
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title="Correlation Heatmap",
        color_continuous_scale='RdBu_r'
    )
    return fig
