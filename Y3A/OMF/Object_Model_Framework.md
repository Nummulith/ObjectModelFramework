[ReadMe.md](../ReadMe.md) \ [Object Model Framework](Object_Model_Framework.md)

<table style="width: 100%">
  <thead>
    <tr>
        <th>
            <h1>Object Model Framework</h1>
        </th>
        <th>
            <img src="../img/Object_Model_Framework.png" width="100" height="100">
        </th>
    </tr>
  </thead>
</table>

## Overview
The **Object Model Framework** is a foundational Python-based program that facilitates the creation, management, and visualization of a network of user-defined classes. Users can dynamically define classes, establish relationships between objects, and interact with external systems.
The Object Model Framework introduces a declarative paradigm for describing relationships between classes instances.
The framework allows users to establish relationships between objects, providing a versatile foundation for various applications.

## Class-Driven Approach
The Object Model Framework adopts a class-driven approach, where the instantiation of the framework involves providing a set of classes. These classes serve as the blueprint for the objects that will later populate the object model.
Upon creating the object model instance, users pass a collection of classes as parameters. Each class defines the structure and properties that the corresponding objects within the framework will possess. This class-driven methodology encapsulates the essence of the object model, allowing for dynamic and intuitive class management.

## Declarative Relationship Description
Each of classes defines the properties (fields) that objects of these classes will possess.
For each field, the user specifies its type (e.g., a class from those passed during the creation of ObjectModel). Subsequent relationships are defined using the IDs of objects of that type. Additionally, a field can possess roles, such as:

- ID IAM_Role: The object ID, allowing easy identification.
- Owner IAM_Role: Signifying that the object "belongs" to the specified ID, and during graph visualization, it will be displayed within the cluster of the owning object.
- List Name IAM_Role: In this case, the field's value is used as the name of a list displayed in the owner's cluster.
- List Item IAM_Role: The value of the field in this list. These two field settings are used in tandem.
- Link In IAM_Role: An arrow pointing from the specified ID to this object.
- Link Out IAM_Role: An arrow pointing from this object to the specified ID.

Not all fields need to be filled for a specific object, allowing selective visualization of relationships based on the object's properties.

This approach allows users to define how objects can be related to each other declaratively. When describing classes, users articulate how objects can be interconnected. Upon receiving object data, the filled properties determine which specific objects these relationships are established with.

By adopting this declarative methodology, users can succinctly express complex relationships, facilitating a clear and intuitive representation of object interconnections within the Object Model Framework. Explore the versatility of declarative relationship definition to enhance your understanding and visualization of intricate object networks.

## Dynamic Object Structure in Memory
The Object Model Framework operates on a dynamic object structure in memory, leveraging a predefined set of classes specified during the instantiation of the framework. This approach allows users to create instances of these classes, constructing a coherent structure of interconnected objects in memory.
Objects created within the Object Model Framework not only encapsulate the properties defined in their respective classes but also forge relationships as dictated by the class specifications. This interconnectedness forms a rich and dynamic object graph in memory, representing the structure and associations among various entities.
By allowing users to create objects from predefined classes, the Object Model Framework adheres to fundamental principles of object-oriented programming. Users can instantiate, manipulate, and interconnect objects in a way that closely aligns with the conceptualization of entities and relationships in the real-world domain.

## Integration with External Systems
The Object Model Framework provides seamless integration with external systems, allowing the structure within the framework to mirror and act as an analogy to the structure in the external system. This integration is facilitated through standardized functions designed to interact with the external environment.

- Retrieving Objects
Effortlessly retrieve objects from the external system using unified functions. Obtain either all objects or a subset, enabling a consistent and efficient mechanism for accessing data.
- Disconnecting Objects
Disconnect from objects in the external system to manage resources and connections effectively. Choose to disconnect from all objects or a specific subset.
- Creating Objects
Create objects within the external system using a unified function. Dynamically generate entities in the external environment, ensuring consistency and coherence with the internal object model.
- Deleting Objects
Effortlessly remove objects from the external system, maintaining synchronization between the internal object model and the external structure.

These unified functions enable a seamless and unified approach to interact with external systems. By providing standardized mechanisms for retrieval, disconnection, creation, and deletion, the Object Model Framework ensures synchronization and consistency between the internal object structure and the corresponding entities in the external environment.

The implementation of integration functions is delegated to user-defined classes, reflecting the specific requirements for interacting with external systems. Users have the flexibility to customize these functions according to the intricacies of the target systems. API calls, database queries, or other communication methods can be implemented as needed.

## Graph Visualization
Upon constructing the object model within the Object Model Framework, a powerful graph visualization function is available. This feature provides valuable insights and a visual representation of the intricate relationships between objects, serving as a potent tool for analysis.

Graph Drawing Lambda_Function
The draw_graph function facilitates the visualization of the entire object structure, showcasing the connections and dependencies between different entities. This function leverages the relationships and properties defined within the object model, offering a comprehensive overview.

The Object Model Framework integrates the [**Graph Drawing Utility**](Graph_Drawing_Utility.md) for visualizing object relationships. The utility is employed to visualize the object graph.

## Conclusion
In conclusion, the Object Model Framework offers a comprehensive and flexible solution for managing and analyzing complex object-oriented structures. By adopting a class-driven approach, users can dynamically create, manage, and visualize objects, fostering a dynamic and intuitive environment.

The framework's integration capabilities further extend its utility by providing standardized functions for interacting with external systems. Users can tailor the integration functions within user-defined classes, ensuring a seamless connection between the internal object model and diverse external environments.

The highlight of the framework is the graph visualization function, which serves as a powerful tool for analysis. By visually representing the relationships and dependencies between objects, users gain valuable insights into the structure of their system, facilitating informed decision-making and optimization.

Incorporate the Object Model Framework into your projects to benefit from its declarative class description, custom integration capabilities, and graph visualization features. Empower your object-oriented design, streamline external system interactions, and gain a deeper understanding of the relationships within your system.

The combination of object modeling, integration with external systems, and graph visualization empowers users to make informed decisions about their object-oriented structures. Explore the graph visualization function to unlock a new dimension of understanding and optimization within the Object Model Framework.

## Requirements

- [**Python 3.7**](https://www.python.org/)
- [**Graphviz**](https://graphviz.gitlab.io/download/)

## Contributing

To contribute to diagram, check out [contribution guidelines](docs/CONTRIBUTING.md).

## License

This repository and its projects are licensed under the MIT License. Refer to the [LICENSE](docs/LICENSE.md) file for details.

## Example

[Source code](../Demo.py)

<img src="../img/Demo.png">

## Links

| Read Me       | Yet Another AWS Analyser | Object Model Framework | Graph Drawing Utility |
| ------------- | ------------------------ | ---------------------- | --------------------- |
| [<img src="../img/Home.png" width="100" height="100">](../ReadMe.md) | [<img src="../img/Yet_Another_AWS_Analyser.png" width="100" height="100">](../docs/Yet_Another_AWS_Analyser.md) | [<img src="../img/Object_Model_Framework.png" width="100" height="100">](../docs/Object_Model_Framework.md) | [<img src="../img/Graph_Drawing_Utility.png" width="100" height="100">](../docs/Graph_Drawing_Utility.md) |