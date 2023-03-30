import unittest

import doc_to_readme.src.doc_to_md as dtm
import doc_to_readme.src.functions as f


class ExtractInfo(unittest.TestCase):
    def setUp(self) -> None:
        dtm.docu = ""
        self.updated_docu = \
            "\n* ### `mean(x: int = 1, y: int = 2) -> float`  \n" \
            "      Calculate mean of x and y.\n"
        self.extracted_info = (
            'mean',
            'mean(x: int = 1, y: int = 2) -> float',
            'Calculate mean of x and y.'
        )

    def test_doc_to_md(self):
        extract = dtm.doc_to_md(f.mean)
        self.assertEqual(extract, self.extracted_info)
        self.assertEqual(dtm.docu, self.updated_docu)


class LoopThroughRepo(unittest.TestCase):
    def setUp(self) -> None:
        dtm.summary = {}
        self.module = "functions"
        self.function = "add"
        self.remaining_modules = ['main', 'doc_to_md', 'run_qc_checks', 'test']
        self.correct_link = '[functions](.\\src\\functions.py)'
        self.correct_dict = {
            'doc': 'Add two numbers (x and y).',
            'fn': 'add(x: int = 4, y: int = 5) -> int',
            'parent_class': None,
            'type': 'function'
        }

    def test_loop_through_repo(self):
        dtm.loop_through_repo()
        self.assertEqual(
            dtm.summary[self.module]['Link'],
            self.correct_link
        )
        self.assertEqual(
            dtm.summary[self.module][self.function],
            self.correct_dict
        )

    def test_loop_through_repo_specified_modules(self):
        dtm.loop_through_repo(specified_modules=(self.module,))
        self.assertEqual(
            dtm.summary[self.module]['Link'],
            self.correct_link
        )
        self.assertEqual(
            dtm.summary[self.module][self.function],
            self.correct_dict
        )

    def test_loop_through_repo_exclude_modules(self):
        dtm.loop_through_repo(exclude_modules=(self.module,))
        with self.assertRaises(KeyError):
            print(dtm.summary[self.module])
        self.assertListEqual(
            list(dtm.summary.keys()),
            self.remaining_modules
        )


if __name__ == '__main__':
    unittest.main()
