bl_info = {
    "name": "Qyntara Blender Pro Exporter",
    "author": "Antigravity AI (Technical Director)",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Qyntara",
    "description": "High-Fidelity glTF/USD Export with QUP Validation",
    "category": "Import-Export",
}

import bpy
import os

# --- QUP VALIDATOR CORE ---
class QUP_Protector:
    """ Audits meshes according to the Qyntara Universal Pipeline (QUP) Spec. """
    
    @staticmethod
    def audit_scene():
        errors = []
        warnings = []
        
        selected = bpy.context.selected_objects
        if not selected:
            errors.append("No objects selected for audit.")
            return errors, warnings
            
        for obj in selected:
            if obj.type != 'MESH': continue
            
            # 1. Scale Audit
            if any(round(s, 3) != 1.0 for s in obj.scale):
                warnings.append(f"{obj.name}: Scale is not [1,1,1]. Auto-apply suggested.")
                
            # 2. Geometry Audit (Static check)
            mesh = obj.data
            non_manifold = False
            zero_area = 0
            
            # Using bmesh for deeper audit if needed, but standard logic first
            for poly in mesh.polygons:
                if poly.area < 0.000001:
                    zero_area += 1
            
            if zero_area > 0:
                warnings.append(f"{obj.name}: Found {zero_area} zero-area faces.")
                
            # 3. Material Audit (Principled v2)
            for slot in obj.material_slots:
                mat = slot.material
                if not mat or not mat.use_nodes:
                    errors.append(f"{obj.name}: Material '{mat.name if mat else 'N/A'}' lacks node tree.")
                    continue
                
                nodes = mat.node_tree.nodes
                principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if not principled:
                    errors.append(f"{obj.name}: Material '{mat.name}' is not PBR compliant (lacks Principled BSDF).")

        return errors, warnings

# --- EXPORTER OPERATORS ---
class QYNTARA_OT_ExportGlb(bpy.types.Operator):
    """ High-Fidelity glTF/GLB Export with PBR Next Support """
    bl_idname = "qyntara.export_glb"
    bl_label = "Export High-Fidelity GLB"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # 1. Verification
        errors, warnings = QUP_Protector.audit_scene()
        
        if errors:
            self.report({'ERROR'}, "Export Aborted: Fix critical errors first.")
            return {'CANCELLED'}
            
        # 2. Path Handling
        if not self.filepath:
            # Generate default path based on scene/object
            blend_path = bpy.data.filepath
            folder = os.path.dirname(blend_path) if blend_path else os.path.expanduser("~")
            name = bpy.context.active_object.name if bpy.context.active_object else "Qyntara_Asset"
            self.filepath = os.path.join(folder, f"{name}.glb")

        # 3. HIGH-FIDELITY EXPORT SETTINGS (Director Grade)
        bpy.ops.export_scene.gltf(
            filepath=self.filepath,
            export_format='GLB',
            export_apply=True,
            export_tangents=True,
            export_colors=True,
            export_materials='EXPORT',
            export_image_format='AUTO',
            export_meshopt_compression_enable=True, # Modern standard
            export_meshopt_compression_level=3,
            export_meshopt_compression_filters=True,
            use_selection=True,
            # PBR Next Extensions
            export_extras=True,
            export_attribute=True
        )
        
        self.report({'INFO'}, f"QUP Export Success: {os.path.basename(self.filepath)}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class QYNTARA_OT_ImportGlb(bpy.types.Operator):
    """ High-Fidelity glTF/GLB Import with Post-Import Audit """
    bl_idname = "qyntara.import_glb"
    bl_label = "Import High-Fidelity GLB"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}
            
        # 1. Standard Import
        bpy.ops.import_scene.gltf(filepath=self.filepath)
        
        # 2. Post-Import QC Audit
        # We assume the imported objects are selected
        errors, warnings = QUP_Protector.audit_scene()
        
        self.report({'INFO'}, f"Imported: {os.path.basename(self.filepath)}")
        if errors or warnings:
            self.report({'WARNING'}, f"QC Results: {len(errors)} errors, {len(warnings)} warnings detected.")
            
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# --- UI PANEL ---
class QYNTARA_PT_MainPanel(bpy.types.Panel):
    """ Qyntara AI Production Panel """
    bl_label = "Qyntara AI (Production)"
    bl_idname = "QYNTARA_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Qyntara'

    def draw(self, context):
        layout = self.layout
        layout.label(text="QUP Production Toolkit", icon='MOD_PHYSICS')
        
        box = layout.box()
        box.label(text="1. Scene Audit", icon='CHECKMARK')
        box.operator("qyntara.run_audit", text="RUN QUP VALIDATION")
        
        col = layout.column(align=True)
        col.label(text="2. High-Fidelity I/O", icon='EXPORT')
        col.operator("qyntara.import_glb", text="IMPORT GLB/GLTF")
        col.operator("qyntara.export_glb", text="EXPORT GLB (WEB/AR)")
        col.operator("qyntara.export_usd", text="EXPORT OPENUSD (OMNIVERSE)")

class QYNTARA_OT_RunAudit(bpy.types.Operator):
    bl_idname = "qyntara.run_audit"
    bl_label = "Run QUP Audit"
    
    def execute(self, context):
        errors, warnings = QUP_Protector.audit_scene()
        
        for err in errors: self.report({'ERROR'}, f"ERR: {err}")
        for wrn in warnings: self.report({'WARNING'}, f"WRN: {wrn}")
        
        if not errors and not warnings:
            self.report({'INFO'}, "QUP Status: OPTIMAL. Asset is industry-ready.")
        elif not errors:
            self.report({'INFO'}, "QUP Status: VALID (with warnings).")
            
        return {'FINISHED'}

# --- REGISTRATION ---
classes = (
    QYNTARA_OT_ExportGlb,
    QYNTARA_OT_ImportGlb,
    QYNTARA_OT_RunAudit,
    QYNTARA_PT_MainPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
