
from qgis.PyQt.QtWidgets import (
    QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit,
    QFileDialog, QMessageBox, QGroupBox, QWidget
)

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsVectorFileWriter,
    QgsWkbTypes
)

from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel


class DynamicLayerAttributeMapper:

    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):

        self.action = QAction(
            "Dynamic Layer Attribute Mapper",
            self.iface.mainWindow()
        )

        self.action.triggered.connect(self.show_dialog)

        self.iface.addPluginToMenu(
            "&Dynamic Layer Attribute Mapper",
            self.action
        )

        self.iface.addToolBarIcon(self.action)

    def unload(self):

        if self.action:
            self.iface.removePluginMenu(
                "&Dynamic Layer Attribute Mapper",
                self.action
            )

            self.iface.removeToolBarIcon(self.action)

    def show_dialog(self):

        dialog = AttributeMapperDialog(self.iface.mainWindow())
        dialog.exec()


class AttributeMapperDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Dynamic Layer Attribute Mapper")
        self.setMinimumWidth(650)

        self.mapping_rows = []

        self.layout_main = QVBoxLayout(self)

        # Target layer
        self.layout_main.addWidget(
            QLabel("1. Target Layer ")
        )

        self.target_layer = QgsMapLayerComboBox()
        self.target_layer.setFilters(
            QgsMapLayerProxyModel.Filter.PolygonLayer
        )

        self.layout_main.addWidget(self.target_layer)

        # Source layer
        self.layout_main.addWidget(
            QLabel("2. Source Layer")
        )

        self.source_layer = QgsMapLayerComboBox()
        self.source_layer.setFilters(
            QgsMapLayerProxyModel.Filter.PolygonLayer
        )

        self.layout_main.addWidget(self.source_layer)

        # Mapping group
        self.mapping_group = QGroupBox(
            "3. Dynamic Attribute Mapping"
        )

        self.mapping_layout = QVBoxLayout(
            self.mapping_group
        )

        self.layout_main.addWidget(self.mapping_group)

        # Mapping headings
        heading = QHBoxLayout()

        heading.addWidget(QLabel("Source Field"))
        heading.addWidget(QLabel("Target Field"))

        self.mapping_layout.addLayout(heading)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("+ Add Mapping")
        self.remove_button = QPushButton("- Remove Last")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        self.layout_main.addLayout(button_layout)

        # Output
        self.layout_main.addWidget(
            QLabel("4. Output GeoPackage")
        )

        output_layout = QHBoxLayout()

        self.output_path = QLineEdit()

        self.browse_button = QPushButton("Browse")

        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.browse_button)

        self.layout_main.addLayout(output_layout)

        # Run
        self.run_button = QPushButton(
            "Run"
        )

        self.layout_main.addWidget(self.run_button)

        # Connections
        self.add_button.clicked.connect(
            self.add_mapping_row
        )

        self.remove_button.clicked.connect(
            self.remove_mapping_row
        )

        self.browse_button.clicked.connect(
            self.browse_output
        )

        self.source_layer.layerChanged.connect(
            self.refresh_mapping_fields
        )

        self.target_layer.layerChanged.connect(
            self.refresh_mapping_fields
        )

        self.run_button.clicked.connect(
            self.run_process
        )

        # Initial row
        self.add_mapping_row()

    def add_mapping_row(self):

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)

        row_layout.setContentsMargins(0, 0, 0, 0)

        source_combo = QComboBox()
        target_combo = QComboBox()

        row_layout.addWidget(source_combo)
        row_layout.addWidget(target_combo)

        self.mapping_layout.addWidget(row_widget)

        self.mapping_rows.append(
            (row_widget, source_combo, target_combo)
        )

        self.refresh_mapping_fields()

    def remove_mapping_row(self):

        if not self.mapping_rows:
            return

        row_widget, source_combo, target_combo = (
            self.mapping_rows.pop()
        )

        self.mapping_layout.removeWidget(row_widget)
        row_widget.deleteLater()

    def refresh_mapping_fields(self, *args):

        source = self.source_layer.currentLayer()
        target = self.target_layer.currentLayer()

        source_names = []
        target_names = []

        if source:
            source_names = [
                field.name() for field in source.fields()
            ]

        if target:
            target_names = [
                field.name() for field in target.fields()
            ]

        for row, source_combo, target_combo in self.mapping_rows:

            old_source = source_combo.currentText()
            old_target = target_combo.currentText()

            source_combo.blockSignals(True)
            target_combo.blockSignals(True)

            source_combo.clear()
            target_combo.clear()

            source_combo.addItems(source_names)
            target_combo.addItems(target_names)

            if old_source in source_names:
                source_combo.setCurrentText(old_source)

            if old_target in target_names:
                target_combo.setCurrentText(old_target)

            source_combo.blockSignals(False)
            target_combo.blockSignals(False)

    def browse_output(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Final Layer",
            "",
            "GeoPackage (*.gpkg)"
        )

        if path:

            if not path.lower().endswith(".gpkg"):
                path += ".gpkg"

            self.output_path.setText(path)

    def run_process(self):

        target = self.target_layer.currentLayer()
        source = self.source_layer.currentLayer()

        output_path = self.output_path.text().strip()

        if not target or not source:

            QMessageBox.warning(
                self,
                "Missing Layer",
                "Please select both input layers."
            )
            return

        if target.id() == source.id():

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "Source and target layers must be different."
            )
            return

        if not output_path:

            QMessageBox.warning(
                self,
                "Missing Output",
                "Please select an output GeoPackage."
            )
            return

        if not output_path.lower().endswith(".gpkg"):

            QMessageBox.warning(
                self,
                "Invalid Output",
                "Please use a .gpkg output file."
            )
            return

        # Validate geometry compatibility
        target_type = QgsWkbTypes.geometryType(
            target.wkbType()
        )

        source_type = QgsWkbTypes.geometryType(
            source.wkbType()
        )

        if target_type != source_type:

            QMessageBox.warning(
                self,
                "Geometry Mismatch",
                "The source and target geometry types "
                "must be compatible."
            )
            return

        # Read mapping rows
        mappings = []
        used_targets = set()

        for row, source_combo, target_combo in self.mapping_rows:

            source_name = source_combo.currentText()
            target_name = target_combo.currentText()

            if not source_name or not target_name:
                continue

            if target_name in used_targets:

                QMessageBox.warning(
                    self,
                    "Duplicate Mapping",
                    f"Target field '{target_name}' "
                    "is mapped more than once."
                )
                return

            source_idx = source.fields().indexFromName(
                source_name
            )

            target_idx = target.fields().indexFromName(
                target_name
            )

            if source_idx < 0 or target_idx < 0:
                QMessageBox.warning(
                    self,
                    "Invalid Mapping",
                    "One or more selected fields are invalid."
                )
                return

            

            mappings.append((source_idx, target_idx))
            used_targets.add(target_name)

        if not mappings:

            QMessageBox.warning(
                self,
                "No Mapping",
                "Please add at least one field mapping."
            )
            return

        # Confirm operation
        answer = QMessageBox.question(
            self,
            "Confirm Replacement",
            "Append all source features to the target layer?\n\n"
            f"Target features: {target.featureCount()}\n"
            f"Source features: {source.featureCount()}\n"
            f"Expected output: "
            f"{target.featureCount() + source.featureCount()}\n\n"
            "Original input layers will not be modified.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:

            # Create temporary memory layer
            geometry_name = QgsWkbTypes.displayString(
                target.wkbType()
            )

            memory = QgsVectorLayer(
                f"{geometry_name}?crs={target.crs().authid()}",
                "Final_Dynamic_Layer_Attributes",
                "memory"
            )

            if not memory.isValid():
                raise Exception(
                    "Could not create temporary output layer."
                )

            provider = memory.dataProvider()

            provider.addAttributes(
                list(target.fields())
            )

            memory.updateFields()

            # Coordinate transformation
            transform = None

            if source.crs() != target.crs():

                transform = QgsCoordinateTransform(
                    source.crs(),
                    target.crs(),
                    QgsProject.instance()
                )

            # Append existing target features unchanged
            target_count = 0

            for feature in target.getFeatures():

                new_feature = QgsFeature(memory.fields())

                new_feature.setGeometry(
                    QgsGeometry(feature.geometry())
                )

                new_feature.setAttributes(
                    feature.attributes()
                )

                if not provider.addFeature(new_feature):
                    raise Exception(
                        "Failed to copy a target feature."
                    )

                target_count += 1

            # Append source features with mapped attributes
            source_count = 0

            for feature in source.getFeatures():

                new_feature = QgsFeature(memory.fields())

                geometry = QgsGeometry(
                    feature.geometry()
                )

                if transform:
                    geometry.transform(transform)

                if (
                    QgsWkbTypes.isMultiType(target.wkbType())
                    and not QgsWkbTypes.isMultiType(
                        source.wkbType()
                    )
                ):
                    geometry.convertToMultiType()

                new_feature.setGeometry(geometry)

                # Start with NULL destination attributes
                attributes = [None] * len(memory.fields())

                # Copy mapped attributes
                for source_idx, target_idx in mappings:

                    attributes[target_idx] = (
                        feature[source_idx]
                    )

                new_feature.setAttributes(attributes)

                if not provider.addFeature(new_feature):
                    raise Exception(
                        "Failed to append a source feature."
                    )

                source_count += 1

            memory.updateExtents()

            # Write GeoPackage
            options = QgsVectorFileWriter.SaveVectorOptions()

            options.driverName = "GPKG"
            options.fileEncoding = "UTF-8"
            options.layerName = "Final_Dynamic_Layer_Attributes"

            options.actionOnExistingFile = (
                QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
            )

            result = QgsVectorFileWriter.writeAsVectorFormatV3(
                memory,
                output_path,
                QgsProject.instance().transformContext(),
                options
            )

            if result[0] != QgsVectorFileWriter.WriterError.NoError:

                raise Exception(
                    f"Output writing failed: {result[1]}"
                )

            # Load output
            output_layer = QgsVectorLayer(
                output_path + "|layername=Final_Dynamic_Layer_Attributes",
                "Final_Dynamic_Layer_Attributes",
                "ogr"
            )

            if not output_layer.isValid():

                raise Exception(
                    "Output saved but could not be loaded."
                )

            QgsProject.instance().addMapLayer(
                output_layer
            )

            QMessageBox.information(
                self,
                "Processing Completed",
                "Dynamic layer attribute mapping completed!\n\n"
                f"Original target features: {target_count}\n"
                f"Appended source features: {source_count}\n"
                f"Final features: {output_layer.featureCount()}\n\n"
                f"Output: {output_path}"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Processing Error",
                str(error)
            )
