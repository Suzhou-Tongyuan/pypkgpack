## PyPkgPack

[![CI](https://github.com/Suzhou-Tongyuan/pypkgpack/actions/workflows/ci.yml/badge.svg)](https://github.com/Suzhou-Tongyuan/pypkgpack/actions/workflows/ci.yml)
[![versions](https://img.shields.io/pypi/pyversions/pypkgpack.svg)](https://pypi.org/project/pypkgpack/#history)
[![pypi](https://img.shields.io/pypi/v/pypkgpack.svg)](https://pypi.org/project/pypkgpack/)
[![License](https://img.shields.io/badge/License-BSD_2--Clause-green.svg)](https://github.com/Suzhou-Tongyuan/pypkgpack/blob/main/LICENSE)

Bundling multiple Python packages into a single Python file.

Usage:

```shell
> pypkgpack /path/to/mypackage1 /path/to/mypackage2 --out bundled_package.py

> python

python> import bundled_package
python> from mypackage.mymodule import myfunction
python> print(myfunction())
```

Features:

- [x] bundling a Python package into a single Python file
- [x] caching bytecode compilation and cache invalidation
- [x] fixing the missing `__init__.py`
- [x] allow multiple source code implementations for the same module
- [x] respect Python's import semantics
- [x] bundled modules need no extra dependencies
- [ ] support bundling binaries and assets
- [ ] allow lazy imports
