import unittest
from tree import Tree

class TestTree(unittest.TestCase):
    def setUp(self):
        self.tree = Tree()
        for val in [10, 5, 20, 3, 7, 15]:
            self.tree.add(val)

    def test_find_existing_node(self):
        node = self.tree.find(7)
        self.assertIsNotNone(node)
        self.assertEqual(node.data, 7)

    def test_find_nonexistent_node(self):
        node = self.tree.find(999)
        self.assertIsNone(node)

if __name__ == '__main__':
    unittest.main()
