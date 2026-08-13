from qyntara_ai.core.advanced_floorplan_ai import SemanticArchitect, Vector2

def test_room_detection():
    ai = SemanticArchitect()
    
    # Create a simple square room (100x100)
    # (0,0) -> (100,0) -> (100,100) -> (0,100) -> (0,0)
    
    lines = [
        (Vector2(0,0), Vector2(100,0)),
        (Vector2(100,0), Vector2(100,100)),
        (Vector2(100,100), Vector2(0,100)),
        (Vector2(0,100), Vector2(0,0))
    ]
    
    print("Building Graph...")
    ai.analyze_scene(lines)
    
    print(f"Nodes: {len(ai.graph.nodes)} (Expected 4)")
    print(f"Edges: {len(ai.graph.edges)} (Expected 4)")
    
    print("Detecting Rooms...")
    rooms = ai.classify_rooms()
    print(f"Rooms Found: {len(rooms)}")
    
    for i, r in enumerate(rooms):
        print(f"Room {i}: Area={r['area']}, Center={r['center']}")
        
    if len(rooms) == 1:
        print("SUCCESS: 1 Room detected.")
    else:
        print("FAILURE: Room detection failed.")

if __name__ == "__main__":
    test_room_detection()
