# Automated Python Documentation in README file

> [!NOTE]
> Available on [PyPI](https://pypi.org/project/doc-to-readme)

## What's this?

Automated docstring extraction and creation/update of documentation of python modules in the README File.

### Why should I use it?

Because it's nice to have a quick overview of all the functions, classes and methods of your module documented in the README file ;-)

### How does it work?

[doc_to_md.py](src/doc_to_md/doc_to_md.py) loops through all Python files in the Repository, and extracts the function calls & the corresponding short description from the docstrings. These are added to a dictionary and afterwards converted to a Markdown Table. Finally, the section **_Functions & Classes_** is appended / updated in the README File.

There are two options how to use it:  
a) [CI Pipeline](#a-add-to-pipeline-github-gitlab-bitbucket-or-azure-devops)  
b) [Python Package](#b-install--use-the-python-package)   

### a) include it in your CI Pipeline (GitHub, GitLab, Bitbucket or Azure Devops)
Check out this [**_Step-by-step guide_**](https://github.com/ziselsberger/use_doc_to_readme) on how to integrate _doc_to_readme_ in your Repository.

### b) install & use the Python Package

```shell
pip install doc-to-readme
```

- **Use within Python** 
```python
import doc_to_md.doc_to_md as dtm

dtm.update_markdown_file(
    file="README.md",
    root_dir=None,              # Directory used as root for searching modules, defaults to folder containing README.md
    exclude_modules=None,       # List of modules to be excluded
    specified_modules=None,     # Only these modules will be included
    separate=True               # Create one table per module
)
```

- **Command Line**
```shell
python -m doc_to_md.doc_to_md -f "README.md" [-r ROOT_DIR] [-e EXCLUDE_MODULES] [-m SELECTED_MODULES] [--separated]

-r ROOT_DIR             # Directory used as root for searching modules, defaults to folder containing README.md
-e EXCLUDE_MODULES      # List of modules to be excluded
-m SELECTED_MODULES     # Only these modules will be included
--separated             # Create one table per module
```

---

_Copyright &copy; 2023 by Mirjam Ziselsberger_  
_This code is free to use under the terms of the [MIT license](/LICENSE)._

## Functions & Classes  

### [doc_to_md.py](./src/doc_to_md/doc_to_md.py)

| Type | Name/Call | Description |
| --- | --- | --- |
| function  | `loop_through_repo(file: str, root_dir: str = None, exclude_modules: Optional[Tuple[str, ...]] = None, specified_modules: Optional[Tuple[str, ...]] = None) -> None` | Collect documentation from functions & classes. |
| function  | `add_summary_to_md(overview_dict: Dict[str, Optional[Union[str, Dict[str, str]]]], markdown: str, separate: bool = True)` | Add Table with all Functions & Classes to Markdown file. |
| function  | `update_markdown_file(file: str = "../../README.md", root_dir: str = None, exclude_modules: Optional[Tuple[str, ...]] = ("test", "functions_for_testing", "classes_for_testing", "doc_to_md"), specified_modules: Optional[Tuple[str, ...]] = None, separate: bool = True)` | Add/update 'Functions & Classes' Section in Markdown file. |
| function  | `parse_through_file(file: str) -> Dict[str, Dict[str, str]]` | Parse through file, return dict with classes and functions. |

### [test_dtm.py](./tests/test_dtm.py)

| Type | Name/Call | Description |
| --- | --- | --- |
| class  | `LoopThroughRepo` | None |
| method (LoopThroughRepo) | `setUp(self) -> None` | None |
| method (LoopThroughRepo) | `test_loop_through_repo(self)` | None |
| method (LoopThroughRepo) | `test_loop_through_repo_specified_modules(self)` | None |
| method (LoopThroughRepo) | `test_loop_through_repo_exclude_modules(self)` | None |

Created with: [doc_to_readme](https://github.com/ziselsberger/doc_to_readme)  
[MIT](https://github.com/ziselsberger/doc_to_readme/blob/main/LICENSE) &copy; 2023 Mirjam Ziselsberger

---
**Last Update:** 2024-12-13
