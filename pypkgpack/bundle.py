from __future__ import annotations
from dataclasses import dataclass
import wisepy2
import pathlib
import base64
import ast_compat as ast
import contextlib
import io


@dataclass
class Context:
    registered_sources: dict[str, tuple[bool, str, bytes]]

    def register_module(
        self,
        module_path: list[str],
        src_path: pathlib.Path,
        source_code: str,
        *,
        is_package: bool,
    ):
        if not module_path:
            raise ValueError("a Python package is required!")
        self.registered_sources[".".join(module_path)] = (
            is_package,
            str(src_path),
            base64.b64encode(source_code.encode("utf-8")),
        )


@contextlib.contextmanager
def _enter_path(xs: list[str], x: str):
    try:
        xs.append(x)
        yield xs
    finally:
        xs.pop()


def _traverse(
    current_module_path: list[str], current_path: pathlib.Path, data: Context
):
    if current_path.is_file() and current_path.suffix == ".py":
        if current_path.name == "__init__.py":
            return
        source = current_path.read_text(encoding="utf-8")
        name = current_path.name[: -len(".py")]
        if not name.isidentifier():
            return
        with _enter_path(current_module_path, name):
            data.register_module(
                current_module_path, current_path, source, is_package=False
            )
    elif current_path.is_dir() and current_path.name.isidentifier():
        if current_path.name == "__pycache__":
            return
        entry = current_path / "__init__.py"
        name = current_path.name
        with _enter_path(current_module_path, name):
            if entry.exists():
                source = entry.read_text(encoding="utf-8")
                data.register_module(
                    current_module_path, entry, source, is_package=True
                )
            else:
                data.register_module(current_module_path, entry, "", is_package=True)
            for each in current_path.iterdir():
                _traverse(current_module_path, each, data)


@wisepy2.wise
def CLI(projectdir: str, *, out: str, dynlinkloader: bool = False):
    p = pathlib.Path(projectdir).absolute()
    ctx = Context({})
    _traverse([], p, ctx)
    buf = io.StringIO()
    if dynlinkloader:
        buf.write("from pypkgpack.importer import register_code_resource\n")
    else:
        buf.write(
            (pathlib.Path(__file__).parent / "importer.py").read_text(encoding="utf-8")
        )
    buf.write("\n")
    for fullname, (is_package, filepath, source_code) in ctx.registered_sources.items():
        node = ast.Call(
            ast.Name("register_code_resource", ctx=ast.Load()),
            [
                ast.Constant(fullname),
                ast.Constant(is_package),
                ast.Constant(filepath),
                ast.Constant(source_code),
            ],
        )
        ast.fix_missing_locations(node)
        buf.write(ast.unparse(node))
        buf.write("\n")
    with pathlib.Path(out).open("w", encoding="utf-8") as f:
        f.write(buf.getvalue())
