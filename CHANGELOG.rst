Changelog
=========


0.6.1
-----

New
~~~
- Include CHANGELOG in the package distribution. [Marek Cermak]

Changes
~~~~~~~
- Use .rst for CHANGELOG. [Marek Cermak]

Fix
~~~
- Fixed multiple action buttons after reload. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/extension.js
  modified:   jupyter_require/static/loader.js


v0.6.0 (2019-12-03)
-------------------

New
~~~
- Added Makefile. [Marek Cermak]
- Added .gitchangelog.rc. [Marek Cermak]
- Reload extension when the kernel is reloaded. [Marek Cermak]


v0.5.0 (2019-11-27)
-------------------

Changes
~~~~~~~
- Refactor RequireJS to singleton pattern. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py


v0.4.3 (2019-11-23)
-------------------

New
~~~
- Give more descriptive comm error output. [Marek Cermak]


v0.4.2 (2019-10-26)
-------------------

New
~~~
- Finish execution only on matching msg id. [Marek Cermak]

Changes
~~~~~~~
- Include shell reply execution check. [Marek Cermak]


v0.4.1 (2019-10-26)
-------------------

Fix
~~~
- Use iopub channel for execution finish. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/loader.js


v0.4.0 (2019-10-26)
-------------------

Fix
~~~
- Fix immature execution finish. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/loader.js


v0.3.3 (2019-10-03)
-------------------
- Ensure target 'loader.js' [Marek Cermak]
- Logging. [Marek Cermak]
- Loader and initial logging setup. [Marek Cermak]

  Implement a common logging functionality

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/extension.js
  new file:   jupyter_require/static/loader.js
  new file:   jupyter_require/static/logger.js
  modified:   setup.py
- Scope the __extension__ variable. [Marek Cermak]


v0.3.2 (2019-09-28)
-------------------
- Update README. [Marek Cermak]


v0.3.1 (2019-09-28)
-------------------
- Autoloading. [Marek Cermak]

  - the extension now loads automatically into the ipython context ---
  is available without issuing the `%load_ext` command
  - implemented silent mode to execute scripts without the need of the
  cell context

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   jupyter_require/magic.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js
- [WIP] Autoloading. [Marek Cermak]
- Update issue templates. [Marek Čermák]
- Update issue templates. [Marek Čermák]
- Update issue templates. [Marek Čermák]
- Update issue templates. [Marek Čermák]
- Include requirements.txt in sdists. [Todd]

  sdists cannot be installed without it


v0.3.0 (2019-07-23)
-------------------
- Trigger events before and after finalization. [Marek Cermak]

  This allows to distinguish between notebook native save and
  JupyterRequire cell finalization.
- Avoid deadlock on requirejs module loading error. [Marek Cermak]
- No need to use RegExp in syntax highlighting. [Marek Cermak]
- Fix syntax highlighting. [Marek Cermak]
- Change regex for syntax highlighting to `requirejs` [Marek Cermak]


v0.2.6 (2019-06-23)
-------------------
- API changes: [Marek Cermak]

  - core:
      - `require.config(libs, shim)` -> `require.config(paths, shim)`

  - magic:
      - `%require`  -> `%requirejs`
      - `%%require` -> `%%requirejs`
      - `%reload`   -> `%reloadjs`

  All of the above changes were made to reduce ambiguity in those commands
  and provide more user comfort.

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/core.py
  modified:   jupyter_require/magic.py
- Fix `link_js` script existence check. [Marek Cermak]
- Fix syntax highlighting in %%require cells. [Marek Cermak]
- Add `get_executed_cell` to Notebook prototype. [Marek Cermak]
- Pass context to the script being executed. [Marek Cermak]

  Context is by default the current cell being executed and the output area.

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/display.js
- Fix `link_js` invalid condition. [Marek Cermak]
- Turn `requrie` into line_cell_magic. [Marek Cermak]
- Remove empty parameters from AsyncFunction. [Marek Cermak]
- Remove Pipfile.lock. [Marek Cermak]

  The dependencies should be resolved and locked on the client side
  instead of pinning them down in the source.


v0.2.5 (2019-05-08)
-------------------
- Jupyter-tools has become jupyter-nbutils package. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/magic.py
  modified:   Pipfile
  modified:   requirements.in
  modified:   requirements.txt
  modified:   setup.py
  modified:   README.rst
- Fix typo in %%define. [Marek Cermak]


v0.2.4 (2019-04-24)
-------------------
- Do not re-throw a script error to prevent kernel crash. [Marek Cermak]


