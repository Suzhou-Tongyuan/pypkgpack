import sys
from pypkgpack import __version__
from pathlib import Path
import shutil


def test_version():
    assert __version__ == "0.4.0"


def test_bundle():
    shutil.rmtree(
        Path("~/.cache/pypkgpack").expanduser().as_posix(), ignore_errors=True
    )
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
            "--dynlinkloader",
        ]
    )
    exec(
        ((Path(__file__).parent / "generated.py").absolute()).read_text(
            encoding="utf-8"
        )
    )
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
            "--dynlinkloader",
        ]
    )

    exec(
        ((Path(__file__).parent / "generated2.py").absolute()).read_text(
            encoding="utf-8"
        )
    )
    import package1
    import package1.module

    assert package1.g(10) == 20
    assert package1.module.f(10) == 11

    print(Path(package1.module.get_file()).absolute().as_posix())
    print(
        (Path(__file__).parent.parent / "pypkgpack" / "module.py").absolute().as_posix()
    )
    assert (
        Path(package1.module.get_file()).absolute().as_posix()
        == (Path(__file__).parent.parent / "pypkgpack" / "module.py")
        .absolute()
        .as_posix()
    )

    CLI(
        [
            str(
                (
                    Path(__file__).parent.parent / "packages-to-test" / "package2.py"
                ).absolute()
            ),
            "--out",
            str((Path(__file__).parent / "generated3.py").absolute()),
        ]
    )

    # abitrary path
    root = (Path(__file__).parent / "mypack" / "mypack.py").absolute()
    exec(
        ((Path(__file__).parent / "generated3.py").absolute()).read_text(
            encoding="utf-8"
        ),
        {"__file__": str(root)},
    )

    import package2

    print(root.parent.joinpath("package2.py").as_posix())
    print(Path(package2.get_file()).absolute().as_posix())
    assert (
        Path(package2.get_file()).absolute().as_posix()
        == root.parent.joinpath("package2.py").as_posix()
    )
