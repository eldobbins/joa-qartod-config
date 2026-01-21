from __future__ import annotations

import math

import ipywidgets as widgets
import pandas as pd
import simplejson as json
from ioos_qc.config import Config
from ioos_qc.stores import PandasStore
from ioos_qc.streams import PandasStream
from IPython.display import display
from ipywidgets import HBox, Label, VBox


def run_qartod(data, configs):
  """ Run qartod on data in a Dataframe and return results appended to that dataframe.
  This mimics the use of QARTOD in joa-qartod, but is included here in case that package is
  not available.
  """
  # Convert the data to a Stream (Pandas dataframe to a PandasStream)
  pandas_stream = PandasStream(data)

  # Pass the run method the config to use
  results = pandas_stream.run(Config(configs))

  # store the results
  store = PandasStore(results)

  # Write only the test results to the store
  results_store = store.save(write_data=False, write_axes=False)

  # Append columns from qc results back into the data
  return pd.concat([data, results_store], axis=1)


def make_config_dict(stream, gross_range_fail, gross_range_suspect, rate_of_change_threshold):
  """ To add parameters to a QARTOD configuration dictionary """
  return {
    "streams": {
      stream: {
        "qartod": {
          "gross_range_test": {
              "fail_span": gross_range_fail,
              "suspect_span": gross_range_suspect,
          },
          "rate_of_change_test": {
              "threshold": rate_of_change_threshold
          },
        }
      }
    }
  }


def choose_stream():
  """Choose between representations of sea surface height
  ssl is relative to a datum and rh is not, so acceptable ranges will be different """
  choose_stream = widgets.Dropdown(
      options=['rh', 'sea_surface_height_above_sea_level'],
      value='rh',
      description='Stream:',
      disabled = False
  )

  display(choose_stream)
  return choose_stream


def config_generator(stream='rh',gr_span=(0,100), roc_max=1, qc_config=None):
  """ Use Jupyter Widgets (sliders) to set configuration parameters for QARTOD """

  # get slider limits from the arguments
  span_min = math.floor(gr_span[0])
  span_max = math.ceil(gr_span[1])
  # use values from a pre-existing configuration dictionary, if it exists
  fail_values = [span_min, span_max]
  suspect_values = [span_min, span_max]
  roc_value = roc_max
  if qc_config:
    roc_value = qc_config["streams"]["rh"]["qartod"]["rate_of_change_test"]["threshold"]
    fail_values = qc_config["streams"]["rh"]["qartod"]["gross_range_test"]["fail_span"]
    suspect_values = qc_config["streams"]["rh"]["qartod"]["gross_range_test"]["suspect_span"]

  # two interdependent sliders for the gross range tests
  caption1 = widgets.Label(value='Gross Range Test Parameters')
  gr_fail = widgets.FloatRangeSlider(
      value=fail_values,
      min=span_min,
      max=span_max,
      step=.1,
      readout=True,
      readout_format='.1f',
  )
  gr_suspect = widgets.FloatRangeSlider(
      value=suspect_values,
      min=span_min,
      max=span_max,
      step=.1,
      readout=True,
      readout_format='.1f',
  )
  top_slider = HBox([Label('Fail:'), gr_fail])
  bottom_slider = HBox([Label('Suspect:'), gr_suspect])

  # the range for suspect must be within the range for fail
  # so use an observer to update min and max of suspect based on the values chosen for fail
  # Function to update suspect range based on fail values
  def update_suspect(*args): # noqa: ARG001 because without this, the slides aren't linked
      gr_suspect.min, gr_suspect.max = gr_fail.value
  # Attach observer to fail slider
  gr_fail.observe(update_suspect, 'value')

  # a new slider for rate of change
  # aiming for the maximum possible on the high side of a base 10 log scale
  caption2 = widgets.Label(value='\n\nRate of Change Test Threshold')
  rate_of_change = widgets.FloatLogSlider(
    value=roc_value,
    base=10,
    min=math.log10(roc_max) - 2, # min exponent of base
    max=math.log10(roc_max) + .3, # max exponent of base
    step=0.1, # exponent step
  )

  # make a button that copies the configuration string into a new widget
  # # in order to share the string with the calling Notebook
  output_text = widgets.Text(description="empty")  # value of this will hold the configuration
  button = widgets.Button(description="Generate Config")
  output = widgets.Output()  # this allows a status message to the Notebook

  def on_button_clicked(b): # noqa: ARG001
    # Display the message within the output widget.
    with output:
      config = make_config_dict(stream, gr_fail.value, gr_suspect.value, rate_of_change.value)
      output_text.value = json.dumps(config)  # value of Text must be a string
      print('Configuration is: ', output_text.value) # noqa: T201

  button.on_click(on_button_clicked)
  # arrange the 3 sliders in the Notebook cell
  display(VBox([caption1, top_slider, bottom_slider,
                caption2, rate_of_change]),
                button,
                output)
  return output_text  # return the container widget to the calling Notebook

def foo():
  """ a test script for sending values back to the Notebook """
  slider = widgets.IntSlider(
      value=5,
      max=10,
      description='Value')
  display(slider)

  # 1. Create a widget to hold the output value
  output_text = widgets.Text(description="Result:")

  def on_button_clicked(b): # noqa: ARG001
      # 2. Update the value of the output widget
      output_text.value = json.dumps({"value": slider.value})

  button = widgets.Button(description="Process Data")
  button.on_click(on_button_clicked)

  # 3. Display the widgets
  display(button, output_text)

  # 4. Return the widget so it can be accessed by something else
  return output_text
