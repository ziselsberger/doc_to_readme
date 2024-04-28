import os
import unittest

import src.doc_to_md.doc_to_md as dtm


class LoopThroughRepo(unittest.TestCase):
    def setUp(self) -> None:
        if os.getcwd().endswith("tests"):
            os.chdir("..")
        dtm.summary = {}
        self.file = "./TEST_README.md"
        self.module = "functions_for_testing"
        self.function = "add"
        self.remaining_modules = ['doc_to_md', 'classes_for_testing', 'test_dtm']
        self.correct_link = '[functions_for_testing.py](./tests/functions_for_testing.py)'
        self.correct_dict = {
            'doc': 'Add two numbers (x and y).',
            'fn': 'add(x: int = 4, y: int = 5) -> int',
            'parent_class': None,
            'type': 'function'
        }

    def test_loop_through_repo(self):
        dtm.loop_through_repo(file=self.file)
        self.assertEqual(
            dtm.summary[self.module]['Link'],
            self.correct_link
        )
        self.assertEqual(
            dtm.summary[self.module][self.function],
            self.correct_dict
        )

    def test_loop_through_repo_specified_modules(self):
        dtm.loop_through_repo(
            file=self.file,
            specified_modules=(self.module,)
        )
        self.assertEqual(
            dtm.summary[self.module]['Link'],
            self.correct_link
        )
        self.assertEqual(
            dtm.summary[self.module][self.function],
            self.correct_dict
        )

    def test_loop_through_repo_exclude_modules(self):
        dtm.loop_through_repo(
            file=self.file,
            exclude_modules=(self.module,)
        )
        with self.assertRaises(KeyError):
            print(dtm.summary[self.module])
        self.assertListEqual(
            list(dtm.summary.keys()),
            self.remaining_modules
        )


if __name__ == '__main__':
    unittest.main()
