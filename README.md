
# Dynamic Layer Attribute Mapper

## Overview

Dynamic Layer Attribute Mapper is a QGIS plugin designed to combine vector layers using dynamic attribute field mapping.

It allows users to append features from a source vector layer into a target vector layer by mapping source fields to corresponding target fields.

## Features

- Select source and target vector layers.
- Dynamically add and remove field mapping rows.
- Map source attributes to target attributes using dropdown lists.
- Append source features to the target layer.
- Preserve existing target features.
- Transform source geometries to the target layer CRS.
- Save the resulting layer as a GeoPackage.

## Requirements

- QGIS 3.44 or later.
- Polygon vector layers.
- Valid source-to-target attribute mappings.

## Installation

1. Download the plugin ZIP package.
2. Open QGIS.
3. Navigate to Plugins → Manage and Install Plugins.
4. Select Install from ZIP.
5. Browse to the downloaded ZIP file.
6. Click Install Plugin.

## Usage

1. Load the source and target polygon layers into QGIS.
2. Open Dynamic Layer Attribute Mapper from the plugin menu.
3. Select the source layer.
4. Select the target layer.
5. Add the required attribute mapping rows.
6. Choose the corresponding source and target fields.
7. Select the output GeoPackage location.
8. Run the tool.
9. Verify the resulting feature count and attributes.

## Output

The plugin creates a new GeoPackage containing the existing target features and appended source features.

The original input layers are not modified.

## Author

Gomathi

## Repository

https://github.com/gomathi5222/Dynamic-Layer-Attribute-Mapper

## License

GNU General Public License v2.0 or later (GPL-2.0-or-later)
