from __future__ import annotations

import numpy as np
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show


def plot_results(data, var_name, collected_results, title, test_name):
    """Plot original data together with quality flags"""
    # create a ColumnDataSource by passing the dataframe of original data
    source = ColumnDataSource(data=data)

    # add flags to the data structure Bokeh uses
    context_result = next(r for r in collected_results if r.stream_id == var_name and r.test == test_name)
    qc_test = context_result.results
    source.data["qc_pass"] = np.ma.masked_where(qc_test != 1, data[var_name])
    source.data["qc_suspect"] = np.ma.masked_where(qc_test != 3, data[var_name])
    source.data["qc_fail"] = np.ma.masked_where(qc_test != 4, data[var_name])
    source.data["qc_notrun"] = np.ma.masked_where(qc_test != 2, data[var_name])

    # set-up the figure
    p1 = figure(x_axis_type="datetime", title=test_name + " : " + title)
    p1.grid.grid_line_alpha = 0.3
    p1.xaxis.axis_label = "Time"
    p1.yaxis.axis_label = "Observation Value"

    p1.line(x="time", y=var_name, source=source, legend_label="obs", color="#A6CEE3")
    p1.scatter(
        x="time",
        y="qc_notrun",
        source=source,
        size=2,
        color="gray",
        alpha=0.2,
        legend_label="qc not run",
    )
    p1.scatter(
        x="time",
        y="qc_pass",
        source=source,
        size=4,
        color="green",
        alpha=0.5,
        legend_label="qc pass",
    )
    p1.scatter(
        x="time",
        y="qc_suspect",
        source=source,
        size=4,
        color="orange",
        alpha=0.7,
        legend_label="qc suspect",
    )
    p1.scatter(
        x="time",
        y="qc_fail",
        source=source,
        size=6,
        color="red",
        alpha=1.0,
        legend_label="qc fail",
    )

    show(gridplot([[p1]], width=800, height=400))
