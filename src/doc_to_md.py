"""Contains functions to gather information about functions and classes in the current repository.

The gathered information can be added to a Markdown file, either as List or Table.

Helpful sources:
- https://www.codeguage.com/courses/python/functions-code-objects
- https://stackoverflow.com/questions/196960/can-you-list-the-keyword-arguments-a-function-receives
"""

__author__ = "Mirjam Ziselsberger"
__email__ = ["ziselsberger@gmail.com", "mirjam.ziselsberger@student.uibk.ac.at"]

import glob
import importlib.util as iu
import inspect
import os
import sys
from typing import Callable, Tuple, Dict, Optional

summary = {}
docu = ""


def doc_to_md(func: Callable) -> Tuple[str, str, str]:
    """Extract information about function/class and add to a string.

    Info is added to global variable 'docu', which is a string, that can be
    written to a Markdown file.

    :param func: function/class
    :return: Function name, call and short description.
    """
    global docu
    name = func.__name__
    short_description = func.__doc__.split("\n")[0]
    # typeof = func.__class__

    function_definition = f"{name}{str(inspect.signature(func))}"
    converted = f"\n* ### `{function_definition}`  \n" \
                f"      {short_description}\n"
    docu += converted
    return name, function_definition, short_description


def loop_through_repo(exclude_modules: Tuple[str] = ("test", "doc_to_md")):
    """Collect documentation from functions & classes

    Loop through all .py modules in the current Repo and add
    function & class infos to a dictionary ('summary').
    To exclude modules, add their name to argument 'exclude_modules'.

    :param exclude_modules: Names of excluded modules, defaults to ("test", "doc_to_md")
    """
    global docu
    global summary
    script_dir = os.path.dirname(os.path.abspath(__file__))
    modules = glob.glob(f"{script_dir}/../**/*.py", recursive=True)

    for module_path in modules:
        module_name = os.path.basename(module_path).strip(".py")
        if module_name in exclude_modules: continue
        spec = iu.spec_from_file_location("test", module_path)
        module = iu.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        functions = dir(module)
        link = f"[{module_name}](.{module_path.split('..')[1]})"
        docu += f"\n\n### Module: {link}\n"
        summary[module_name] = {"Link": link}
        for func in functions:
            if not func.startswith("__"):
                fn, fdef, fdoc = doc_to_md(getattr(module, func))
                summary[module_name][fn] = {
                    "function": fdef,
                    "docu": fdoc
                }


def add_summary_to_md(overview_dict: Dict[str, Optional[str, Dict[str, str]]], markdown: str):
    """Add Table with all Functions & Classes to Markdown file.

    :param overview_dict: Dictionary with function & class information
    :param markdown: Path to markdown file
    """
    with open(markdown, 'ab+') as f:
        f.write(f"\n## Functions & Classes  \n".encode('utf-8'))
        table = "| Module | Function/Class | Description |\n| --- | --- | --- |\n"
        for mod, functions in overview_dict.items():
            link = overview_dict.get(mod).get("Link")
            for _, info in functions.items():
                try:
                    func, desc = info.values()
                except ValueError:
                    pass
                except AttributeError:
                    pass
                else:
                    table += f"| {link} | `{func}` | {desc} |\n"
        f.write(table.encode('utf-8'))


def update_markdown_file(file: str = "../README.md"):
    """Add/update 'Functions & Classes' Section in Markdown file.

    :param file: Path to Markdown file, defaults to '../README.md'
    """
    with open(file, "r") as f:
        content = []
        for line in f.readlines():
            if line.startswith("## Functions & Classes"):
                break
            content.append(line)

    with open(file, "w") as f:
        f.writelines(content[:-1]) if content[-1] == "\n" else f.writelines(content)

    loop_through_repo()
    add_summary_to_md(summary, file)

    # with open(file, 'ab+') as f:
    #     f.write(docu.encode('utf-8'))


if __name__ == "__main__":
    update_markdown_file()

