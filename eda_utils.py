import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def generate_basic_stats(_df):
    """Generate and cache summary statistics for a dataset."""
    return _df.describe(include='all').transpose()

# Categorical Plots

def create_categorical_plot(df, col_name, show_percentage=False):
    """Creates a Plotly bar chart for a selected categorical column.
       Optionally shows percentages instead of raw counts.
    """
    if df[col_name].nunique() == 0:
        return None

    counts = df[col_name].value_counts().nlargest(10).reset_index()
    counts.columns = [col_name, 'count']

    if show_percentage:
        total = counts['count'].sum()
        counts['percentage'] = (counts['count'] / total * 100).round(2)
        fig = px.bar(
            counts,
            x='percentage',
            y=col_name,
            orientation='h',
            title=f"Top 10 Value Percentages for {col_name}",
            text='percentage'
        ).update_yaxes(categoryorder="total ascending")
    else:
        fig = px.bar(
            counts,
            x='count',
            y=col_name,
            orientation='h',
            title=f"Top 10 Value Counts for {col_name}",
            text='count'
        ).update_yaxes(categoryorder="total ascending")

    return fig

# Numerical Plots

def create_numerical_plot(df, col_name, add_kde=False):
    """Creates a visualization for a numerical column.
       - If column looks like discrete sequential numbers → line chart
       - If few unique values → bar chart
       - Otherwise → histogram with optional KDE
    """
    if df[col_name].dropna().empty:
        return None

    unique_vals = df[col_name].nunique()
    sorted_vals = sorted(df[col_name].dropna().unique())

    # Case 1: Small range of integers (e.g., overs, innings)
    if unique_vals < 30 and all(float(v).is_integer() for v in sorted_vals):
        counts = df[col_name].value_counts().sort_index()
        fig = px.line(
            x=counts.index,
            y=counts.values,
            markers=True,
            title=f"Line Plot of {col_name} (Counts)"
        )
        fig.update_layout(xaxis_title=col_name, yaxis_title="Count")
        return fig

    # Case 2: Discrete numeric but not sequential (few unique values)
    if unique_vals < 20:
        counts = df[col_name].value_counts().reset_index()
        counts.columns = [col_name, 'count']
        fig = px.bar(
            counts,
            x=col_name,
            y='count',
            title=f"Distribution of {col_name} (Discrete)"
        )
        return fig

    # Case 3: Continuous numeric
    fig = px.histogram(
        df,
        x=col_name,
        title=f"Distribution of {col_name}",
        marginal="box"
    )

    if add_kde:
        fig = px.histogram(
            df,
            x=col_name,
            nbins=30,
            marginal="box",
            histnorm='density'
        )
        fig.update_traces(opacity=0.6)
        kde_fig = px.density_contour(df, x=col_name)
        fig.add_traces(kde_fig.data)

    return fig


# Correlation Heatmap

@st.cache_data
def generate_correlation_heatmap_fig(_df):
    """Generates and caches a correlation heatmap for numeric columns."""
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
