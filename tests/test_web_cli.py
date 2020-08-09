import pytest

from aiohttp import web


def test_entry_func_empty(mocker) -> None:
    error = mocker.patch("aiohttp.web.ArgumentParser.error",
                         side_effect=SystemExit)
    with pytest.raises(SystemExit):
        argv = [""]

        web.main(argv)

    error.assert_called_with("'entry-func' not in 'module:function' syntax")


def test_entry_func_only_module(mocker) -> None:
    error = mocker.patch("aiohttp.web.ArgumentParser.error",
                         side_effect=SystemExit)

    with pytest.raises(SystemExit):
        argv = ["test"]
        web.main(argv)

    error.assert_called_with("'entry-func' not in 'module:function' syntax")


def test_entry_func_only_function(mocker) -> None:
    error = mocker.patch("aiohttp.web.ArgumentParser.error",
                         side_effect=SystemExit)

    with pytest.raises(SystemExit):
        argv = [":test"]
        web.main(argv)

    error.assert_called_with("'entry-func' not in 'module:function' syntax")


def test_entry_func_only_separator(mocker) -> None:
    error = mocker.patch("aiohttp.web.ArgumentParser.error",
                         side_effect=SystemExit)

    with pytest.raises(SystemExit):
        argv = [":"]
        web.main(argv)

    error.assert_called_with("'entry-func' not in 'module:function' syntax")


def test_entry_func_relative_module(mocker) -> None:
    error = mocker.patch("aiohttp.web.ArgumentParser.error",
                         side_effect=SystemExit)
    with pytest.raises(SystemExit):
        argv = [".a.b:c"]

        web.main(argv)

    error.assert_called_with("relative module names not supported")


def test_entry_func_non_existent_module(mocker) -> None:
    mocker.patch("aiohttp.web.import_module",
                 side_effect=ImportError("Test Error"))
    error = mocker.patch("aiohttp.web.ArgumentParser.error",
                         side_effect=SystemExit)

    with pytest.raises(SystemExit):
        argv = ["alpha.beta:func"]

        web.main(argv)

    error.assert_called_with("unable to import alpha.beta: Test Error")


def test_entry_func_non_existent_attribute(mocker) -> None:
    import_module = mocker.patch("aiohttp.web.import_module")
    error = mocker.patch("aiohttp.web.ArgumentParser.error",
                         side_effect=SystemExit)
    module = import_module("alpha.beta")
    del module.func

    with pytest.raises(SystemExit):
        argv = ["alpha.beta:func"]
        web.main(argv)

    error.assert_called_with("module %r has no attribute %r" %
                             ("alpha.beta", "func"))


def test_path_when_unsupported(mocker, monkeypatch) -> None:
    mocker.patch("aiohttp.web.import_module")
    monkeypatch.delattr("socket.AF_UNIX", raising=False)

    error = mocker.patch("aiohttp.web.ArgumentParser.error",
                         side_effect=SystemExit)
    with pytest.raises(SystemExit):
        argv = "--path=test_path.sock alpha.beta:func".split()
        web.main(argv)

    error.assert_called_with("file system paths not supported by your"
                             " operating environment")


def test_entry_func_call(mocker) -> None:
    mocker.patch("aiohttp.web.run_app")
    import_module = mocker.patch("aiohttp.web.import_module")
    module = import_module("alpha.beta")

    with pytest.raises(SystemExit):
        argv = ("-H testhost -P 6666 --extra-optional-eins alpha.beta:func "
                "--extra-optional-zwei extra positional args").split()
        web.main(argv)

    module.func.assert_called_with(
        ("--extra-optional-eins --extra-optional-zwei extra positional "
         "args").split())


def test_running_application(mocker) -> None:
    run_app = mocker.patch("aiohttp.web.run_app")
    import_module = mocker.patch("aiohttp.web.import_module")
    exit = mocker.patch("aiohttp.web.ArgumentParser.exit",
                        side_effect=SystemExit)
    module = import_module("alpha.beta")
    app = module.func()

    with pytest.raises(SystemExit):
        argv = ("-H testhost -P 6666 --extra-optional-eins alpha.beta:func "
                "--extra-optional-zwei extra positional args").split()
        web.main(argv)

    run_app.assert_called_with(app, host="testhost", port=6666, path=None)
    exit.assert_called_with(message="Stopped\n")