v0.2.3 (2019-06-23)
-------------------
- Magic to define new modules in-place. [Marek Cermak]
- Magic to reload linked libraries. [Marek Cermak]
- Do not re-link already linked styles and scripts. [Marek Cermak]
- Don't forget to pop library from LIBS on undef. [Marek Cermak]
- Magic to undefine linked modules. [Marek Cermak]
- Add cell magic to execute JS script directly. [Marek Cermak]

  %%require [REQUIREMENTS] is a new cell magic which executes given script
  with specific requirements and provides syntax highlighting

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   Pipfile
  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   jupyter_require/magic.py
  modified:   setup.py


v0.2.2 (2019-04-14)
-------------------
- Rename magic to comply with python API. [Marek Cermak]
- Fix incorrect imports and typo in requirements. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/magic.py
  modified:   requirements.txt
- Add option to compress CSS before loading. [Marek Cermak]

  defaults to True

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   Pipfile
  modified:   Pipfile.lock
  modified:   jupyter_require/notebook.py
  modified:   jupyter_require/static/extension.js
  modified:   requirements.txt
- Move utilities from core to notebook module. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   jupyter_require/notebook.py
- Link font awesome CSS and fix invisible icon. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/static/extension.js


v0.2.1 (2019-04-11)
-------------------
- Fix install instructions. [Marek Cermak]
- Link font awesome CSS on nbextension initialization. [Marek Cermak]

  Custom shield icon requires fontawesome to be loaded before actual magic
  is called from the notebook

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/static/extension.js
- Do not throw error if comm is not defined yet. [Marek Cermak]


v0.2.0 (2019-04-04)
-------------------
- Dependency maintenance. [Marek Cermak]

  Removed pinned versions from requirements.txt -- Let @Thoth resolve it ;)

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   Pipfile.lock
  modified:   requirements.txt
- Modify install instructions in README.rst. [Marek Cermak]
- Wait for kernel and handle invalid user script. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js
- Clean requirements properly in require.reload() [Marek Cermak]
- Format error messages instead of returning objects. [Marek Cermak]

  - shuffle a bit with timeouts
- Check if output has metadata. [Marek Cermak]

  Error cells do not define metadata
- Refactor core.py and stringify error traceback. [Marek Cermak]

  - use more intuitive parameter names

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
- Fix reload with clear=True. [Marek Cermak]
- JSON.stringify error object. [Marek Cermak]
- Fix `load_js` duplicated script parameter. [Marek Cermak]
- Fix README extension in MANIFEST.in. [Marek Cermak]
- Remove leftover from preparation to node migration. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  deleted:    js/src/core.js
  deleted:    js/src/events.js
  deleted:    js/src/extension.js
- Update description. [Marek Cermak]
- Update README to reflect utils migration. [Marek Cermak]
- Move utils module to jupyter-tools. [Marek Cermak]

  Prevent unnecessary loading errors by moving the utils module to
  jupyter-tools.

  jupyter-tools: https://github.com/CermakM/jupyter-tools
- Correct links in the resource table. [Marek Cermak]
- Replace raw directive. [Marek Cermak]

  PyPI does not support raw directive
- Correct spelling grammar using grammarly. [Marek Cermak]

  grammarly: https://app.grammarly.com/
- Change content type for PyPI to render properly. [Marek Cermak]
- Rename to README.rst for GitHub to parse correctly. [Marek Cermak]

  - stylistic changes for GitHub parsers
  - Change .md to .rst in setup.py

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  renamed:    README -> README.rst
  new file:   docs/images/readme_example.svg
  modified:   setup.py
- Remove README.md. [Marek Cermak]
- Migrate README to .rst. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  new file:   README
  modified:   README.md
- Update README.md. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   README.md
  modified:   jupyter_require/__init__.py
- Isolate scope of embedded safe scripts. [Marek Cermak]


v0.1.22 (2019-03-27)
--------------------
- Finalize only once and select valid code cells. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/display.js
  modified:   jupyter_require/static/extension.js


v0.1.21 (2019-03-27)
--------------------
- Utilities to install jupyter-require extension. [Marek Cermak]

  This utilities are meant to assist user in installing extensions without
  the need of jupyter-require, or installing the jupyter-require extension
  itself.


v0.1.20 (2019-03-27)
--------------------
- Position the action button and change icon. [Marek Cermak]
- Introduce Save and Finalize action button. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js
- Refactor Python-JS communication and logging. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js


v0.1.19 (2019-03-27)
--------------------
- Refactor Python-JS communication and logging. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js


v0.1.18 (2019-03-26)
--------------------
- Set correct output area element width. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/display.js
  modified:   jupyter_require/static/extension.js


