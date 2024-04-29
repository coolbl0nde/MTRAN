class TreeNode:
    def __init__(self, type, children=None, value=None, data_type = None):
        self.type = type
        self.children = children or []
        self.value = value
        self.data_type = data_type

    def add_child(self, child):
        if isinstance(child, list):
            self.children += child
            return

        self.children.append(child)


