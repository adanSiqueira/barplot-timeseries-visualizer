import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from multiprocessing import Process
import pandas as pd
import seaborn as sns
import numpy as np
import textwrap
from PIL import Image
import os


def load_icons(df: pd.DataFrame, icon_folder: str, label_col: str) -> dict:
    """
    Load and resize icons (e.g., flags or logos) for each unique label in the dataset.

    This function reads PNG images from a directory and builds a mapping between 
    each label in the provided DataFrame and its corresponding image, resized 
    proportionally for consistent placement on plots.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least one column of categorical labels.
    icon_folder : str
        Path to the folder containing the icon files (e.g., "./icons").
        Each icon filename must match a label value, with a ".png" extension.
    label_col : str
        Name of the column in `df` containing label values.

    Returns
    -------
    dict
        Dictionary mapping each label (str) → PIL.Image.Image object.
    """
    icons = {}
    for label in df[label_col].unique():
        filename = os.path.join(icon_folder, f"{label}.png")
        if os.path.exists(filename):
            img = Image.open(filename).convert("RGB")
            img.thumbnail((30, 20), Image.Resampling.LANCZOS)
            icons[label] = img
    return icons


def add_icons(ax: plt.Axes, icons: dict) -> None:
    """
    Attach small images (e.g., flags or icons) next to each y-axis label in a bar chart.

    This function places images aligned to the y-tick positions, typically used to 
    visually identify each label in a horizontal bar plot.

    Parameters
    ----------
    ax : plt.Axes
        Matplotlib Axes object containing the horizontal bar plot.
    icons : dict
        Dictionary mapping label names (str) → PIL.Image.Image objects.

    Returns
    -------
    None
    """
    ytick_labels = [t.get_text().replace('\n', ' ') for t in ax.get_yticklabels()]
    ytick_positions = ax.get_yticks()

    for y_pos, label in zip(ytick_positions, ytick_labels):
        if label in icons:
            img = icons[label].convert("RGBA")
            fig = ax.get_figure()
            dpi_scale = fig.dpi / 100.0
            imagebox = OffsetImage(img, zoom=0.07 / dpi_scale)
            ab = AnnotationBbox(
                imagebox,
                xy=(0, y_pos),
                xybox=(-15, 0),
                box_alignment=(0, 0.5),
                frameon=False,
                xycoords=('data', 'data'),
                boxcoords="offset points",
                pad=0
            )
            ax.add_artist(ab)


def draw_frame(
    ax: plt.Axes, 
    df: pd.DataFrame, 
    title: str, 
    frame: int, 
    icons: dict, 
    n_largest: int = 10, 
    colors: list | None = None, 
    palette: str | None = 'viridis'
) -> None:
    """
    Draw a single frame for the animated time series bar chart.

    This function renders one step (frame) of the animation, showing the top entities 
    at the specified time (or index), along with optional color palette and icons.

    Parameters
    ----------
    ax : plt.Axes
        Matplotlib Axes where the bars will be drawn.
    df : pd.DataFrame
        Dataset containing at least the columns 'dt', 'label', and 'x'.
    title : str
        Title to display above the plot for the current frame.
    frame : int
        Current frame identifier (e.g., year or time period).
    icons : dict
        Mapping of label names → PIL.Image.Image objects for use in the chart.
    n_largest : int, optional
        Number of top items to display per frame (default is 10).
    colors : list, optional
        Explicit list of colors for the bars. If None, the palette is used instead.
    palette : str, optional
        Seaborn or Matplotlib palette name (default is 'viridis').

    Returns
    -------
    None
    """
    ax.clear()
    setup_plotstyle(ax)
    setup_dt(ax, frame)
    frame_data = df[df['dt'] == frame]
    top_items = frame_data.nlargest(n_largest, 'x')

    if colors is not None:
        ax.barh(y=top_items['label'], width=top_items['x'], color=colors, edgecolor='none')
    else:
        sns.barplot(x='x', y='label', data=top_items, hue='label', legend=False, palette=palette, ax=ax)

    wrap_labels(ax, width=18)

    for label in ax.get_yticklabels():
        label.set_ha('right')
        label.set_x(-0.014)
        label.set_fontweight('bold')

    for _, row in top_items.iterrows():
        ax.text(row['x'], row['label'], f'{row["x"]:.2f}', va='center', color='black')

    add_icons(ax, icons)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title(f"{title}", fontsize=18, fontweight='bold')


def setup_plotstyle(ax: plt.Axes) -> None:
    """
    Apply a clean and minimalistic visual style to a Matplotlib Axes.

    This helper removes unnecessary chart borders and ticks to highlight 
    the animated bars and reduce visual clutter.

    Parameters
    ----------
    ax : plt.Axes
        The plot axes to style.

    Returns
    -------
    None
    """
    sns.set_style("whitegrid")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('none')
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.tick_params(axis='y', which='both', left=False, right=False)