v0.1.17 (2019-03-26)
--------------------
- Bidirectional communication. [Marek Cermak]

  Jupyter fronten can now communicate to JR kernel and notifies it about
  certain events, like application reload, which can be used for example
  for re-initializing comms.

  Comms now survive window refreshes.

  Simple logging using daiquiri -- new requirement introduced.

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   Pipfile
  modified:   Pipfile.lock
  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js
  modified:   requirements.in
  modified:   requirements.txt


v0.1.16 (2019-03-25)
--------------------
- Implement `safe_execute` method for persistent scripts. [Marek Cermak]

  Safe scripts are executed on cell creation
  and are therefore not allowed to have any requirements.
  Scripts executed with this method also persist through notebook
  reloads and are automatically loaded on app initialization.

  This function is convenient for automatic loading and linking
  of custom CSS and JS files.

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/core.py
  modified:   jupyter_require/notebook.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/display.js
  modified:   jupyter_require/static/extension.js


v0.1.15 (2019-03-25)
--------------------
- Outputs are saved on kernel related events and proper close. [Marek
  Cermak]

  If notebook is closed properly (close and halt), then outputs are
  finalized and stored. Outputs, however, do not survive for example
  SIGKILL.

  TODO: Create action button which explicitly finalizes the outputs

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/display.js
  modified:   jupyter_require/static/extension.js
- Enable copy/pasting for jupyter-require cells. [Marek Cermak]

  - outputs are not preserved untill finalization

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/display.js
  modified:   jupyter_require/static/extension.js
- Persistens outputs in static frozen state. [Marek Cermak]

  Any cells in frozen state can be copied over and they preserve metadata
  and the current state of the output as a static HTML.

  TODO: Use the metadata to re-execute script to relaod the dynamic state

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/display.js
  modified:   jupyter_require/static/extension.js
- Freeze and store cell output on save event. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/display.js
  modified:   jupyter_require/static/extension.js
- Selected correct cell for requirement metadata. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js
- Store outputs as display metadata. [Marek Cermak]

  Output and execution partial is stored in outputs metadata, the
  partial is convenient function which can be executed in different cell
  contexts

  The outputs metadata schema:

  ```json
  metadata: {
      "display": {
  	"application/javascript": Function,
  	"text/html": Element
      }
  }
  ```

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  deleted:    jupyter_require/static/event_manager.js
  new file:   jupyter_require/static/display.js
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js
  modified:   setup.py
- Remove event manager completely. [Marek Cermak]

  - refactor core
  - register events after notebook has been loaded

  - [WIP] cell metadata to preserve output

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/static/core.js

  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/event_manager.js
  modified:   jupyter_require/static/extension.js
- Refactor event manager. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  renamed:        jupyter_require/static/events.js -> jupyter_require/static/event_manager.js

  modified:       jupyter_require/core.py
  modified:       jupyter_require/static/core.js
  modified:       jupyter_require/static/extension.js
  modified:       setup.py
- Replace `display` with `execute_with_requirements` [Marek Cermak]


v0.1.14 (2019-03-22)
--------------------
- Custom async execution and output. [Marek Cermak]

  Output into the cell which is being currently executed --
  jupyter-require keeps track of execution and marks running cells.

  This functionality has been made possible by extending Notebook class by
  `get_running_cells` and `get_running_cells_indices`

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js
- [WIP] Custom async execution and output. [Marek Cermak]

  Use JSTemplate in core utility scripts.
- [WIP] Custom async execution and output. [Marek Cermak]

  Execute the user script in controled environment of the current cell with pre-defined global access and await the execution

  TODO: The 'current cell' is at this moment the selected cell, which is
  inapropriate as currently selected cell may not match executed cell at
  the execution time.
- [WIP] Custom async execution and output. [Marek Cermak]

  [target]: execute the user script in controled environment of the current
  cell with pre-defined global access and await the execution

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/core.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/extension.js


v0.1.13 (2019-03-17)
--------------------
- Execute JS scripts via comms. [Marek Cermak]

  - move JS scripts from templates to core.js

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/core.py
  modified:   jupyter_require/notebook.py
  modified:   jupyter_require/static/core.js
  modified:   jupyter_require/static/events.js
  modified:   jupyter_require/static/extension.js


v0.1.12 (2019-03-17)
--------------------
- Add module with common notebook utilities. [Marek Cermak]
- Set only non-empty requirement metadata. [Marek Cermak]
- Temporary fix before node.js migration. [Marek Cermak]

  - explicitly create static/ folder

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  new file:   jupyter_require/static/core.js
  new file:   jupyter_require/static/events.js
  new file:   jupyter_require/static/extension.js
  modified:   .gitignore
  modified:   Pipfile.lock


