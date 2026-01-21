# Initial Set-Up

This document describes how the `joa-qartod-config` repository was configured for development work. To use the package, see [Workflow](./workflow.md).


## GitHub

Made a new repo in GitHub. I cannot write to https://github.com/JOASurveys, so I'm working in my own account for the moment. It can be transfered to JOA later.

This repo is **public** so that it can be cloned into Google Colab Notebook VMs without fancy permissions. Therefore, this repo should only commit simple functions that do not require access to proprietary information. In the future, if sensitive information is added, `joa-qartod-config` should be converted to a private repo. In that case, there are many ways of giving Colab access. Here is a rundown of methods I found; options come and go, so check what the current options are before diving in.

1. GitHub Personal Access Token (PAT) provides access to an individual person with a GitHub account. The token is created in GitHub and then copied into a Colab secret, which is then used with `oauth2`:

```python
from google.colab import userdata
PAT = userdata.get('PAT')
!git clone https://oauth2:{PAT}@github.com/eldobbins/eldobbins-colab-testing.git
```

2. GitHub allows SSH [Deploy Keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys) to allow access to a repo to anyone with the key. The key is generated in the Colab VM and then copied into GitHub. Since the VM is ephermal, some fussing is required to ensure the key remains. See [colab-github](https://github.com/tsunrise/colab-github) as an example.

3. GitHub says deploy keys [are not secure](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys#deploy-keys) and suggests making a [GitHub App](https://docs.github.com/en/apps/overview) instead. IThis looked like overkill to me, so I did not explore it.

4. Colab can have access to a GitHub account with all the accompanying permissions. But again, that is for an individual, and not and organization. I felt uncomfortable given such sweeping access, so I did not explore it. [Colab's example](https://colab.research.google.com/github/googlecolab/colabtools/blob/master/notebooks/colab-github-demo.ipynb).

5. You could upload the code into Google Drive (for desktop) and then mount its location in the Notebook. The extra steps involved in this would provide lots of ways for the code to get out of sync, so I did not explore it.


## UV package management

I expect that there will be many modules of different types we will want to access individually from the Notebooks, rather than a single entry point. So I'm going with the "package" `uv` intialization.

```shell
$ uv init --package
$ uv sync
$ source .venv/bin/activate
(joa-qartod-config) $ uv add pandas
(joa-qartod-config) $ uv add sqlalchemy
(joa-qartod-config) $ uv add mysql-connector-python
(joa-qartod-config) $ uv add ioos-qc
(joa-qartod-config) $ uv add python-dotenv
(joa-qartod-config) $ uv add "ipywidgets>=7,<8"
```

Using ipywidgets, I cannot seem to avoid installing Jupyter even though everything will eventually be used in Colab where Jupyter isn't needed. Instead, I start it up as needed with: (Note: `uvx` would ignore the existing environment, so I use `uv run` instead.)

```shell
(joa-qartod) $ uv run --with bokeh jupyter lab
```

I was having some trouble getting code to produce the same output in Colab and a local Jupyter server using JupyterLab, because Colab branched Jupyter before a new architecture was implemented for JupyterLab 3.0. For instance, "classic" Notebooks and Colab do not need jupyter-bokeh as a link between Bokeh's JavaScript output and Jupyter's Python, but JupyterLab does. See [Bokeh's User Guide](https://docs.bokeh.org/en/latest/docs/user_guide/output/jupyter.html) for more information.

### Development Environment

Add pytest as an optional dependency in a separate group.

```
$ uv add pytest --optional testing
$ uv sync --all-extras  # or
$ uv sync --extra testing
```

### Package installation

So the Notebooks can access the code, install the package with `-e` for editable. Then test it.

```
(joa-qartod-config) $ uv pip install -e .
(joa-qartod-config) $ joa-qartod-config
Hello from joa-qartod-config!
```

## Development Tools

### Pre-commit

Following the example of `joa-qartod`, I'm using `pre-commit` and `ruff` for syntax checking (not using isort or mypy). These are already installed on my machine, so:

```shell
(joa-qartod-config) $ pre-commit install
pre-commit installed at .git/hooks/pre-commit
(joa-qartod-config) $ cp ../joa-qartod/.pre-commit-config.yaml .
(joa-qartod-config) $ pre-commit autoupdate
(joa-qartod-config) $ pre-commit run
```

### Ruff

Ruff is configured in pyproject.py.

- Ruff doesn't like print statements. To ignore that, add  ` # noqa: T201` to the end of the print line
- Internet says `ruff` sometimes doesn't sort imports, but it did for me.


### Pytest

Tests are in ./tests/ to separate them from the code. The configuration is in pyproject.py as [tool.pytest.ini_options] rather than in a separate pytest.ini file because that is what the [Scientific Python Library Development Guide](https://learn.scientific-python.org/development/guides/pytest/#testing-with-pytest) did. testpath is set to only tests/ so tests in other places should be ignored.


## Colab

### Local Development

Notebooks must work the same locally (for local database access) and in Colab (a the desired product for JOA).

There is a bug in Colab with ipywidgets 8.0.8 that treats my code as a "third party widget". It disables the slider bars. For these to work, the dependencies must be fixed to "ipywidgets>=7,<8". This limits the version of jupyter-bokeh to v3 because the newest version relies on ipywidgets v8. So I've got ipywidgets in the requirements, and import bokeh when starting a local Notebook. Colab should work OK.

### Running Colab with local kernel

To test with a local database, I had to either make the database available via the internet, or run the Colab Notebook locally. I chose the latter option. To do that,

1. Start up a Jupyter service with `uv run --with jupyter-bokeh jupyter lab` (or whatever)

2. One of the lines output to the screen by the startup looks like `http://localhost:8888/lab?token=63dfab2d6732c07fd65d1a2838efc17bc064a041b1a7924f`  This is the backend URL. Copy that.

3. Start up a Colab Notebook. In the upper right (below the Share button), is the access to the runtimes. Click the down menu icon next to "Connect" and choose "Connect to a local runtime".

4. Paste the backend URL into the resulting dialog box. Click connect. "Connected (Local)" with a green checkmark should appear.

Here are some things to note:

- Your current working directory will be the directory in which you started Jupyter on your local machine. The contents of that directory will show up in Colab Files (interface on the left)

- You are running in your local environment and will have all the packages already installed there (because you started the Jupyter server with `uv run`).
  - You lose access to Colab secrets.
  - You lose access to the `google` library, so no more `from google.colab import userdata`.

- If you want to install another package, use some command line magic like `!uv pip install -e ../joa-qartod/`


### Integration with GitHub package
No need to install uv because that is now included in the VM. You can dive right in!

```python
!git clone https://github.com/eldobbins/joa-qartod-config.git
# Install the package in editable mode using the --system flag
!uv pip install --system -e joa-qartod-config
# test that it works. Should return the uv default set-up "Hello from joa-qartod-config!"
!joa-qartod-config

# for some reason it needs this extra nudge or it can't find the module
import site
for sitepackages in site.getsitepackages():
    site.addsitedir(sitepackages)
```

The --system flag is necessary because Colab runs in a non-standard environment where uv cannot easily create its typical virtual environments. -e is for editable.

You also need to do this for IOOS-QARTOD because that is not in the Colab environment. If you use the other form, `from ioos_qc.config import Config` will fail with `ModuleNotFound`.
```python
!git clone https://github.com/ioos/ioos_qc
!python -m pip install ioos_qc
```

## More Info

- [example of Colab secrets](https://colab.research.google.com/github/aisawanj/Example_using_Secrets_in_Google_Colab/blob/main/Example_using_Secrets_in_Google_Colab.ipynb#scrollTo=GAbo80dWui2t)
- [ways of getting custom code into the VM](https://www.geeksforgeeks.org/techtips/how-to-import-custom-modules-in-google-colab/)