def wrap_labels(ax: plt.Axes, width: int | float = 12) -> None:
    """
    Automatically wrap y-axis labels that exceed a given character width.

    This ensures long category names are displayed across multiple lines 
    instead of overflowing the chart area.

    Parameters
    ----------
    ax : plt.Axes
        The plot axes containing the y-axis labels.
    width : int or float, optional
        Maximum character width before wrapping (default is 12).

    Returns
    -------
    None
    """
    labels = [t.get_text() for t in ax.get_yticklabels()]
    wrapped_labels = [textwrap.fill(label, width) for label in labels]
    ax.set_yticklabels(wrapped_labels)


def setup_dt(ax: plt.Axes, dt: int) -> None:
    """
    Display the current frame label (e.g., year or date) on the chart.

    The label is drawn as text within the plot area, typically in the 
    bottom-right corner.

    Parameters
    ----------
    ax : plt.Axes
        The plot axes.
    dt : int
        Current frame identifier (e.g., year or time index).

    Returns
    -------
    None
    """
    ax.text(0.9, 0.05, str(dt), transform=ax.transAxes,
            ha='center', color="#0B0101", fontsize=15)


def save_animation(
    df: pd.DataFrame,
    frames: list | np.ndarray | pd.Series,
    icons: dict,
    file_format: str = 'mp4',
    output_path: str = os.path.dirname(os.path.abspath(__file__)),
    title: str = None,
    width: int | float = 12,
    height: int | float = 6,
    fps: int = 10,
    n_largest: int = 10,
    palette: str | None = 'viridis'
) -> None:
    """
    Generate and save a horizontal bar chart time series animation.

    The animation visualizes how the top N items evolve over time and 
    saves it to disk as an MP4 or GIF file using `ffmpeg`.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset containing at least 'dt', 'label', and 'x' columns.
    frames : list or np.ndarray or pd.Series
        Sequence of frame identifiers (e.g., years or timestamps).
    icons : dict
        Mapping of labels → PIL.Image.Image objects for icons.
    file_format : str, optional
        File format for output ('mp4' or 'gif'). Default is 'mp4'.
    output_path : str, optional
        Directory where the file will be saved (default: current directory).
    title : str, optional
        Title displayed on each animation frame.
    width : int or float, optional
        Figure width in inches (default is 12).
    height : int or float, optional
        Figure height in inches (default is 6).
    fps : int, optional
        Frames per second for the output video (default is 10).
    n_largest : int, optional
        Number of top items to display (default is 10).
    palette : str, optional
        Color palette for Seaborn bars (default is 'viridis').

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(width, height))

    def animate(frame):
        frame_data = df[df['dt'] == frame]
        top_items = frame_data.nlargest(n_largest, 'x')
        colors = top_items['color'].tolist() if 'color' in top_items.columns else None
        draw_frame(ax, df, f"{title}", frame, icons, n_largest=n_largest, colors=colors, palette=palette)
        return []

    anim = FuncAnimation(fig, animate, frames=frames, interval=200)
    print(f"Saving animation as {file_format}...")
    anim.save(os.path.join(output_path, f"animation.{file_format}"), writer="ffmpeg", fps=fps)
    print(f"Animation saved as animation.{file_format}")


def show_animation(
    df: pd.DataFrame,
    frames: list | np.ndarray | pd.Series,
    icons: dict,
    title: str = None,
    width: int | float = 12,
    height: int | float = 6,
    fps: int = 10,
    n_largest: int = 10,
    palette: str | None = 'viridis'
) -> None:
    """
    Display the animated time series bar chart interactively.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset containing 'dt', 'label', and 'x' columns.
    frames : list or np.ndarray or pd.Series
        Sequence of frame identifiers (e.g., years).
    icons : dict
        Mapping of label → PIL.Image.Image for icons.
    title : str, optional
        Plot title for each animation frame.
    width : int or float, optional
        Figure width in inches.
    height : int or float, optional
        Figure height in inches.
    fps : int, optional
        Interval between frames in milliseconds (default 10).
    n_largest : int, optional
        Number of bars per frame (default 10).
    palette : str, optional
        Seaborn or Matplotlib color palette.

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(width, height))

    def animate(frame):
        frame_data = df[df['dt'] == frame]
        top_items = frame_data.nlargest(n_largest, 'x')
        colors = top_items['color'].tolist() if 'color' in top_items.columns else None
        draw_frame(ax, df, f"{title}", frame, icons, n_largest=n_largest, colors=colors, palette=palette)
        return []

    anim = FuncAnimation(fig, animate, frames=frames, interval=fps)
    plt.show()


if __name__ == "__main__":
    data_path = './data/clean-formatted-data.csv'
    icons_path = './icons'
    file_format = 'gif'
    output = os.path.dirname(os.path.abspath(__file__))
    title = "Top 10 Populations in the World Prediction"
    fps = 12
    width = 12
    height = 8
    n_largest = 10
    palette = 'viridis'

    df = pd.read_csv(data_path)
    frames = df['dt'].unique().tolist()
    icons = load_icons(df, icons_path, label_col='label')

    p = Process(target=save_animation, args=(df, frames, icons, file_format, output, title, width, height, fps))
    p.start()
    show_animation(df, frames, icons, title=title, width=width, height=height, fps=fps)
    p.join()