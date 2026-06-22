"""
Streamlit Dashboard Application for Business Analytics.
Provides interactive Plotly visualizations from uploaded CSV data.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. STREAMLIT APP & UPLOADER SETUP
# ==============================================================================
st.set_page_config(page_title="Analytics Dashboard", layout="wide")

st.title("Interactive Business & Performance Dashboard")
st.markdown(
    "Upload your CSV file below to automatically generate the dashboard. "
    "You can download high-res images for Word using the camera icon on the chart, "
    "or download the interactive HTML file using the button below the chart."
)

# The File Uploader Button
uploaded_file = st.file_uploader("Upload your Race Data (CSV)", type=['csv'])

if uploaded_file is not None:
    # ==============================================================================
    # 2. DATA LOADING & PREPARATION
    # ==============================================================================
    df = pd.read_csv(uploaded_file)

    # Clean up Wager column text and format dates
    df["wager"] = pd.to_numeric(
        df["wager"].astype(str).str.replace(",", "").str.replace('"', ""),
        errors="coerce",
    )
    df["Date "] = pd.to_datetime(df["Date "], errors="coerce")
    df_plot = df.dropna(subset=["Date ", "wager"]).sort_values("Date ")

    # Automatically grab all race/product columns
    product = [
        col for col in df.columns
        if col.strip() not in ["Date", "Date ", "wager", "Total players of race  6"]
    ]

    # ==============================================================================
    # 3. DASHBOARD LAYOUT SETUP
    # ==============================================================================
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{}, {}],
            [{"colspan": 2}, None],
        ],
        subplot_titles=(
            "Total Wagers Over Time",
            "Performance vs. Player Volume (Race 6)",
            "Product Performance Over Time",
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.08,
    )

    # ==============================================================================
    # 4. ADDING TRACES
    # ==============================================================================

    # --- Chart 1: Total Wagers (Top-Left) ---
    fig.add_trace(
        go.Scatter(
            x=df_plot["Date "],
            y=df_plot["wager"],
            mode="lines+markers",
            name="Wager Amount",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.1)",
            showlegend=False,
            hovertemplate="Date: %{x}<br>Wager: %{y:,.0f}<extra></extra>",
        ),
        row=1, col=1,
    )

    # --- Chart 2: Volume vs Performance Mix (Top-Right) ---
    # Legend is turned ON and grouped for this specific chart
    fig.add_trace(
        go.Bar(
            x=df["Date "],
            y=df["Total players of race  6"],
            name="Total Players",
            legendgroup="Chart2",
            legendgrouptitle_text="<b>Volume vs Perf</b>",
            marker_color="rgba(16, 185, 129, 0.6)",
            marker_line=dict(color="#10b981", width=1.5),
            showlegend=True,
            hovertemplate="Players: %{y}<extra></extra>",
        ),
        row=1, col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=df["Date "],
            y=df["Race 6"],
            name="Race 6 Performance",
            legendgroup="Chart2",
            mode="lines+markers",
            line=dict(color="#ef4444", width=3, shape="spline"),
            marker=dict(size=5),
            showlegend=True,
            hovertemplate="Performance: %{y}<extra></extra>",
        ),
        row=1, col=2,
    )

    # --- Chart 3: Comparative Product Performance (Bottom Full-Width) ---
    color_palette = px.colors.qualitative.Safe
    color_idx = 0

    for prod in product:
        if prod in df.columns:
            is_race_6 = prod.strip() == "Race 6"

            line_color = "#ef4444" if is_race_6 else color_palette[color_idx % len(color_palette)]
            line_width = 4 if is_race_6 else 2
            if not is_race_6:
                color_idx += 1

            fig.add_trace(
                go.Scatter(
                    x=df["Date "],
                    y=df[prod],
                    mode="lines+markers",
                    name=prod,
                    legendgroup="Chart3",
                    legendgrouptitle_text="<b>Products</b>",
                    line=dict(color=line_color, width=line_width, shape="spline", smoothing=1.3),
                    marker=dict(size=6 if is_race_6 else 4),
                    showlegend=True,
                    hovertemplate=f"<b>{prod}</b>: %{{y}}<extra></extra>",
                ),
                row=2, col=1,
            )

    # ==============================================================================
    # 5. DASHBOARD STYLING & INTERACTIVE FEATURES
    # ==============================================================================
    fig.update_layout(
        template="plotly_white",
        plot_bgcolor="#ffffff",
        hovermode="x unified",
        height=850,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#e2e8f0",
            borderwidth=1,
        ),
    )

    # Add Time-Range buttons to the bottom chart
    fig.update_xaxes(
        title_text="Date",
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(step="all", label="All")
            ])
        ),
        row=2, col=1
    )

    # REMOVE ALL GRIDLINES
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    # Set Titles
    fig.update_yaxes(title_text="Total Wager", tickformat=",.0f", row=1, col=1)
    fig.update_yaxes(title_text="Value / Volumes", row=1, col=2)
    fig.update_yaxes(title_text="Performance Metrics", row=2, col=1)

    # ==============================================================================
    # 6. EXPORT CONFIG & STREAMLIT RENDER
    # ==============================================================================
    config = {
        "scrollZoom": True,
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "Dashboard_Export",
            "height": 950,
            "width": 1400,
            "scale": 2,
        },
    }

    # Render the interactive chart
    st.plotly_chart(fig, use_container_width=True, config=config)

    # ==============================================================================
    # 7. HTML EXPORT BUTTON
    # ==============================================================================
    html_string = fig.to_html(full_html=True, include_plotlyjs='cdn', config=config)

    st.download_button(
        label="📥 Download Dashboard as Interactive HTML",
        data=html_string,
        file_name="Interactive_Dashboard.html",
        mime="text/html"
    )

else:
    st.info("Awaiting file upload. Please upload a CSV to generate the dashboard.")