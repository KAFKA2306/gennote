import ast
from pathlib import Path
import unittest


SOURCE_DIR = Path(__file__).parent / "src"


class RepositoryTest(unittest.TestCase):
    def test_python_sources_parse(self):
        for path in SOURCE_DIR.glob("*.py"):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_post_script_has_one_main_entrypoint(self):
        path = SOURCE_DIR / "post.py"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        guards = [
            node
            for node in tree.body
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
        ]
        self.assertEqual(len(guards), 1)


if __name__ == "__main__":
    unittest.main()
