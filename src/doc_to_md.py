"""Contains methods to gather information about functions and classes in the current repository.

The gathered information can be added to a Markdown file, either as List or Table.

Helpful sources:
- https://www.codeguage.com/courses/python/functions-code-objects
- https://stackoverflow.com/questions/196960/can-you-list-the-keyword-arguments-a-function-receives
- https://gabrielelanaro.github.io/blog/2014/12/12/extract-docstrings.html
"""

__author__ = "Mirjam Ziselsberger"
__email__ = ["ziselsberger@gmail.com", "mirjam.ziselsberger@student.uibk.ac.at"]

import argparse
import ast
import datetime
import glob
import inspect
import os
from typing import Callable, Tuple, Dict, Optional, Union

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

    function_definition = f"{name}{str(inspect.signature(func))}"
    converted = f"\n* ### `{function_definition}`  \n" \
                f"      {short_description}\n"
    docu += converted
    return name, function_definition, short_description


def loop_through_repo(
        exclude_modules: Tuple[str, ...] = (),
        specified_modules: Optional[Tuple[str, ...]] = None
) -> None:
    """Collect documentation from functions & classes

    Loop through all .py modules in the current Repo and add
    function & class infos to a dictionary ('summary').
    To exclude modules, add their name to argument 'exclude_modules'.

    :param exclude_modules: Names of excluded modules
    :param specified_modules: Names of specified modules
    """
    global summary
    script_dir = os.path.dirname(os.path.abspath(__file__))
    modules = glob.glob(f"{script_dir}/../**/*.py", recursive=True)

    for module_path in modules:
        module_name = os.path.basename(module_path).replace(".py", "")
        if specified_modules:
            if module_name not in specified_modules: continue
        elif module_name in exclude_modules:
            continue
        summary[module_name] = parse_through_file(module_path)
        link = f"[{module_name}](.{module_path.split('..')[1]})"
        summary[module_name]["Link"] = link


def add_summary_to_md(overview_dict: Dict[str, Optional[Union[str, Dict[str, str]]]], markdown: str):
    """Add Table with all Functions & Classes to Markdown file.

    :param overview_dict: Dictionary with function & class information
    :param markdown: Path to markdown file
    """
    with open(markdown, 'ab+') as f:
        f.write(f"\n## Functions & Classes  \n".encode('utf-8'))
        table = "| Module | Type | Name/Call | Description |\n| --- | --- | --- | --- |\n"
        for mod, functions in overview_dict.items():
            link = overview_dict.get(mod).get("Link")
            for _, info in functions.items():
                try:
                    func, desc, t, p = info.values()
                except ValueError:
                    pass
                except AttributeError:
                    pass
                else:
                    table += f"| {link} | {t} {f'({p})' if p is not None else ''} | `{func}` | {desc} |\n"

        f.write(table.encode('utf-8'))
        f.write(f"\n---\n**Created:** 2023-03-15  \n"
                f"**Last Update:** {datetime.date.today()}".encode('utf-8'))


def update_markdown_file(file: str = "../README.md",
                         exclude_modules: Tuple[str, ...] = (),
                         specified_modules: Optional[Tuple[str, ...]] = None):
    """Add/update 'Functions & Classes' Section in Markdown file.

    :param exclude_modules: Names of excluded modules
    :param specified_modules: Names of specified modules
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

    loop_through_repo(exclude_modules=exclude_modules,
                      specified_modules=specified_modules)
    add_summary_to_md(summary, file)

    # with open(file, 'ab+') as f:
    #     f.write(docu.encode('utf-8'))


def parse_through_file(file):
    with open(file) as fd:
        tree = ast.parse(fd.read())
        func_docs = {f.name: (ast.get_docstring(f).split("\n\n")[0].replace('\n', ' ').replace('  ', ' ')
                              if ast.get_docstring(f) else None)
                     for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.ClassDef))}

        class_definitions = [node for node in tree.body if isinstance(node, ast.ClassDef)]
        method_names = {node.name: class_def.name for class_def in class_definitions
                        for node in class_def.body if isinstance(node, ast.FunctionDef)}

    with open(file, 'r') as f:
        functions = {}
        end = True
        for line in f.readlines():
            rm_blanks = line.strip()
            if rm_blanks.startswith("def "):
                function_name = rm_blanks.split("def ")[1].split("(")[0]
                if function_name.startswith("__"): continue
                functions[function_name] = {"fn": None,
                                            "doc": func_docs.get(function_name),
                                            "type": "method" if function_name in method_names else "function",
                                            "parent_class": method_names.get(function_name)}
                functions[function_name]["fn"] = rm_blanks.split("def ")[1]
                end = rm_blanks.endswith(":")
            elif rm_blanks.startswith("class "):
                function_name = rm_blanks.split("class ")[1].split("(")[0].rstrip(":")
                if function_name.startswith("__"): continue
                functions[function_name] = {"fn": None,
                                            "doc": func_docs.get(function_name),
                                            "type": "class",
                                            "parent_class": method_names.get(function_name)}
                end = rm_blanks.endswith(":")
            elif not end:
                rm_blanks = rm_blanks.split('"""')[0]
                end = rm_blanks.endswith(":")
                functions[function_name]["fn"] += rm_blanks

    for name in functions.keys():
        try:
            functions[name]['fn'] = functions[name]['fn'].replace(',', ', ').replace('  ', ' ').rstrip(':')
        except AttributeError:
            functions[name]['fn'] = name

    return functions


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exclude", required=False, help="Exclude modules", default=[], nargs='+')
    parser.add_argument("-m", "--modules", required=False, help="Specify modules", default=[], nargs='+')
    args = parser.parse_args()

    exclude = ("test", "doc_to_md")
    if args.exclude:
        exclude += tuple(args.exclude)

    specified_modules = args.modules

    update_markdown_file(exclude_modules=exclude,
                         specified_modules=specified_modules)