v0.1.11 (2019-03-16)
--------------------
- Conform to nbextension ipywidgets-like structure. [Marek Cermak]

  Enables installation by package manager without additional configuration
  and will allow for future node.js usage

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  new file:   MANIFEST.in
  new file:   jupyter-config/notebook.d/jupyter-require.json
  new file:   setup.cfg
  new file:   setupbase.py
  modified:   Pipfile
  modified:   Pipfile.lock
  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   setup.py

  modified:   jupyter_require/core.py
- [WIP] Conform to nbextension ipywidgets-like structure. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   .gitignore
  renamed:    jupyter_require/require/core.js -> js/src/core.js
  renamed:    jupyter_require/require/events.js -> js/src/events.js
  renamed:    jupyter_require/require/extension.js -> js/src/extension.js
- Include events module dependency in main extension file. [Marek
  Cermak]


v0.1.10 (2019-03-14)
--------------------
- Persistend requireJS requirements and cell updates. [Marek Cermak]

  - The required libraries persist through reloads and kernel restarts and
  are automatically reloaded on notebook startup
  - Cell states are updated as well

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   core.py
  modified:   require/core.js
  modified:   require/events.js
  modified:   require/extension.js
- [WIP] nbextension. [Marek Cermak]

  - communicate using events
  - store requirements in cell's metadata

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   core.py
  new file:   require/core.js
  new file:   require/events.js
  new file:   require/extension.js


v0.1.9 (2019-03-12)
-------------------
- Use jupyter comms and promises to await required libs. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  new file:   jupyter_require/js/core.js
  modified:   Pipfile
  modified:   Pipfile.lock
  modified:   jupyter_require/core.py


v0.1.8 (2019-03-11)
-------------------
- Allow additional attributes in link_css function. [Marek Cermak]


v0.1.7 (2019-03-08)
-------------------
- Fix typo in summary. [Marek Cermak]
- Fix require arguments. [Marek Cermak]
- Give timeout before loading libraries. [Marek Cermak]

  - TODO: pause python execution as well
- Get rid of spectate and call update manually. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   Pipfile
  modified:   README.md
  modified:   jupyter_require/__init__.py
  modified:   jupyter_require/core.py
  modified:   jupyter_require/magic.py
  modified:   requirements.in
  modified:   requirements.txt
- Move execute_js from jupyter_d3 to jupyter_require module. [Marek
  Cermak]

  - switch from traitlets to spectate
  - refactorings

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   Pipfile
  modified:   Pipfile.lock
  modified:   jupyter_require/core.py
  modified:   requirements.in
  modified:   requirements.txt
- Update README. [Marek Cermak]
- Fix setup.py to cope with PyPI. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   jupyter_require/__about__.py
  modified:   setup.py


v0.1.4 (2019-02-26)
-------------------
- Update README to reflect naming changing. [Marek Cermak]


v0.1.3 (2019-02-26)
-------------------
- Load modules directly after linking. [Marek Cermak]

  - refactor context method
  - implement display_context method
- Remove excessive print. [Marek Cermak]
- Rename package to jupyter_require to prevent clashes with require.
  [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  renamed:    require/__about__.py -> jupyter_require/__about__.py
  renamed:    require/__init__.py -> jupyter_require/__init__.py
  renamed:    require/core.py -> jupyter_require/core.py
  renamed:    require/magic.py -> jupyter_require/magic.py
  modified:   setup.py
- Fix typo in `require` [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   require/__init__.py
  modified:   require/core.py
- Link modules properly. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   require/__about__.py
  modified:   require/__init__.py
  modified:   require/core.py
  modified:   require/magic.py
- Refactorings. [Marek Cermak]


v0.1.2 (2019-02-26)
-------------------
- Update README. [Marek Cermak]
- Pass path properly and add setup calssifiers. [Marek Cermak]
- Move magic into separate module. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   require/__init__.py
  new file:   require/magic.py
  modified:   require/require.py


v0.1.0 (2019-02-26)
-------------------
- Add virtual environments to .gitignore. [Marek Cermak]
- Add requirements files. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  new file:   requirements.in
  new file:   requirements.txt
- Add setuptools and __about__ module. [Marek Cermak]

  - move to pre-alpha

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  new file:   require/__about__.py
  modified:   require/__init__.py
  new file:   setup.py
- Rename to jupyter-require. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  modified:   require/__init__.py
  modified:   require/require.py
- Ported from https://github.com/CermakM/jupyter-d3. [Marek Cermak]

  Signed-off-by: Marek Cermak <macermak@redhat.com>

  new file:   .gitignore
  new file:   Pipfile
  new file:   Pipfile.lock
  new file:   require/__init__.py
  new file:   require/require.py


