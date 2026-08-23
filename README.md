# PyGCEditor

PyGCEditor is a desktop editor for EAWX Galactic Conquest campaign sets. It
loads planets, factions, trade routes, campaigns, and starting forces from an
Empire at War mod data folder and can export edited campaign XML.

## Requirements

- Windows, Linux, or macOS
- Python 3.10 or newer
- A mod data directory containing the expected EAWX XML files

## Installation

From the repository directory, create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration

Edit `config.xml` before starting the editor. The main settings are:

- `ModPath`: base mod directory. The editor loads its `Data` subdirectory.
- `Submod`: optional entries in ascending priority order. Each entry can be a
	submod folder name relative to `ModPath`, or an absolute submod path. The
	editor loads each entry's `Data` subdirectory.
- `MaximumFleetMovementDistance`: distance used for automatic map connections.
- `StartingForcesLibraryURL`: path to the starting-forces CSV library.

The Options dialog can update these values while the editor is running.

## Running

Start using the configured `ModPath`:

```powershell
python main.py
```

Alternatively, provide a mod directory as the first argument:

```powershell
python main.py "C:\Path\To\Mod"
```

A loading dialog displays the active paths, progress, and Python log messages.
It closes automatically when loading finishes. Closing it during loading exits
the application. After startup, the log can be reopened from **Options > Show
Loading Log**.

## Controls

### File menu

- **Save**: save the selected campaign to a chosen XML file.
- **Import Default Forces**: import the configured starting-forces library into
	the selected campaign without saving.
- **Import Default Forces and Save**: import forces, then save the selected
	campaign to a chosen XML file.
- **Import Default Forces and Save (All GCs)**: import forces into all loaded
	campaigns and save campaigns configured to use default forces to their 
    original locations.
- **Set Data Folder**: load another mod data directory.
- **Quit**: close the editor.

### Edit menu

- **Undo** or `Ctrl+Z`: undo the most recent edit. Up to 20 edits are retained.

### Add menu

- **Galactic Conquest...**: create or edit campaign properties.
- **Trade Route...**: create a trade route by entering its name and endpoint
	planets.

### Options menu

- **Auto connection settings**: set the automatic planet-connection distance
	and hide or show those connections.
- **Configuration options**: edit the mod path, submods, starting-forces CSV,
	and automatic connection distance.
- **Show Loading Log**: reopen the loading and Python log dialog after startup.
- **Dark Map**: toggle the map-only dark background. Planet faction colours
	are preserved.

### Layout tab

- Select or deselect planets using the checklist.
- Use **Select All Planets** or **Deselect All Planets**.
- Filter planets with the search field.
- Select or deselect trade routes using the checklist.
- Use **Select All Trade Routes** or **Deselect All Trade Routes**.
- Right-click a planet in the checklist and choose **Change position** to edit
	its galactic coordinates.

### Forces tab

- Select a planet from the combo box to inspect its starting forces and stats.
- **Import Default Forces** replaces the selected campaign's starting forces
	with the configured library.

### Factions tab

- Select or deselect playable factions using the checklist.
- Review total planet and income counts by faction.

### Map controls

- Left-click a planet to select or deselect it.
- Right-click an active planet, then right-click another active planet to select
	an existing route or start creating a new one.
- Middle-click and drag to pan the map.
- Scroll the mouse wheel to zoom around the cursor.
- Hover over any planet to see its information and possible connected routes.

The Matplotlib navigation toolbar also provides its standard view-history,
pan, zoom, and save-figure controls. **Home** resets the map view.

## Tests

Run the test suite with:

```powershell
python -m pytest -q
```
