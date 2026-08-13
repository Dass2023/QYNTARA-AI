import maya.cmds as cmds
import os

def check_shelf(shelf_name):
    if cmds.shelfLayout(shelf_name, exists=True):
        return True
    return False

def create_shelf():
    shelf_name = "Qyntara"
    
    # Delete if exists to clear old buttons
    if check_shelf(shelf_name):
        cmds.deleteUI(shelf_name, layout=True)
        
    # Create shelf
    # We rely on the topShelf layout usually, or getting the ShelfLayout
    # A cleaner way is to load it into the main shelf bar
    main_shelf = cmds.internalVar(userShelfDir=True)
    
    cmds.shelfLayout(shelf_name, parent="ShelfLayout")
    
    # Add Button
    icon_path = "pythonFamily.png" # Standard maya icon
    
    command = "import qyntara_ai.ui.main_window as qwin; qwin.show()"
    
    cmds.shelfButton(
        annotation="Launch Qyntara AI Validator",
        image1=icon_path, 
        command=command, 
        label="QValidator",
        parent=shelf_name,
        sourceType="python"
    )
    
    print(f"Shelf '{shelf_name}' created successfully.")

if __name__ == "__main__":
    create_shelf()
