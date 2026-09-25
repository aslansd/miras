import pytest


def pytest_addoption(parser):
    parser.addoption("--run-slow", action="store_true", help="run slow tests (Stan fits)")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: long-running (Stan fits); skipped unless --run-slow")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-slow"):
        return
    skip = pytest.mark.skip(reason="slow; use --run-slow")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)
