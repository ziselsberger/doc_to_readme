# Automated (Python) Module Documentation in README

## What's this?

Automated docstring extraction and creation/update of documentation (of python modules) in README File.

### Why?

Because it's nice :-)

### How?

[doc_to_md.py](src/doc_to_md/doc_to_md.py) loops through all Python files in the Repository and extracts the function calls + the
corresponding short description from the docstrings. These are added to a dictionary and afterwards converted to
a Markdown Table. Finally, the section **_Functions & Classes_** is appended / updated in the README File.

### Install & Use Python Package

Currently available on [TestPyPI](https://test.pypi.org/project/doc-to-markdown-mz/).
 
```shell
pip install -i https://test.pypi.org/simple/ doc-to-markdown-mz
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
-s SELECTED_MODULES     # Only these modules will be included
--separated             # Create one table per module
```

---

### Add to Pipeline (GitHub, GitLab or Bitbucket)
_[Documentation](./How_to_setup_the_pipelines.md) on how to set up the pipelines to update a file on every push._

> ### [**_Step-by-step guide_**](https://github.com/ziselsberger/use_doc_to_readme) on how to integrate _doc_to_readme_ in your Repository

---

_Copyright &copy; 2023 by Mirjam Ziselsberger_  
_This code is free to use under the terms of the [MIT license](/LICENSE)._

## Functions & Classes  
### [doc_to_md](./src/doc_to_md/doc_to_md.py)

| Type | Name/Call | Description |
| --- | --- | --- |
| function  | `loop_through_repo(file: str, root_dir: str = None, exclude_modules: Tuple[str, ...] = (), specified_modules: Optional[Tuple[str, ...]] = None) -> None` | Collect documentation from functions & classes |
| function  | `add_summary_to_md(overview_dict: Dict[str, Optional[Union[str, Dict[str, str]]]], markdown: str, separate: bool = True)` | Add Table with all Functions & Classes to Markdown file. |
| function  | `update_markdown_file(file: str = "../README.md", root_dir: str = None, exclude_modules: Tuple[str, ...] = (), specified_modules: Optional[Tuple[str, ...]] = None, separate: bool = True)` | Add/update 'Functions & Classes' Section in Markdown file. |
| function  | `parse_through_file(file: str) -> Dict[str, Dict[str, str]]` | Parse through module and gather info on classes and functions |

Created with: [doc_to_readme](https://github.com/ziselsberger/doc_to_readme)  
[MIT](https://github.com/ziselsberger/doc_to_readme/blob/main/LICENSE) &copy; 2023 Mirjam Ziselsberger

---
**Last Update:** 2023-04-25