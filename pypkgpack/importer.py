from __future__ import annotations
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
import pathlib
import types
import base64
import warnings
import marshal
import hashlib
import sys
import os

BYTECODE_CACHE_DIR: pathlib.Path | None = pathlib.Path(
    os.getenv("PYBUNDLE_CACHE_PATH") or "~/.cache/pypkgpack"
).expanduser()

try:
    BYTECODE_CACHE_DIR.mkdir(mode=0o777, parents=True, exist_ok=True)
except IOError:
    # in case no permission
    BYTECODE_CACHE_DIR = None

FILE_PATH = str
IS_PACKAGE = bool
bundled_resources: dict[str, tuple[IS_PACKAGE, FILE_PATH, list[bytes]]] = {}
PYTHON_VERSION = ".".join(map(str, sys.version_info[:3]))


def register_code_resource(name: str, is_package: bool, filepath: str, *codes: bytes):
    if name in bundled_resources:
        old_is_package, old_filepath, old_codes = bundled_resources[name]
        old_codes.extend(codes)
        if filepath != old_filepath:
            warnings.warn(f"multiple '__file__' found for module {name}")
        if old_is_package is not is_package:
            warnings.warn(
                f"{name} has been asked to be {'package' if old_is_package else 'module'}"
            )
            bundled_resources[name] = is_package, old_filepath, old_codes
    else:
        bundled_resources[name] = (is_package, filepath, list(codes))


class BundledSourceLoader(Loader):
    def __init__(
        self, is_package: bool, fullname: str, filepath: str, source_codes: list[bytes]
    ):
        self.fullname = fullname
        self.source_codes = source_codes
        self.is_package = is_package
        self.filepath = filepath

    def create_module(self, spec: ModuleSpec) -> types.ModuleType | None:
        module = types.ModuleType(self.fullname)
        module.__name__ = self.fullname
        module.__loader__ = self
        module.__file__ = self.filepath
        if self.is_package:
            module.__package__ = module.__name__
            module.__path__ = []
        else:
            module.__package__ = ".".join(module.__name__.split(".")[:-1])
        return module

    def compile_module(self, source_codes: list[bytes]):
        code_objects: list[types.CodeType] = []

        def do_compile():
            for src in source_codes:
                src = base64.b64decode(src).decode("utf-8")
                code_objects.append(
                    compile(src, self.filepath, "exec")
                )

        if BYTECODE_CACHE_DIR is None:
            # NO cache dir available
            do_compile()
        else:
            md5 = 1192634
            for source_code in source_codes:
                digest = hashlib.md5(source_code).hexdigest().encode()
                md5 ^= int.from_bytes(digest, "little", signed=False)
            hexdigest = hex(md5).encode()
            cache_file = BYTECODE_CACHE_DIR / (self.fullname + "@" + PYTHON_VERSION)
            if cache_file.exists() and cache_file.is_file():
                with cache_file.open("rb") as f:
                    cache_contents = f.read()
            else:
                cache_contents = b""
            if cache_contents.startswith(hexdigest):
                code_objects.extend(marshal.loads(cache_contents[len(hexdigest) :]))
            else:
                do_compile()
                try:
                    cache_file.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
                    with cache_file.open("wb") as f:
                        f.write(hexdigest)
                        f.write(marshal.dumps(code_objects))
                except IOError:
                    pass
        return code_objects

    def exec_module(self, module: types.ModuleType):
        code_objects = self.compile_module(self.source_codes)
        for code_object in code_objects:
            exec(code_object, module.__dict__)


class BundledSourceFinder(MetaPathFinder):
    def find_spec(self, fullname: str, path, target=None):
        if fullname in bundled_resources:
            is_package, filepath, codes = bundled_resources[fullname]
            return ModuleSpec(
                fullname,
                BundledSourceLoader(
                    is_package, fullname=fullname, filepath=filepath, source_codes=codes
                ),
            )


sys.meta_path.insert(0, BundledSourceFinder())
