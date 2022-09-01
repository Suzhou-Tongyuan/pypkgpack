from pybundle import importer
import base64

def test_manual():
    importer.register_code_resource("fff", True, base64.b64encode(b"a = 1"))
    importer.register_code_resource("fff.ggg", False, base64.b64encode(b"from . import a"))
    importer.register_code_resource("fff.b", False, base64.b64encode(b"c = 1"))
    importer.register_code_resource("fff.cccc", True, base64.b64encode(b""))
    importer.register_code_resource("fff.cccc.dddd", False, base64.b64encode(b"z = 2"))

    import fff.ggg as ggg
    print(ggg.a)

    import fff
    print(fff.a)

    from fff.cccc.dddd import z
    print(z)
