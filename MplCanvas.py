import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.gridspec as gridspec

class DataHolder:
    """
    A class to store the axes and associated data for each plot.
    attributes:
        ax: The axis of the plot.
        data: The data to be plotted (as a pandas DataFrame).
        paired: A boolean indicating if the data is paired.
        type: The type of plot (0 for line plot, 1 for scatter plot).
    """
    
    def __init__(self, ax: Axes, data: pd.DataFrame, paired=False, type=0):
        """
        Initializes a DataHolder instance with plot data and configurations.

        Args:
            ax: The axes object of the plot.
            data: The data (as a pandas DataFrame) to be plotted.
            paired: A boolean indicating if the data is paired (default is False).
            type: The plot type (0 for line plot, 1 for scatter plot) (default is 0).
        """
        self.ax = ax
        self.data = data
        self.paired = paired
        self.type = type

class MplCanvas(FigureCanvas):
    """
    A custom canvas for matplotlib figures that manages multiple plots.

    attributes:
        fig: The matplotlib figure.
        plots: A dictionary that maps plot names to their respective DataHolder.
        gs: The GridSpec object for managing subplot layout.
        MAX_COL: The maximum number of columns for subplots.
    """
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        constructs a figure canvas with specific dimensions and dpi.
        Args:
            parent: The parent widget (default is None).
            width: The width of the figure (default is 5).
            height: The height of the figure (default is 4).
            dpi: The dpi (dots per inch) for the figure (default is 100).
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi, label='h')
        self.plots: dict[str, DataHolder] = {}
        self.gs = gridspec.GridSpec(1, 1, self.fig)  # Initial GridSpec with 1x1 layout
        self.MAX_COL = 2  # Maximum number of columns for subplots
        super().__init__(self.fig)  # Initialize the figure canvas

    def get_ax(self, name):
        """
        Retrieves the axes for a specific plot by its name.
        Args:
            name: The name of the plot.
        Returns:
            The axes associated with the given plot name.
        """
        return self.plots[name].ax

    def add_plot(self, plot_name, data, paired=False, type=0):
        """
        Adds a new plot to the canvas.
        Args:
            plot_name: The name of the plot.
            data: The data (as a pandas DataFrame) to be plotted.
            paired: A boolean indicating if the data is paired (default is False).
            type: The plot type (0 for line plot, 1 for scatter plot) (default is 0).
        """
        # Create a new axes for the plot
        new_ax = 0
        if self.gs.ncols * self.gs.nrows >= len(self.plots) + 1:
            # If there's space in the current grid, use the next available subplot
            new_ax = self.fig.add_subplot(self.gs[len(self.plots)])
        else:
            # Otherwise, adjust the figure layout to accommodate more plots
            self.gs, new_ax = self.__adjust_figure()

        # Plot the data based on its type (paired or unpaired)
        self.__plot_paired(new_ax, data, type) if paired else self.__plot_unpaired(new_ax, data, type)

        # Format the plot (title, labels, etc.)
        self.format_plot(new_ax, plot_name)
        self.fig.tight_layout()  # Adjust layout to prevent overlap
        self.draw()  # Redraw the canvas to reflect changes

        # Store the plot in the plots dictionary
        self.plots[plot_name] = DataHolder(new_ax, data, paired, type)

    def update_plot(self, plot_name, data):
        """
        Updates an existing plot with new data.

        args:
            plot_name: The name of the plot to update.
            data: The new data (as a pandas DataFrame) to plot.
        """
        # Clear the existing axes
        self.plots[plot_name].ax.cla()

        # Retrieve the axes and plot type
        ax: Axes = self.plots[plot_name].ax
        type = self.plots[plot_name].type

        # Replot based on whether the data is paired or unpaired
        self.__plot_paired(ax, data, type) if self.plots[plot_name].paired else self.__plot_series(ax, data, type)
        self.format_plot(ax, plot_name)  # Reapply formatting

        # Redraw the axes
        ax.draw()

    def __adjust_figure(self):
        """
        Adjusts the figure layout by creating a new GridSpec to accommodate more subplots.
        returns:
            The new GridSpec object and the new axes for the next subplot.
        """
        # Get existing axes
        existing_axes = self.fig.get_axes()
        total_plots = len(existing_axes) + 1
        ncols = min(self.MAX_COL, total_plots)  # Limit columns to MAX_COL
        nrows = (total_plots + ncols - 1) // ncols  # Calculate the number of rows

        # Create a new GridSpec with the updated layout
        new_gs = gridspec.GridSpec(nrows, ncols, figure=self.fig)

        # Reposition existing axes
        for i, ax in enumerate(existing_axes):
            row, col = divmod(i, ncols)
            ax.set_subplotspec(new_gs[row, col])  # Move each axis to a new position

        # Add the new subplot
        new_ax = self.fig.add_subplot(new_gs[len(existing_axes)])
        self.gs = new_gs  # Update the GridSpec

        return new_gs, new_ax

    def __plot_paired(self, ax, data, type):
        """
        Plots paired data sets together on the given axis.
        Aargs:
            ax: The axis on which to plot the data.
            data: The data (as a pandas DataFrame) to plot.
            type: The plot type (0 for line plot, 1 for scatter plot).
        """
        pairs = detect_adjacent_pairs(data)  # Get pairs of adjacent columns
        for x, y in pairs:
            if type == 0:
                ax.plot(data[x], data[y], label=f'{x} vs {y}', marker='o')  # Line plot
            elif type == 1:
                ax.scatter(data[x], data[y], label=f'{x} vs {y}', alpha=0.7)  # Scatter plot

    def __plot_unpaired(self, ax, data, type):
        """
        Plots unpaired data sets on the given axis.
        args:
            ax: The axis on which to plot the data.
            data: The data (as a pandas DataFrame) to plot.
            type: The plot type (0 for line plot, 1 for scatter plot).
        """
        x_col = data.columns[0]  # The first column as the y-axis
        x = data[x_col]

        # Plot each remaining column against the y-axis
        for y in data.columns[1:]:
            if type == 0:
                ax.plot(x, data[y], label=f'{x_col} vs {y}', marker='o')  # Line plot
            elif type == 1:
                ax.scatter(x, data[y], label=f'{x_col} vs {y}', alpha=0.7)  # Scatter plot

    def format_plot(self, ax, name):
        """
        Applies formatting to the plot, such as title, labels, and grid.
        Args:
            ax: The axis to apply formatting to.
            name: The name of the plot to set as the title.
        """
        ax.set_title(name)
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.legend()
        ax.grid(True)

def detect_adjacent_pairs(df):
    """
    Detects pairs of adjacent columns in the DataFrame.
    args:
        df: The pandas DataFrame to detect pairs in.
    outputs:
        A list of tuples representing adjacent pairs of columns.
    """
    pairs = [(df.columns[i], df.columns[i + 1]) for i in range(0, len(df.columns), 2)]
    return pairs
