import logging
import socket
import json
import threading

logger = logging.getLogger(__name__)

class EngineSyncClient:
    """
    Real-Time Bridge to Game Engines (Unreal/Unity).
    Uses TCP Sockets to send asset updates.
    """
    
    def __init__(self, host='127.0.0.1', port=13000):
        self.host = host
        self.port = port
        self.connected = False
        self.socket = None

    def connect(self, silent=False):
        """Attempts to connect to the Engine Listener."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1.0) # Reduced from 2.0 to improve UI responsiveness
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to Engine at {self.host}:{self.port}")
            return True
        except Exception as e:
            if not silent:
                logger.warning(f"Engine connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.connected = False

    def push_selection(self, objects, silent=False):
        """
        Sends transform/metadata of selected objects to the engine.
        Protocol: JSON Packet
        """
        if not self.connected:
            # Try once to reconnect?
            if not self.connect(silent=silent):
                return False

        from maya import cmds
        data_packet = {"action": "update_transforms", "objects": []}
        
        for obj in objects:
            # Get Transform
            t = cmds.xform(obj, q=True, t=True, ws=True)
            r = cmds.xform(obj, q=True, ro=True, ws=True)
            s = cmds.xform(obj, q=True, s=True, ws=True)
            
            data_packet["objects"].append({
                "name": obj,
                "position": t,
                "rotation": r,
                "scale": s,
                # In a real tool, we'd send FBX path or USD ref here too
            })

        try:
            msg = json.dumps(data_packet).encode('utf-8')
            self.socket.sendall(msg)
            return True
        except Exception as e:
            logger.error(f"Sync sending failed: {e}")
            self.connected = False
            return False

    def mock_push(self, objects):
        """ Simulates success for UI testing when no Engine is running. """
        logger.info(f"[Mock Sync] Sent {len(objects)} objects to Unreal Endpoint.")
        return True
