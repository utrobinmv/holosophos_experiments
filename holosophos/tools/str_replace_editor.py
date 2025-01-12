from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from holosophos.files import WORKSPACE_DIR

# Global state for undo operations
_file_history: Dict[str, List[List[str]]] = defaultdict(list)


def _save_file_state(path: Path, content: List[str]) -> None:
    _file_history[str(path.resolve())].append(content.copy())


def _write(path: Path, file_text: str, overwrite: bool) -> str:
    if not overwrite:
        assert (
            not path.exists()
        ), f"Cannot write file, path already exists: {path}. Pass overwrite=True"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(file_text)
    _save_file_state(path, file_text.splitlines(True))
    return file_text


def _view(
    path: Path,
    view_start_line: Optional[int] = None,
    view_end_line: Optional[int] = None,
    max_output_length: int = 2048,
) -> str:
    assert path.exists(), f"Path does not exist: {path}"
    if not path.is_file():
        output = []
        for level1 in path.iterdir():
            if level1.name.startswith("."):
                continue
            output.append(str(level1.relative_to(path)))
            if level1.is_dir():
                for level2 in level1.iterdir():
                    if level2.name.startswith("."):
                        continue
                    output.append(f"  {level2.relative_to(path)}")
        return "\n".join(output)

    lines = path.open().readlines()
    enum_start_line = 1
    if view_start_line or view_end_line:
        if not view_start_line:
            view_start_line = 1
        if not view_end_line:
            view_end_line = len(lines)
        view_end_line = view_end_line if view_end_line <= len(lines) else len(lines)
        view_end_line = view_end_line if view_end_line != -1 else len(lines)
        assert view_start_line >= 1, "Line numbers must start at 1"
        assert view_end_line >= 1, "Line numbers must start at 1"
        assert (
            view_start_line <= view_end_line
        ), "Incorrect view parameters, start is higher than end"
        lines = lines[view_start_line - 1 : view_end_line]
        enum_start_line = view_start_line
    output = []
    total_length = 0
    for i, line in enumerate(lines, enum_start_line):
        prefix = f"{i:6d}\t"
        current_line = prefix + line
        if total_length + len(current_line) > max_output_length:
            space_for_text = max_output_length - total_length - len(prefix)
            space_for_text = max(space_for_text, 0)
            output.append(prefix + line[:space_for_text] + " <response clipped>")
            break
        output.append(current_line)
        total_length += len(current_line)
    return "".join(output)


def _insert(path: Path, insert_line: int, new_str: str) -> str:
    assert path.is_file(), f"File not found: {path}"
    lines = path.open().readlines()
    assert 0 <= insert_line <= len(lines), f"Invalid insert_line: {insert_line}"
    _save_file_state(path, lines)
    lines.insert(insert_line, new_str if new_str.endswith("\n") else new_str + "\n")
    path.open("w").writelines(lines)
    return "".join(lines)


def _str_replace(path: Path, old_str: str, new_str: str) -> str:
    assert path.is_file(), f"File not found: {path}"
    content = path.open().read()
    count = content.count(old_str)
    assert count != 0, "old_str not found in file"
    assert count == 1, "old_str is not unique in file"
    _save_file_state(path, content.splitlines(True))
    new_content = content.replace(old_str, new_str)
    path.open("w").write(new_content)
    return new_content


def _undo_edit(path: Path) -> str:
    text_path = str(path.resolve())
    assert text_path in _file_history, f"No edit history available for: {text_path}"
    assert _file_history[text_path], f"No edit history available for: {text_path}"
    previous_state = _file_history[text_path].pop()
    path.open("w").writelines(previous_state)
    return "".join(previous_state)


def str_replace_editor(
    command: str,
    path: str,
    file_text: Optional[str] = None,
    old_str: Optional[str] = None,
    new_str: Optional[str] = None,
    insert_line: Optional[int] = None,
    view_start_line: Optional[int] = None,
    view_end_line: Optional[int] = None,
    overwrite: Optional[bool] = False,
) -> str:
    """
    Custom editing tool for viewing, creating and editing files.
    State is persistent across command calls and discussions with the user.
    If `path` is a file, `view` displays the result of applying `cat -n`.
    Attention! It means that for every line it's number is prepended! Do not expect view to return the original text.
    If `path` is a directory, `view` lists non-hidden files and directories up to 2 levels deep.
    The `write` command cannot be used if the specified `path` already exists as a file.
    If a `command` generates a long output, it will be truncated and marked with `<response clipped>`.
    The `undo_edit` command will revert the last edit made to the file at `path`.

    Notes for using the `str_replace` command:
    - The `old_str` parameter should match EXACTLY one or more consecutive lines from the original file.
    - Be mindful of whitespaces!
    - If the `old_str` parameter is not unique in the file, the replacement will not be performed.
    - Make sure to include enough context in `old_str` to make it unique
    - The `new_str` parameter should contain the edited lines that should replace the `old_str`

    Examples:
        Create a file with "Hello world!": str_replace_editor("write", file_text="Hello world!")
        View a file with enumerated lines: str_replace_editor("view", "file.txt")
        View first three lines of a file: str_replace_editor("view", "file.txt", view_start_line=1, view_end_line=3)
        View lines from 5 to the end of a file: str_replace_editor("view", "file.txt", view_start_line=5)
        Replace "line1" with "line2": str_replace_editor("str_replace", "file.txt", old_str="line", new_str="line2")
        Insert "line2" after line 1: str_replace_editor("insert", "file.txt", insert_line=1, new_str="line2")

    Args:
        command: The commands to run. Allowed options are: `view`, `write`, `str_replace`, `insert`, `undo_edit`.
        path: Path to file or directory inside current work directory. Should not be absolute.
        view_start_line: Optional for view command, use to view specific lines
        view_end_line: Optional for view command, use to view specific lines
        file_text: Required for `write` command, with the content of the file to be writed.
        overwrite: Optional for `write` command. If True, the command is allowed to overwrite existing files.
        insert_line: Required for `insert` command. `new_str` will be inserted AFTER the line `insert_line` of `path`.
        new_str: Required for `str_replace` containing the new string. Required for `insert` containing the string to insert.
        old_str: Required for `str_replace` containing the string in `path` to replace.
    """
    assert not path.startswith(
        "/"
    ), "Absolute path is not supported, only relative to the work directory"
    valid_commands = ("view", "write", "str_replace", "insert", "undo_edit")

    path_obj = WORKSPACE_DIR / path

    if command == "view":
        return _view(path_obj, view_start_line, view_end_line)
    if command == "write":
        assert file_text is not None, "'file_text' is required for 'write' command"
        return _write(
            path_obj, file_text, overwrite if overwrite is not None else False
        )
    if command == "insert":
        assert insert_line is not None, "'insert_line' is required for 'insert' command"
        assert new_str is not None, "'new_str' is required for 'insert' command"
        return _insert(path_obj, insert_line, new_str)
    if command == "str_replace":
        assert old_str is not None, "'old_str' is required for 'str_replace' command"
        assert new_str is not None, "'new_str' is required for 'str_replace' command"
        return _str_replace(path_obj, old_str, new_str)
    if command == "undo_edit":
        return _undo_edit(path_obj)
    assert False, f"Not a valid command! List of commands: {valid_commands}"
