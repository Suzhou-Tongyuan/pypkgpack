## PyBundle

Bundling a Python package into a single Python file.

Usage:

```shell
> pybundle /path/to/mypackage --out bundled_package.py

> python

python> import bundled_package
python> from mypackage.mymodule import myfunction
python> print(myfunction())
```

Features:

- [x] bundling a Python package into a single Python file.
- [x] support caching bytecode compilation and cache invalidation.
- [ ] support bundling binaries and assets.
- [x] respect Python's import semantics.
- [x] bundled modules need no extra dependencies.
