Graph Drawing Utility for Object Relationships
Overview
The Graph Drawing Utility project provides a versatile tool for visualizing object relationships in the context of the Object Model Framework. This utility is designed to be seamlessly integrated into projects, such as the one described earlier, allowing users to dynamically represent and explore the connections between objects.

Key Features
Dynamic Object Addition:

Users can add objects to the graph using the add_item method, allowing for the incorporation of diverse entities and their relationships.
Viewing Objects:

The item_view method provides a means to inspect the details of individual objects, facilitating a deeper understanding of the interconnected elements.
Relationship Establishment:

Users can establish relationships between objects using three types:
add_parent: Defines an ownership relationship, clustering owned objects together.
add_list_item: Associates an object with a list, displaying related items within the owner's cluster.
add_link: Creates a connection between objects using arrows.
Graph Rendering:

The utility enables users to visualize the constructed object graph, providing a clear representation of the established relationships.

Integration with Object Model Framework
This utility is specifically designed to work seamlessly with the Object Model Framework, enhancing the visualization capabilities of interconnected objects.