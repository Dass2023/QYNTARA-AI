    @staticmethod
    @undo_chunk
    def fix_triangulate(report_entry):
        """Triangulates mesh."""
        objects = QyntaraFixer._get_objects(report_entry)
        if not objects: return False
        
        for obj in objects:
            try:
                cmds.polyTriangulate(obj, ch=True)
            except Exception as e:
                logger.warning(f"Failed to fix triangulation {obj}: {e}")
        return True
