# Automated (Python) Module Documentation in README

## What's this?

Automated docstring extraction and creation/update of documentation (of python modules) in README File.

### Why?

Because it's nice :-)

### How?

[doc_to_md.py](src/doc_to_md/doc_to_md.py) loops through all Python files in the Repository and extracts the function calls + the
corresponding short description from the docstrings. These are added to a dictionary and afterwards converted to
a Markdown Table. Finally, the section **_Functions & Classes_** is appended / updated in the README File.

**_Works in GitHub, GitLab & Bitbucket :-)_**

> _[Documentation](./How_to_setup_the_pipelines.md) on how to set up the pipelines to update a file on every push._

---

### [**_Step-by-step guide_**](https://github.com/ziselsberger/use_doc_to_readme) on how to integrate _doc_to_readme_ in your Repository

---

_Copyright &copy; 2023 by Mirjam Ziselsberger_  
_This code is free to use under the terms of the [MIT license](/LICENSE)._

## Functions & Classes  

### [doc_to_md.py](./src/doc_to_md/doc_to_md.py)

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