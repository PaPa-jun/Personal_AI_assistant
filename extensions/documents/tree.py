import os, json

class Node:
    """
    # The node of sort tree.

    Every node is a text block.

    :param label: The label of text block.
    :param cls: The class index of text block.
    :param conf: The confidence of text block.
    :param box: The coordinates of text block.
    """
    def __init__(self, label, cls, conf, box) -> None:
        self.label = label  # The label of the text block.
        self.cls = cls  # The class index of the text block.
        self.conf = conf  # The confidence level of the text block.
        self.box = box  # The coordinates of the text block as [x1, y1, x2, y2].
        self.children = []  # List to hold child nodes.
        self.units = []  # List to hold content units associated with this node.

class Tree:
    """
    # The sort tree.
    """
    def __init__(self) -> None:
        self.root: Node  # The root of the tree, initially not set.
        self.nodes = []  # List to store all nodes in the tree.
        self.data = []  # List to store the serialized data of nodes.

    def find_overlap(self, node, axis, epsilon, overlapping_nodes) -> list:
        """
        # Find nodes that overlap with the given node on the specified axis.

        :param node: The node to check for overlaps.
        :param axis: The axis on which to check overlap ('x' or 'y').
        :param epsilon: The tolerance for overlap.
        :param overlapping_nodes: Pre-filtered list of potentially overlapping nodes.
        :return: List of overlapping nodes.
        """
        results = []
        if axis == 'x':  # Check overlap on the x-axis.
            for element in self.nodes:
                if element.box[1] >= node.box[1]: continue  # Skip if above the node.
                if element.box[2] >= node.box[0] and element.box[0] <= node.box[2]:  # Check for horizontal overlap.
                    results.append(element)
        elif axis == 'y':  # Check overlap on the y-axis.
            for element in overlapping_nodes:
                if abs(element.box[3] - node.box[3]) < epsilon:  # Check for vertical proximity.
                    results.append(element)
        return results

    def find_nearest(self, overlapping_nodes, epsilon) -> list:
        """
        # Find the nearest node vertically from a list of overlapping nodes.

        :param overlapping_nodes: List of nodes overlapping on the x-axis.
        :param epsilon: The tolerance for proximity on the y-axis.
        :return: List of nearest nodes on the y-axis.
        """
        nearest_node = overlapping_nodes[-1]  # Take the last node as the nearest candidate.
        nearest_nodes = self.find_overlap(nearest_node, 'y', epsilon, overlapping_nodes)  # Find overlaps on y-axis.
        return nearest_nodes

    def find_parent(self, epsilon) -> None:
        """
        # Establish parent-child relationships between nodes.

        Determines the hierarchy by finding overlapping nodes and setting the parent (father) node.

        :param epsilon: The tolerance used for determining overlap/proximity.
        """
        if len(self.nodes) < 1:  # If no nodes exist, set a default empty root node.
            self.root = Node(label='empty', box=[-1, -1, -1, -1], cls=-1, conf=-1)
        for node in reversed(self.nodes):  # Iterate through nodes in reverse order.
            overlapping_on_x = self.find_overlap(node, 'x', epsilon, None)  # Find overlapping nodes on x-axis.
            if overlapping_on_x:
                nearest_nodes = self.find_nearest(overlapping_on_x, epsilon)  # Find nearest node on y-axis.
                nearest_nodes[-1].children.append(node)  # Append the current node as a child of the nearest node.
            elif node == self.nodes[0]:  # If it's the first node, set it as the root.
                self.root = node
            else:
                self.nodes[0].children.append(node)  # Otherwise, append it to the first node's children.

        for node in self.nodes:
            if len(node.children) > 1:
                node.children.sort(key=lambda s: (s.box[0]))  # Sort children by their horizontal position.

    def serialize_tree(self, root) -> None:
        """
        # Recursively traverse the tree and serialize nodes to JSON-compatible format.

        :param root: The root node from which to start the traversal.
        """
        if root is None:
            return

        data = {
            "name": root.label,
            "class": root.cls,
            "confidence": root.conf,
            "box": {
                "x1": root.box[0],
                "y1": root.box[1],
                "x2": root.box[2],
                "y2": root.box[3]
            },
            "content": "\n".join(root.units) if root.units else ""
        }

        self.data.append(data)  # Add serialized node data to the list.

        if root.children:  # Recursively process each child.
            for node in root.children:
                self.serialize_tree(node)

    def sort(self, epsilon) -> None:
        """
        # Perform the sorting process on the tree.

        Finds the parent-child relationships and then serializes the data.

        :param epsilon: The tolerance used for determining overlap/proximity.
        """
        self.find_parent(epsilon)  # Find parent-child relationships.
        self.serialize_tree(self.root)  # Serialize the tree starting from the root.

    def save_to_json(self, save_dir, name) -> None:
        """
        # Save the serialized tree data to a JSON file.

        :param save_dir: Directory where the JSON file will be saved.
        :param name: Name of the JSON file.
        """
        os.makedirs(save_dir, exist_ok=True)  # Ensure the save directory exists.
        json_data = json.dumps(self.data, indent=4, ensure_ascii=False)  # Convert data to JSON string.
        with open(os.path.join(save_dir, name), 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)  # Write JSON data to file.