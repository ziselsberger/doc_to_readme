# Automated (Python) Module Documentation in README

## What's this?

Automated docstring extraction and creation/update of documentation (of python modules) in README File.

### Why?

Because it's nice :-)

### How?

[doc_to_md.py](src/doc_to_md.py) loops through all Python files in the Repository and extracts the function calls + the
corresponding short description from the docstrings. These are added to a dictionary and afterwards converted to
a Markdown Table. Finally, the section **_Functions & Classes_** is appended / updated in the README File.

**_Works in GitHub, GitLab & Bitbucket :-) Yay!_**

> _[Documentation](./How_to_setup_the_pipelines.md) on how to set up the pipelines to update a file on every push._

---

### [**_Step-by-step guide_**](https://github.com/ziselsberger/use_doc_to_readme) on how to integrate _doc_to_readme_ in your Repository

---

_Copyright &copy; 2023 by Mirjam Ziselsberger_  
_This code is free to use under the terms of the [MIT license](/LICENSE)._

## Functions & Classes  
| Module | Type | Name/Call | Description |
| --- | --- | --- | --- |
| [main](./main.py) | function  | `hello_world()` | Just says hello |
| [functions](./src/functions.py) | function  | `mean(x: int = 1, y: int = 2) -> float` | Calculate mean of x and y. |
| [functions](./src/functions.py) | function  | `add(x: int = 4, y: int = 5) -> int` | Add two numbers (x and y). |
| [functions](./src/functions.py) | function  | `multiply(x: int = 6, y: int = 7) -> int` | Multiply two numbers (x and y). |
| [classes](./src/classes.py) | class  | `TechnicalQualityTests` | Base class for all technical QC Tests. |
| [classes](./src/classes.py) | method (TechnicalQualityTests) | `add_to_dict(self, test_name: str, test_result: Tuple[bool, str]) -> None` | Add QC result to dictionary. |

Created with: [doc_to_readme](https://github.com/ziselsberger/doc_to_readme)  
[MIT](https://github.com/ziselsberger/doc_to_readme/blob/main/LICENSE) &copy; 2023 Mirjam Ziselsberger

---
**Last Update:** 2023-04-20