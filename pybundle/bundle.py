from __future__ import annotations
from dataclasses import dataclass
import wisepy2
import pathlib
import base64
import pretty_doc as PD
import io
import ast_compat as ast
import contextlib


@dataclass
class Context:
    registered_sources: dict[str, tuple[bool, bytes]]

    def register_module(self, path: list[str], source_code: str, *, is_package: bool):
        if not path:
            raise ValueError("a Python package is required!")
        self.registered_sources['.'.join(path)] = (is_package, base64.b64encode(source_code.encode('utf-8')))

@contextlib.contextmanager
def _enter_path(xs: list[str], x: str):
    try:
        xs.append(x)
        yield xs
    finally:
        xs.pop()

def _traverse(current_module_path: list[str], current_path: pathlib.Path, data: Context):
    if current_path.is_file() and current_path.suffix == '.py':
        if current_path.name == '__init__.py':
            return
        source = current_path.read_text(encoding='utf-8')
        name = current_path.name[:-len(".py")]
        if not name.isidentifier():
            return
        with _enter_path(current_module_path, name):
            data.register_module(current_module_path, source, is_package=False)
    elif current_path.is_dir() and current_path.name.isidentifier():
        entry = current_path / "__init__.py"
        name = current_path.name
        with _enter_path(current_module_path, name):
            if entry.exists():
                source = entry.read_text(encoding='utf-8')
                data.register_module(current_module_path, source, is_package=True)
            else:
                data.register_module(current_module_path, '', is_package=True)
            for each in current_path.iterdir():
                _traverse(current_module_path, each, data)

@wisepy2.wise
def CLI(projectdir: str, *, out: str):
    p = pathlib.Path(projectdir).absolute()
    ctx = Context({})
    _traverse([], p, ctx)
    buf = io.StringIO()
    buf.write((pathlib.Path(__file__).parent / "importer.py").read_text(encoding='utf-8'))
    buf.write('\n')
    for fullname, (is_package, source_code) in ctx.registered_sources.items():
        node = ast.Call(ast.Name("register_code_resource", ctx=ast.Load()), [ast.Constant(fullname), ast.Constant(is_package), ast.Constant(source_code)])
        ast.fix_missing_locations(node)
        buf.write(ast.unparse(node))
        buf.write('\n')
    with pathlib.Path(out).open('w', encoding='utf-8') as f:
        f.write(buf.getvalue())
