from pypkgpack import __version__
from pathlib import Path


def test_version():
    assert __version__ == "0.1.0"


def test_bundle():
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
        ]
    )
    import tests.generated
    import package1
    import package1.module

    assert package1.g(10) == 20
    assert package1.module.f(10) == 11
