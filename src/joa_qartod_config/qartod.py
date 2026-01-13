from __future__ import annotations

import ipywidgets as widgets
import simplejson as json
from ioos_qc.results import collect_results
from ioos_qc.streams import PandasStream
from IPython.display import display
from ipywidgets import HBox, Label, VBox


def run_qartod(data, context_configs):
  # Convert the data to a Stream (Pandas dataframe to a PandasStream)
  pandas_stream = PandasStream(data)

  # Pass the run method the config to use
  results = pandas_stream.run(context_configs)

  # Then collect all the results into a single list
  return collect_results(results, how="list")


def make_config_dict(gross_range_fail, gross_range_suspect, rate_of_change_threshold):
  """ To add parameters to a QARTOD configuration dictionary """
  return {
    "streams": {
      "rh": {
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


def config_generator ():
  """ Use Jupyter Widgets (sliders) to set configuration parameters for QARTOD """

  # two interdependent sliders for the gross range tests
  caption1 = widgets.Label(value='Gross Range Test Parameters')
  gr_fail = widgets.FloatRangeSlider(
      value=[5, 50.0],
      min=0,
      max=100.0,
      step=0.1,
      readout=True,
      readout_format='.1f',
  )
  gr_suspect = widgets.FloatRangeSlider(
      value=[10, 40.0],
      min=0,
      max=100.0,
      step=0.1,
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
  caption2 = widgets.Label(value='\n\nRate of Change Test Threshold')
  rate_of_change = widgets.FloatSlider(
      value=0.1,
      min=0,
      max=1,
      step=0.01,
      readout=True,
      readout_format='.1f',
  )

  # arrange the 3 sliders in the Notebook cell
  display(VBox([caption1, top_slider, bottom_slider,
                caption2, rate_of_change]))

  # make a button that copies the configuration string into a new widget
  # # in order to share the string with the calling Notebook
  output_text = widgets.Text(description="empty")  # value of this will hold the configuration
  button = widgets.Button(description="Generate Config")
  output = widgets.Output()  # this allows a status message to the Notebook

  def on_button_clicked(b): # noqa: ARG001
    # Display the message within the output widget.
    with output:
      config = make_config_dict(gr_fail.value, gr_suspect.value, rate_of_change.value)
      output_text.value = json.dumps(config)  # value of Text must be a string
      print('Configuration is: ', output_text.value) # noqa: T201

  button.on_click(on_button_clicked)
  display(button, output)
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
