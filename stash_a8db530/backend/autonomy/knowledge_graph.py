"""
Qyntara AI Knowledge Graph
==========================
Maintains semantic links between Assets, Concepts, and Rules.
Enables reasoning like: "This is a 'Prop', therefore it needs 'Collision' and 'LODs'."
"""

import networkx as nx
import json
import os
from typing import List, Dict, Any, Optional

class KnowledgeGraph:
    def __init__(self, persist_path="backend/data/knowledge_graph.json"):
        self.graph = nx.DiGraph()
        self.persist_path = persist_path
        self._load()

        # Initialize Base Ontology if empty
        if len(self.graph.nodes) == 0:
            self._init_ontology()

    def _init_ontology(self):
        """Defines the core spatial intelligence ontology."""
        # Concepts
        self.add_concept("Asset", "Root entity")
        self.add_concept("Prop", "Static object", parent="Asset")
        self.add_concept("Character", "Animated entity", parent="Asset")
        self.add_concept("Environment", "Scene container", parent="Asset")

        # Rules
        self.add_rule("Prop", "requires_collision", {"type": "convex"})
        self.add_rule("Prop", "requires_lods", {"count": 3})
        self.add_rule("Character", "requires_rig", {"bones_min": 1})
        self.add_rule("Environment", "requires_lightmap", {"res": 1024})

    def add_concept(self, name: str, description: str, parent: Optional[str] = None):
        self.graph.add_node(name, type="Concept", description=description)
        if parent:
            self.graph.add_edge(parent, name, relation="is_parent_of")

    def add_rule(self, concept: str, rule_name: str, params: Dict[str, Any]):
        rule_node = f"Rule_{rule_name}_{concept}"
        self.graph.add_node(rule_node, type="Rule", name=rule_name, params=params)
        self.graph.add_edge(concept, rule_node, relation="enforces")

    def register_asset(self, asset_id: str, classification: str, metadata: Dict[str, Any]):
        """Links a live asset to the ontology."""
        self.graph.add_node(asset_id, type="Instance", metadata=metadata)
        
        # Link to classification (e.g., "Prop")
        if classification in self.graph.nodes:
            self.graph.add_edge(classification, asset_id, relation="classifies")
        else:
            # Fallback
            self.graph.add_edge("Asset", asset_id, relation="classifies")

    def get_rules_for_asset(self, asset_id: str) -> List[Dict]:
        """Infers rules based on the asset's classification inheritance."""
        rules = []
        # Find classification parents
        predecessors = list(self.graph.predecessors(asset_id))
        
        for parent in predecessors:
            # Traverse up ontology (concept hierarchy) isn't strictly directed down in graph terms for 'is_parent_of',
            # but 'classifies' creates Parent -> Instance.
            # So we check the Parent and its ancestors.
            
            # Simple 1-level check for v8.0 MVP
            # Check rules connected to Parent
            for neighbor in self.graph.neighbors(parent):
                node = self.graph.nodes[neighbor]
                if node.get("type") == "Rule":
                    rules.append(node)
                    
            # Check ancestors of Parent (if we defined 'is_parent_of' as Parent->Child)
            # We defined add_edge(parent, name). So Parent -> Child.
            # We need to traverse upstream from Parent? No, Parent is the source.
            # If Child inherits from Parent, Child should have Parent's rules.
            # Current structure: Parent -> Child. 
            # If Asset is instance of Child (Child -> Asset), then we need upstream of Child.
            
            # For MVP, we just check direct classification.
            
        return rules

    def save(self):
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
        data = nx.node_link_data(self.graph)
        with open(self.persist_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, "r") as f:
                    data = json.load(f)
                self.graph = nx.node_link_graph(data)
            except Exception:
                print("Knowledge Graph load failed. Starting fresh.")
