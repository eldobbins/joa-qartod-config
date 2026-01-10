from __future__ import annotations

from ioos_qc.results import collect_results
from ioos_qc.streams import PandasStream


def run_qartod(data, context_configs):
  # Convert the data to a Stream (Pandas dataframe to a PandasStream)
  pandas_stream = PandasStream(data)

  # Pass the run method the config to use
  results = pandas_stream.run(context_configs)

  # Then collect all the results into a single list
  return collect_results(results, how="list")
