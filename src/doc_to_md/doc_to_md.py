#!/usr/bin/env python3
"""Gather information about functions and classes in the current repository.

The information is converted to a table and appended to a Markdown file.

Helpful sources:
- https://www.codeguage.com/courses/python/functions-code-objects
- https://stackoverflow.com/questions/196960/can-you-list-the-keyword-arguments-a-function-receives
- https://gabrielelanaro.github.io/blog/2014/12/12/extract-docstrings.html
"""

__author__ = "Mirjam Ziselsberger"
__email__ = "ziselsberger@gmail.com"
__copyright__ = "Copyright 2023, Mirjam Ziselsberger"
__license__ = "MIT License"

import argparse
import ast
import datetime
import glob
import os
from typing import Tuple, Dict, Optional, Union

summary = {}


def loop_through_repo(
        file: str,
        root_dir: str = None,
        exclude_modules: Optional[Tuple[str, ...]] = None,
        specified_modules: Optional[Tuple[str, ...]] = None
) -> None:
    """Collect documentation from functions & classes

    Loop through all .py modules in the root directory of this repo and add
    function & class info to a dictionary ('summary').
    To exclude modules, add their name to argument 'exclude_modules'.

    :param file: Path to markdown file
    :param root_dir: Path to root directory
    :param exclude_modules: Names of excluded modules
    :param specified_modules: Names of specified modules
    """
    global summary

    if not root_dir:
        root_dir = os.path.dirname(os.path.abspath(file))

    skip = ["site-packages", "venv", "__init__"]
    modules = sorted([m for m in glob.glob(f"{root_dir}/**/*.py", recursive=True)
                      if not any(map(m.__contains__, skip))])

    if exclude_modules is None:
        exclude_modules = []

    for module_path in modules:
        module_name = os.path.basename(module_path).replace(".py", "")
        if specified_modules:
            if module_name not in specified_modules: continue
        elif module_name in exclude_modules:
            continue
        print(f"Loop through: {module_path}")
        try:
            summary[module_name] = parse_through_file(module_path)
        except TypeError:
            continue
        path = module_path.replace(root_dir, '.')
        link = f"[{os.path.basename(path)}]({path})"
        summary[module_name]["Link"] = link


def add_summary_to_md(
        overview_dict: Dict[str, Optional[Union[str, Dict[str, str]]]],
        markdown: str,
        separate: bool = True
):
    """Add Table with all Functions & Classes to Markdown file.

    :param overview_dict: Dictionary with function & class information
    :param markdown: Path to markdown file
    :param separate: Create one table per module
    """
    with open(markdown, 'ab+') as f:
        f.write(f"\n## Functions & Classes  \n".encode('utf-8'))
        if not separate:
            table = "| Module | Type | Name/Call | Description |\n| --- | --- | --- | --- |\n"
        for mod, functions in overview_dict.items():
            link = overview_dict.get(mod).get("Link")
            if len(functions) <= 1: continue
            if separate:
                table = f"\n### {link}\n\n| Type | Name/Call | Description |\n| --- | --- | --- |\n"
            for _, info in functions.items():
                try:
                    func, desc, t, p = info.values()
                except ValueError:
                    pass
                except AttributeError:
                    pass
                else:
                    if separate:
                        table += f"| {t} {f'({p})' if p is not None else ''} | `{func}` | {desc} |\n"
                    else:
                        table += f"| {link} | {t} {f'({p})' if p is not None else ''} | `{func}` | {desc} |\n"
            if separate:
                f.write(table.encode('utf-8'))
        if not separate:
            f.write(table.encode('utf-8'))
        f.write(f"\nCreated with: "
                f"[doc_to_readme](https://github.com/ziselsberger/doc_to_readme)  \n"
                f"[MIT](https://github.com/ziselsberger/doc_to_readme/blob/main/LICENSE) "
                f"&copy; 2023 Mirjam Ziselsberger\n".encode('utf-8'))
        f.write(f"\n---\n**Last Update:** {datetime.date.today()}".encode('utf-8'))


def update_markdown_file(file: str = "../../README.md",
                         root_dir: str = None,
                         exclude_modules: Optional[Tuple[str, ...]] = ("test",
                                                                       "functions_for_testing",
                                                                       "classes_for_testing",
                                                                       "doc_to_md"),
                         specified_modules: Optional[Tuple[str, ...]] = None,
                         separate: bool = True):
    """Add/update 'Functions & Classes' Section in Markdown file.

    :param file: Path to Markdown file, defaults to '../README.md'
    :param root_dir: Path to root directory
    :param exclude_modules: Names of excluded modules
    :param specified_modules: Names of specified modules
    :param separate: Create one table per module
    """
    try:
        with open(file, "r") as f:
            content = []
            for line in f.readlines():
                if line.startswith("## Functions & Classes"):
                    break
                content.append(line)

        if content:
            with open(file, "w") as f:
                f.writelines(content[:-1]) if content[-1] == "\n" else f.writelines(content)
    except FileNotFoundError:
        print(f"Create file: {file}")
        pass

    loop_through_repo(
        file=file,
        root_dir=root_dir,
        exclude_modules=exclude_modules,
        specified_modules=specified_modules)
    add_summary_to_md(summary, file, separate=separate)


def parse_through_file(file: str) -> Dict[str, Dict[str, str]]:
    """Parse through module and gather info on classes and functions

    :param file: Module path
    :returns: Dictionary containing information on classes and functions
    """

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
    parser.add_argument("-f", "--file", required=False, help="Path to README", default="../../README.md")
    parser.add_argument("-d", "--root_dir", required=False, help="Path to rood dir", default=None)
    parser.add_argument("-e", "--exclude", required=False, help="Exclude modules", default=[], nargs='+')
    parser.add_argument("-m", "--modules", required=False, help="Specify modules", default=[], nargs='+')
    parser.add_argument("--separated", required=False, help="Separate tables for each module", action='store_true')
    args = parser.parse_args()

    exclude = ("test", "functions_for_testing", "classes_for_testing")
    if args.exclude is not None and args.exclude != [""]:
        exclude += tuple(args.exclude)

    selected_modules = None if args.modules == [""] else args.modules
    root_directory = None if args.root_dir == "" else args.root_dir

    print(f"Path to README: {args.file}")
    print(f"Exclude modules: {exclude}")
    print(f"Selected modules: {selected_modules}")
    if root_directory:
        print(f"Specified root directory: {root_directory}")

    update_markdown_file(file=args.file,
                         root_dir=root_directory,
                         exclude_modules=exclude,
                         specified_modules=selected_modules,
                         separate=args.separated)
