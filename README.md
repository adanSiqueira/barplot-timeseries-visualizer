<h1 align="center">Barplot Time Series Animation Generator</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/Pandas-Data%20Analysis-yellow?logo=pandas&logoColor=white" alt="Pandas Badge"/>
  <img src="https://img.shields.io/badge/Matplotlib-Visualization-orange?logo=plotly&logoColor=white" alt="Matplotlib Badge"/>
  <img src="https://img.shields.io/badge/Seaborn-Styling-teal?logo=seaborn&logoColor=white" alt="Seaborn Badge"/>
  <img src="https://img.shields.io/badge/FFmpeg-Video%20Encoding-red?logo=ffmpeg&logoColor=white" alt="FFmpeg Badge"/>
</p>

<p align="center">
  <strong> Link:</strong>  
  <a href="https://barplot-timeseries-animation-generator.streamlit.app/">
    https://barplot-timeseries-animation-generator.streamlit.app/
  </a><br>
  Upload your dataset and icons, and <strong>build animations like this:</strong>
</p>

![Demo](animations/animation.gif)

---

##  Overview
This project is a **Streamlit web app** and **Python blueprint** for generating *animated bar chart races* that visualize how top categories evolve over time, similar to the popular **“bar chart race”** videos.

It’s designed to be modular, readable, and easily extensible into a fully automated program where you can simply provide a dataset with three key columns, and generate animations directly.

The animation showcases the top entities per period (e.g., year), dynamically updating ranks, bars, and optional icons.
Use it for visualizing:

* Population growth by country
* Company revenues by year
* Product sales by month
* Sports or performance statistics
* Any time-based ranking visualization

---

## Features

-  **Animated barplots** over time (year, month, etc.)
-  **Modular structure** with reusable setup functions
-  **Parallel processing** to render and save animations simultaneously
- **Custom plot styling** via `setup_plotstyle()`
-  **Dynamic year label overlay** with `setup_year()`
-  **Automatic export** to `.mp4` using `ffmpeg`

---

## Requirements

If running locally, sure the following libraries are installed:

```bash
pip install -r requirements.txt
````

If you want to save animations as `.mp4`, you’ll also need **FFmpeg** installed on your system:

* Windows: [Download FFmpeg](https://ffmpeg.org/download.html)
* macOS (Homebrew): `brew install ffmpeg`
* Linux (Debian/Ubuntu): `sudo apt install ffmpeg`
---

##  Project Structure

```
barplot-timeseries-animation/
├── data/
│   └── clean-data.csv         # Dataset 
│   └── un-country-data.csv    # Raw data
├── main.py                    # Modular script containing all logic functionalities
├── app.py                     # Streamlit application
├── README.md                  # Project documentation
└── requirements.txt           # Python dependencies
└── packages.txt               # OS Dependencies
```

---

##  Expected Data Format

Your CSV should include **three columns**:

| Column  | Description                               |
| ------- | ----------------------------------------- |
| `dt`    | Time unit (year, month, etc.)             |
| `label` | Category name (country, product, etc.)    |
| `x`     | Numeric value (population, revenue, etc.) |

Example:

| dt   | label | x         |
| ---- | ----- | --------- |
| 1950 | China | 554419000 |
| 1950 | India | 376325200 |
| 1950 | USA   | 157813000 |
| 1951 | China | 562388000 |
| 1951 | India | 382740000 |

---

##  Core Functions (in `main.py`)

| Function                                                                                                         | Description                                                                                                       | Key Parameters                                                        | Returns                     |
| ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------- |
| **`load_icons(df, icon_folder, label_col)`**                                                                     | Loads and resizes `.png` icons for each label (e.g., country flag, logo), returning a mapping from label → image. | `df`, `icon_folder`, `label_col`                                      | `dict` — {label: PIL.Image} |
| **`add_icons(ax, icons)`**                                                                                       | Places each corresponding icon next to its y-axis label in a horizontal bar chart.                                | `ax`, `icons`                                                         | `None`                      |
| **`draw_frame(ax, df, title, frame, icons, n_largest, colors, palette)`**                                        | Renders a single frame of the animated chart, showing the top N values for a given time or index.                 | `ax`, `df`, `title`, `frame`, `icons`, `n_largest`, `palette`         | `None`                      |
| **`setup_plotstyle(ax)`**                                                                                        | Applies a clean, minimal style to a Matplotlib Axes (removes spines and unnecessary ticks).                       | `ax`                                                                  | `None`                      |
| **`wrap_labels(ax, width)`**                                                                                     | Automatically wraps long y-axis labels into multiple lines to prevent overflow.                                   | `ax`, `width`                                                         | `None`                      |
| **`setup_dt(ax, dt)`**                                                                                           | Displays the current frame label (e.g., year) within the chart area.                                              | `ax`, `dt`                                                            | `None`                      |
| **`save_animation(df, frames, icons, file_format, output_path, title, width, height, fps, n_largest, palette)`** | Generates and saves the full animated bar chart as an `.mp4` or `.gif` file using `ffmpeg`.                       | `df`, `frames`, `icons`, `file_format`, `output_path`, `title`, `fps` | `None`                      |
| **`show_animation(df, frames, icons, title, width, height, fps, n_largest, palette)`**                           | Displays the animation interactively in a Matplotlib window (instead of saving).                                  | `df`, `frames`, `icons`, `title`, `fps`                               | `None`                      |

---

##  How It Works

### 1. Data is filtered for each frame

```python
frame_data = df[df['dt'] == frame]
top_items = frame_data.nlargest(n_largest, 'x')
```

### 2. Bars are drawn with Seaborn

```python
sns.barplot(x='x', y='label', data=top_items, palette='viridis', ax=ax)
```

### 3. Optional icons are attached

```python
img = icons[label].convert("RGBA")
imagebox = OffsetImage(img, zoom=0.07)
```

### 4. Animation saved

```python
anim.save(os.path.join(output_path, "animation.mp4"), writer="ffmpeg", fps=fps)
```
---

##  Author

**Adan Siqueira**  
 [GitHub Profile](https://github.com/AdanSiqueira)

---

If you like this project, don’t forget to ⭐ star the repository to show your support!