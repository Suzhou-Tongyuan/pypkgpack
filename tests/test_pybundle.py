import sys
from pypkgpack import __version__
from pathlib import Path
import shutil

def test_version():
    assert __version__ == "0.1.0"


def test_bundle():
    shutil.rmtree(Path("~/.cache/pypkgpack").expanduser().as_posix(), ignore_errors=True)
    from pypkgpack.bundle import CLI

    CLI(
        [
            str(
                (
                    Path(__file__).parent.parent / "packages-to-test" / "package1"
                ).absolute()
            ),
            "--out",
            str((Path(__file__).parent / "generated.py").absolute()),
            '--dynlinkloader'
        ]
    )
    exec(((Path(__file__).parent / "generated.py").absolute()).read_text(encoding='utf-8'))
    import package1
    import package1.module
    assert package1.g(10) == 20
    assert package1.module.f(10) == 11

    # reload using cache to increment coverage
    del sys.modules["package1.module"]
    del sys.modules["package1"]
    import package1
    import package1.module
    assert package1.g(10) == 20
    assert package1.module.f(10) == 11

    # regenerate and reload to increment coverage
    del sys.modules["package1.module"]
    del sys.modules["package1"]

    CLI(
        [
            str(
                (
                    Path(__file__).parent.parent / "packages-to-test" / "package1"
                ).absolute()
            ),
            "--out",
            str((Path(__file__).parent / "generated2.py").absolute()),
            '--dynlinkloader'
        ]
    )

    exec(((Path(__file__).parent / "generated2.py").absolute()).read_text(encoding='utf-8'))
    import package1
    import package1.module

    assert package1.g(10) == 20
    assert package1.module.f(10) == 11
