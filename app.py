import streamlit as st
import pandas as pd
import os
from pathlib import Path
from io import BytesIO
from main import save_animation
from PIL import Image

# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title=" BarChart Timeseries Animation Generator",
    page_icon="📊",
    layout="centered"
)

# ------------------------------------------------------------
# Title and Description
# ------------------------------------------------------------
st.title("📊 BarChart Timeseries Animation Generator")
st.markdown(
    """
    Turn your **time series data** into an engaging **bar chart race animation**.  
    Upload your dataset, customize the look, and download your animation as `.mp4` or `.gif`.
    """
)

st.markdown("---")

# ------------------------------------------------------------
# Data Input
# ------------------------------------------------------------
st.header("📁 1 - Upload Your Data")

# Chart Title
title = st.text_input("📝 Chart Title", placeholder="e.g., Global Population Growth (1960–2020)")

# CSV Upload
uploaded_csv = st.file_uploader("📄 Upload your CSV file", type=["csv"])
df = None
frames = None
if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    frames = df['dt'].unique().tolist()
    st.success("✅ CSV loaded successfully!")
    st.caption("Here's a preview of your data:")
    st.dataframe(df.head())

st.markdown("---")

# ------------------------------------------------------------
# Icon Upload
# ------------------------------------------------------------
st.header("🏁 2 - Upload Icon Images")

st.caption("Upload one `.png` file per label — the file name should match your dataset labels.")

uploaded_icons = st.file_uploader(
    "📸 Upload .png icons",
    type=["png"],
    accept_multiple_files=True
)

icons = {}
if uploaded_icons:
    for file in uploaded_icons:
        label = os.path.splitext(file.name)[0]
        icons[label] = Image.open(BytesIO(file.read()))
    st.success(f"✅ {len(icons)} icons loaded successfully!")

st.markdown("---")

# ------------------------------------------------------------
# Chart Configuration
# ------------------------------------------------------------
st.header("⚙️ 3 - Chart Configuration (Optional)")

# Create two columns for better organization
col1, col2 = st.columns(2)

with col1:
    file_format = st.segmented_control("🎞️ Export Format", options=["mp4", "gif"])
    fps = st.slider("🎚️ Frames per Second (fps)", min_value=1, max_value=60, value=12)
    n_largest = st.slider("🏅 Bars Displayed", min_value=5, max_value=30, value=10)

with col2:
    width = st.slider("📏 Chart Width", min_value=6, max_value=20, value=12)
    height = st.slider("📐 Chart Height", min_value=4, max_value=12, value=8)
    palettes = sorted([
        "viridis", "plasma", "inferno", "magma", "cividis", "rocket", "mako", "crest", "flare", "vlag",
        "icefire", "Spectral", "coolwarm", "RdYlBu", "cubehelix", "Paired", "tab10", "Set2", "pastel", "deep",
    ])
    palette = st.selectbox("🎨 Color Palette", options=palettes, index=0)
    st.markdown(
            """
            <div>
                <a href="https://seaborn.pydata.org/tutorial/color_palettes.html" target="_blank">
                    🔗 Learn more
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

# ------------------------------------------------------------
# Download Section
# ------------------------------------------------------------
st.header("💾 4 - Generate and Download")

st.markdown("When ready, click **Download** to generate your animation video.")

if st.button("Generate & Download Animation"):
    try:
        # Create output folder
        output_path = Path("downloads")
        output_path.mkdir(exist_ok=True)

        with st.spinner("🎥 Generating your animation... please wait ⏳"):
            save_animation(
                df=df,
                frames=frames,
                icons=icons,
                file_format=file_format,
                output_path=output_path,
                title=title,
                width=width,
                height=height,
                fps=fps,
                n_largest=n_largest,
                palette=palette
            )

        st.success("✅ Animation successfully generated!")

        # Find latest downloaded file
        files = sorted(output_path.glob(f"*.{file_format}"), key=os.path.getmtime, reverse=True)
        if files:
            latest = files[0]
            st.video(str(latest))
            with open(latest, "rb") as file:
                st.download_button(
                    label="⬇️ Download File",
                    data=file,
                    file_name=latest.name,
                    mime="video/mp4" if file_format == "mp4" else "image/gif"
                )

    except Exception as e:
        st.error(f"❌ Error: {e}")