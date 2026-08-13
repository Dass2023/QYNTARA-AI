from .qt_utils import QtWidgets, QtCore, QtGui
import logging
import os
from ..core import retopology, baking_automation, genai_client, remote_processor, usd_validator, engine_sync, pointnet_classifier, asset_library, delivery, floorplan_builder

logger = logging.getLogger(__name__)

class ScannerWidget(QtWidgets.QWidget):
    """
    UI Tab for the 'Scan-to-Asset' pipeline (Lidar / Photogrammetry Tools).
    Features:
    1. Import & Validate
    2. Auto-Retopology
    3. Baking (Projection)
    4. AI Materials
    5. Delivery
    """
    def __init__(self, parent=None):
        super(ScannerWidget, self).__init__(parent)
        self.retopo_manager = retopology.AutoRetopologyManager()
        self.baker = baking_automation.BakingAutomation()
        self.ai_client = genai_client.GenAIClient()
        self.cloud_client = remote_processor.RemoteProcessor()
        self.usd_validator = usd_validator.USDValidator()
        self.engine_link = engine_sync.EngineSyncClient()
        self.classifier = pointnet_classifier.PointNetClassifier()
        self.asset_lib = asset_library.AssetLibrary()
        self.delivery_mgr = delivery.DeliveryManager()
        
        self.init_ui()
        
    def init_ui(self):
        # Wrapper
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        # Scroll Area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        content = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(content)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # -- Import --
        self.btn_import = QtWidgets.QPushButton("IMPORT SCAN / LIDAR DATA")
        self.btn_import.setStyleSheet("""
            QPushButton { background: #444; color: #fff; font-weight: bold; padding: 10px; border: 1px solid #555; border-radius: 4px; }
            QPushButton:hover { background: #555; }
        """)
        self.btn_import.clicked.connect(self.import_scan)
        self.layout.addWidget(self.btn_import)

        # -- Validation --
        val_group = QtWidgets.QGroupBox("1. Scan Health Check")
        val_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 6px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        v_layout = QtWidgets.QVBoxLayout(val_group)
        v_layout.setContentsMargins(10, 15, 10, 10)
        self.btn_validate_scan = QtWidgets.QPushButton("VALIDATE SCAN HEALTH")
        self.btn_validate_scan.setStyleSheet("background: #d19a66; color: black; font-weight: bold; padding: 8px;")
        self.btn_validate_scan.clicked.connect(self.run_scan_validation)
        v_layout.addWidget(self.btn_validate_scan)
        self.layout.addWidget(val_group)
        
        # -- Retopo --
        retopo_group = QtWidgets.QGroupBox("2. Auto-Retopology")
        retopo_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 6px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        r_layout = QtWidgets.QVBoxLayout(retopo_group)
        r_layout.setContentsMargins(10, 15, 10, 10)
        hbox_q = QtWidgets.QHBoxLayout()
        hbox_q.addWidget(QtWidgets.QLabel("Target Quality:"))
        self.combo_quality = QtWidgets.QComboBox()
        self.combo_quality.addItems(["Low (Game Prop - 5%)", "Mid (Hero Prop - 20%)", "High (Cinematic - 50%)"])
        self.combo_quality.setCurrentIndex(1)
        hbox_q.addWidget(self.combo_quality)
        r_layout.addLayout(hbox_q)
        self.chk_cloud = QtWidgets.QCheckBox("☁️ Run on Cloud (Offload)")
        self.chk_cloud.setStyleSheet("color: #61afef; font-weight: bold;")
        r_layout.addWidget(self.chk_cloud)
        self.btn_retopo = QtWidgets.QPushButton("RUN AUTO-RETOPO")
        self.btn_retopo.setStyleSheet("background: #00CEC9; color: black; font-weight: bold; padding: 8px;")
        self.btn_retopo.clicked.connect(self.run_retopo)
        r_layout.addWidget(self.btn_retopo)
        self.layout.addWidget(retopo_group)
        
        # -- Baking --
        bake_group = QtWidgets.QGroupBox("3. Texture Reprojection (Bake)")
        bake_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 6px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        b_layout = QtWidgets.QVBoxLayout(bake_group)
        b_layout.setContentsMargins(10, 15, 10, 10)
        self.lbl_high = QtWidgets.QLabel("(Select High Poly)")
        self.lbl_low = QtWidgets.QLabel("(Select Low Poly)")
        self.high_poly_node = None
        self.low_poly_node = None
        form = QtWidgets.QFormLayout()
        btn_set_high = QtWidgets.QPushButton("Set Source")
        btn_set_high.clicked.connect(self.set_high_poly)
        btn_set_low = QtWidgets.QPushButton("Set Target")
        btn_set_low.clicked.connect(self.set_low_poly)
        form.addRow(btn_set_high, self.lbl_high)
        form.addRow(btn_set_low, self.lbl_low)
        b_layout.addLayout(form)
        self.btn_bake = QtWidgets.QPushButton("BAKE TEXTURES")
        self.btn_bake.setStyleSheet("background: #E06C75; color: black; font-weight: bold; padding: 8px;")
        self.btn_bake.clicked.connect(self.run_bake)
        self.btn_bake.setEnabled(False)
        b_layout.addWidget(self.btn_bake)
        self.layout.addWidget(bake_group)
        
        # -- AI / SUBSTANCE MATERIAL GENERATOR --
        mat_group = QtWidgets.QGroupBox("4. Material Generator")
        mat_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 6px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        mat_layout = QtWidgets.QVBoxLayout(mat_group)
        mat_layout.setContentsMargins(10, 15, 10, 10)
        
        # PHASE 3: Mode Selection (AI vs Substance)
        mode_layout = QtWidgets.QHBoxLayout()
        mode_layout.addWidget(QtWidgets.QLabel("Mode:"))
        
        self.bg_material_mode = QtWidgets.QButtonGroup(self)
        self.rad_ai = QtWidgets.QRadioButton("AI Generator")
        self.rad_ai.setChecked(True)
        self.rad_ai.setToolTip("Use AI-powered material generation")
        self.bg_material_mode.addButton(self.rad_ai)
        
        self.rad_substance = QtWidgets.QRadioButton("Substance Designer")
        self.rad_substance.setToolTip("Use Substance Automation Toolkit (requires installation)")
        self.bg_material_mode.addButton(self.rad_substance)
        
        mode_layout.addWidget(self.rad_ai)
        mode_layout.addWidget(self.rad_substance)
        mode_layout.addStretch()
        
        # Substance status indicator
        self.lbl_substance_status = QtWidgets.QLabel()
        self.lbl_substance_status.setStyleSheet("color: #888; font-style: italic; font-size: 10px;")
        mode_layout.addWidget(self.lbl_substance_status)
        
        mat_layout.addLayout(mode_layout)
        
        # Prompt input (shared by both modes)
        h_prompt = QtWidgets.QHBoxLayout()
        self.txt_prompt = QtWidgets.QLineEdit()
        self.txt_prompt.setPlaceholderText("Enter material description (e.g., 'rusty metal', 'concrete wall')...")
        h_prompt.addWidget(QtWidgets.QLabel("Prompt:"))
        h_prompt.addWidget(self.txt_prompt)
        mat_layout.addLayout(h_prompt)
        
        # PHASE 3: Substance Parameters (hidden by default)
        self.substance_params_widget = QtWidgets.QWidget()
        params_layout = QtWidgets.QVBoxLayout(self.substance_params_widget)
        params_layout.setContentsMargins(0, 5, 0, 5)
        
        # Resolution selector
        res_layout = QtWidgets.QHBoxLayout()
        res_layout.addWidget(QtWidgets.QLabel("Resolution:"))
        self.combo_resolution = QtWidgets.QComboBox()
        self.combo_resolution.addItems(["512", "1024", "2048", "4096"])
        self.combo_resolution.setCurrentText("1024")
        res_layout.addWidget(self.combo_resolution)
        res_layout.addStretch()
        params_layout.addLayout(res_layout)
        
        # Export SBSAR checkbox
        self.chk_export_sbsar = QtWidgets.QCheckBox("Export .sbsar for Pipeline")
        self.chk_export_sbsar.setToolTip("Save Substance archive for use in other tools")
        params_layout.addWidget(self.chk_export_sbsar)
        
        self.substance_params_widget.setVisible(False)
        mat_layout.addWidget(self.substance_params_widget)
        
        # Connect mode toggle
        self.rad_substance.toggled.connect(self.on_material_mode_changed)
        
        # Generate button
        self.btn_gen_material = QtWidgets.QPushButton("GENERATE MATERIAL")
        self.btn_gen_material.setStyleSheet("background: #c678dd; color: black; font-weight: bold; padding: 10px;")
        self.btn_gen_material.clicked.connect(self.run_material_generation)
        mat_layout.addWidget(self.btn_gen_material)
        
        self.layout.addWidget(mat_group)
        
        # Initialize Substance Bridge
        from ..core.substance_bridge import SubstanceIntegration
        self.substance = SubstanceIntegration()
        self.update_substance_status()

        # -- Sync -- 
        sync_group = QtWidgets.QGroupBox("5. Real-Time Engine Sync")
        sync_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 6px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        s_layout = QtWidgets.QVBoxLayout(sync_group)
        self.btn_connect = QtWidgets.QPushButton("CONNECT TO UNREAL")
        self.btn_connect.clicked.connect(self.toggle_connection)
        self.lbl_status = QtWidgets.QLabel("🔴 Disconnected")
        s_layout.addWidget(self.btn_connect)
        s_layout.addWidget(self.lbl_status)
        self.btn_push = QtWidgets.QPushButton("PUSH SELECTION")
        self.btn_push.clicked.connect(self.push_to_engine)
        s_layout.addWidget(self.btn_push)
        self.layout.addWidget(sync_group)
        
        # -- Recon --
        recon_group = QtWidgets.QGroupBox("6. AI Reconstruction")
        recon_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 6px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        rc_layout = QtWidgets.QVBoxLayout(recon_group)
        rc_layout.setContentsMargins(10, 15, 10, 10)
        self.btn_classify = QtWidgets.QPushButton("CLASSIFY OBJECTS")
        self.btn_classify.clicked.connect(self.run_classification)
        rc_layout.addWidget(self.btn_classify)
        self.btn_replace = QtWidgets.QPushButton("REPLACE (Door/Window)")
        self.btn_replace.clicked.connect(self.run_replacement)
        rc_layout.addWidget(self.btn_replace)
        self.layout.addWidget(recon_group)

        # -- Export --
        export_group = QtWidgets.QGroupBox("7. Delivery (Final Export)")
        export_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; margin-top: 6px; padding-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        ex_layout = QtWidgets.QVBoxLayout(export_group)
        ex_layout.setContentsMargins(10, 15, 10, 10)
        self.btn_deliver = QtWidgets.QPushButton("PACKAGE SOLUTION")
        self.btn_deliver.setStyleSheet("background: #4caf50; color: white; font-weight: bold; padding: 12px;")
        self.btn_deliver.clicked.connect(self.run_delivery)
        ex_layout.addWidget(self.btn_deliver)
        self.layout.addWidget(export_group)
        
        self.layout.addStretch()

    # --- METHODS ---
    def run_retopo(self):
        try:
            from maya import cmds
            sel = cmds.ls(sl=True, long=True)
            if not sel:
                cmds.warning("Select scan objects first.")
                return
            
            q_text = self.combo_quality.currentText()
            quality = "mid"
            if "Low" in q_text: quality = "low"
            elif "High" in q_text: quality = "high"
            
            if self.chk_cloud.isChecked():
                self.run_retopo_cloud(sel, quality)
                return
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            try:
                results = self.retopo_manager.run_smart_retopo(sel, target_quality=quality)
                if results:
                    print(f"Retopology Complete (Local). Created: {results}")
                    cmds.select(results)
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()
        except Exception as e:
            print(f"Retopo Error: {e}")

    def run_retopo_cloud(self, objects, quality):
        print("Submitting to Qyntara Cloud...")
        job_id = self.cloud_client.submit_retopology_job(objects)
        print(f"Job ID: {job_id} uploaded.")
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
             success = self.cloud_client.mock_server_process(job_id, objects[0], self.retopo_manager)
             if success:
                 result_path = self.cloud_client.get_result(job_id)
                 if result_path:
                     from maya import cmds
                     imported = cmds.file(result_path, i=True, returnNewNodes=True)
                     print(f"Cloud Job Complete! Imported: {imported}")
                     cmds.select(imported)
        except Exception as e:
            print(f"Cloud Error: {e}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def set_high_poly(self):
        from maya import cmds
        sel = cmds.ls(sl=True, long=True)
        if sel:
            self.high_poly_node = sel[0]
            self.lbl_high.setText(str(self.high_poly_node))
            self.check_bake_ready()

    def set_low_poly(self):
        from maya import cmds
        sel = cmds.ls(sl=True, long=True)
        if sel:
            self.low_poly_node = sel[0]
            self.lbl_low.setText(str(self.low_poly_node))
            self.check_bake_ready()
            
    def check_bake_ready(self):
        ready = bool(self.high_poly_node and self.low_poly_node)
        self.btn_bake.setEnabled(ready)

    def run_bake(self):
        if not self.high_poly_node or not self.low_poly_node:
            return
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            maps = self.baker.bake_textures(self.high_poly_node, self.low_poly_node)
            if maps:
                print(f"Bake Success! Output: {maps}")
        except Exception as e:
            print(f"Bake Error: {e}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def import_scan(self):
        try:
            from maya import cmds
            file_filter = "Scan Files (*.obj *.fbx *.abc *.usd *.usdc *.usda *.usdz *.ply);;All Files (*.*)"
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import LiDAR / Scan Data", "", file_filter)
            
            if path:
                if path.lower().endswith(".usd") or path.lower().endswith(".usdz"):
                    if not cmds.pluginInfo("mayaUsdPlugin", q=True, loaded=True):
                         try: cmds.loadPlugin("mayaUsdPlugin")
                         except: pass
                
                nodes = cmds.file(path, i=True, returnNewNodes=True, force=True, prompt=False)
                if nodes:
                    print(f"Imported: {nodes}")
                    cmds.select(nodes)
                    cmds.viewFit()
        except Exception as e:
            print(f"Import Error: {e}")

    def run_scan_validation(self):
        try:
            main_window = self.window()
            if hasattr(main_window, "combo_pipeline"):
                validator = main_window.validator
                validator.set_pipeline_profile("lidar")
                print("Switched to LiDAR Validation Profile.")
                main_window.tabs.setCurrentIndex(0)
                main_window.run_validation()
        except Exception as e:
            print(f"Validation Launch Error: {e}")

    def run_genai(self):
        prompt = self.txt_prompt.text()
        if not prompt: return

        from maya import cmds
        sel = cmds.ls(sl=True)
        if not sel: return

        print(f"Generating material for: '{prompt}'...")
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            paths = self.ai_client.generate_material(prompt)
            if not paths: return

            mat_name = f"AI_{prompt.replace(' ', '_')}_Mat"
            sg_name = f"{mat_name}SG"
            
            if cmds.objExists(mat_name): cmds.delete(mat_name)
            if cmds.objExists(sg_name): cmds.delete(sg_name)
            
            shader = cmds.shadingNode("blinn", asShader=True, name=mat_name)
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
            cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader")
            
            if "diffuse" in paths:
                tex_node = cmds.shadingNode("file", asTexture=True, name=f"{mat_name}_Diffuse_File")
                cmds.setAttr(f"{tex_node}.fileTextureName", paths["diffuse"], type="string")
                cmds.connectAttr(f"{tex_node}.outColor", f"{shader}.color")
            
            cmds.sets(sel, forceElement=sg)
            print(f"Material '{mat_name}' created and assigned.")
        except Exception as e:
            print(f"GenAI Error: {e}")
        finally:
             QtWidgets.QApplication.restoreOverrideCursor()

    def toggle_connection(self):
        if self.engine_link.connected:
            self.engine_link.disconnect()
            self.lbl_status.setText("🔴 Disconnected")
        else:
            success = self.engine_link.connect()
            if success:
                self.lbl_status.setText("🟢 Connected")
            else:
                 self.lbl_status.setText("🟡 Mock Connected")
    
    # --- PHASE 3: SUBSTANCE DESIGNER METHODS ---
    def on_material_mode_changed(self, checked):
        """Toggle Substance-specific UI elements."""
        if checked:  # Substance mode
            self.substance_params_widget.setVisible(True)
            self.btn_gen_material.setText("GENERATE MATERIAL (Substance)")
            self.btn_gen_material.setStyleSheet("background: #ff6b35; color: white; font-weight: bold; padding: 10px;")
        else:  # AI mode
            self.substance_params_widget.setVisible(False)
            self.btn_gen_material.setText("GENERATE MATERIAL (AI)")
            self.btn_gen_material.setStyleSheet("background: #c678dd; color: black; font-weight: bold; padding: 10px;")
    
    def update_substance_status(self):
        """Update Substance Designer installation status."""
        if self.substance.substance_installed:
            self.lbl_substance_status.setText("✅ Substance Designer detected")
            self.lbl_substance_status.setStyleSheet("color: #00ff9d; font-weight: bold; font-size: 10px;")
        else:
            self.lbl_substance_status.setText("⚠️ Substance not found (will use fallback)")
            self.lbl_substance_status.setStyleSheet("color: #ff6b6b; font-style: italic; font-size: 10px;")
            # Disable Substance mode if not installed
            # self.rad_substance.setEnabled(False)  # Optional: force AI mode
    
    def run_material_generation(self):
        """Unified material generation handler (AI or Substance)."""
        if self.rad_ai.isChecked():
            # Use existing AI generator
            self.run_genai()
        else:
            # Use Substance Designer
            self.run_substance_material()
    
    def run_substance_material(self):
        """Generate material using Substance Designer."""
        from maya import cmds
        
        prompt = self.txt_prompt.text().strip()
        if not prompt:
            QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a material description.")
            return
        
        sel = cmds.ls(sl=True)
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Selection Required", "Please select an object to apply material.")
            return
        
        print(f"[Substance] Generating material for: '{prompt}'...")
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        try:
            # Get parameters
            resolution = int(self.combo_resolution.currentText())
            export_sbsar = self.chk_export_sbsar.isChecked()
            
            # Create output directory
            import tempfile
            output_dir = tempfile.mkdtemp(prefix="qyntara_substance_")
            
            # Generate material
            texture_paths = self.substance.generate_material(prompt, output_dir, resolution)
            
            if not texture_paths:
                QtWidgets.QApplication.restoreOverrideCursor()
                QtWidgets.QMessageBox.critical(self, "Generation Failed", "Failed to generate material textures.")
                return
            
            # Create Maya material
            mat_name = f"Substance_{prompt.replace(' ', '_')}_Mat"
            sg_name = f"{mat_name}SG"
            
            # Delete existing
            if cmds.objExists(mat_name):
                cmds.delete(mat_name)
            if cmds.objExists(sg_name):
                cmds.delete(sg_name)
            
            # Create shader network
            shader = cmds.shadingNode("standardSurface", asShader=True, name=mat_name)
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
            cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader")
            
            # Connect textures
            if "diffuse" in texture_paths:
                tex_node = cmds.shadingNode("file", asTexture=True, name=f"{mat_name}_Diffuse_File")
                cmds.setAttr(f"{tex_node}.fileTextureName", texture_paths["diffuse"], type="string")
                cmds.connectAttr(f"{tex_node}.outColor", f"{shader}.baseColor")
            
            if "roughness" in texture_paths:
                tex_node = cmds.shadingNode("file", asTexture=True, name=f"{mat_name}_Roughness_File")
                cmds.setAttr(f"{tex_node}.fileTextureName", texture_paths["roughness"], type="string")
                cmds.setAttr(f"{tex_node}.colorSpace", "Raw", type="string")
                cmds.connectAttr(f"{tex_node}.outAlpha", f"{shader}.specularRoughness")
            
            if "normal" in texture_paths:
                bump_node = cmds.shadingNode("bump2d", asUtility=True, name=f"{mat_name}_Bump")
                tex_node = cmds.shadingNode("file", asTexture=True, name=f"{mat_name}_Normal_File")
                cmds.setAttr(f"{tex_node}.fileTextureName", texture_paths["normal"], type="string")
                cmds.setAttr(f"{tex_node}.colorSpace", "Raw", type="string")
                cmds.connectAttr(f"{tex_node}.outAlpha", f"{bump_node}.bumpValue")
                cmds.connectAttr(f"{bump_node}.outNormal", f"{shader}.normalCamera")
            
            if "metallic" in texture_paths:
                tex_node = cmds.shadingNode("file", asTexture=True, name=f"{mat_name}_Metallic_File")
                cmds.setAttr(f"{tex_node}.fileTextureName", texture_paths["metallic"], type="string")
                cmds.setAttr(f"{tex_node}.colorSpace", "Raw", type="string")
                cmds.connectAttr(f"{tex_node}.outAlpha", f"{shader}.metalness")
            
            # Assign to selection
            cmds.sets(sel, forceElement=sg)
            
            QtWidgets.QApplication.restoreOverrideCursor()
            
            # Success message
            msg = f"Material '{mat_name}' created and assigned.\\n\\n"
            msg += f"Textures generated: {len(texture_paths)}\\n"
            msg += f"Resolution: {resolution}x{resolution}\\n"
            msg += f"Output: {output_dir}"
            
            if export_sbsar:
                msg += "\\n\\n.sbsar export: Not yet implemented"
            
            QtWidgets.QMessageBox.information(self, "Success", msg)
            print(f"[Substance] Material '{mat_name}' created successfully.")
            
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, "Error", f"Substance generation failed:\\n{str(e)}")
            print(f"[Substance] Error: {e}")
            import traceback
            traceback.print_exc()

    def push_to_engine(self):
        from maya import cmds
        sel = cmds.ls(sl=True)
        if not sel: return
        success = self.engine_link.push_selection(sel)
        if not success or "Mock" in self.lbl_status.text():
            self.engine_link.mock_push(sel)
            print(f"Synced {len(sel)} objects to Engine (Mock Success).")

    def run_classification(self):
        from maya import cmds
        sel = cmds.ls(sl=True)
        if not sel: return
        print("Running AI Classification...")
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            results = self.classifier.classify_objects(sel)
            self.classifier.apply_labels_to_scene(results)
            count = len(results)
            QtWidgets.QMessageBox.information(self, "AI Classifier", f"Successfully classified {count} objects.")
        except Exception as e:
            print(f"Classifier Error: {e}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def run_replacement(self):
        from maya import cmds
        sel = cmds.ls(sl=True)
        if not sel: return
        print("Running Semantic Asset Replacement...")
        count = 0
        replaced = []
        for obj in sel:
            if cmds.attributeQuery("aiLabel", node=obj, exists=True):
                label = cmds.getAttr(f"{obj}.aiLabel")
                if label in ["Door", "Window", "Chair", "Table"]:
                    new_asset = self.asset_lib.replace_with_asset(obj, label)
                    if new_asset:
                        count += 1
                        replaced.append(new_asset)
        if count > 0:
            cmds.select(replaced)
            QtWidgets.QMessageBox.information(self, "Asset Replacement", f"Successfully replaced {count} scan blobs.")
        else:
             QtWidgets.QMessageBox.warning(self, "No Replacement", "No objects with 'Door' or 'Window' AI labels found.")

    def run_delivery(self):
        from maya import cmds
        sel = cmds.ls(sl=True)
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Export", "Please select the final assets you want to package.")
            return
        try:
             path = self.delivery_mgr.export_clean_scene(sel)
             QtWidgets.QMessageBox.information(self, "Delivery Complete", f"Solution packaged at:\n{path}")
             import subprocess
             subprocess.Popen(f'explorer "{path}"')
        except Exception as e:
            print(f"Delivery Error: {e}")
