import allure
from allure_commons.types import Severity

@allure.feature("Fail tests")
def test_fail1():
    assert False

@allure.feature("Fail tests")
def test_fail2():
    assert False

@allure.feature("Fail tests")
@allure.severity(Severity.BLOCKER)
def test_fail3():
    assert False

@allure.feature("Fail tests")
@allure.severity(Severity.CRITICAL)
def test_fail4():
    assert False

@allure.feature("Fail tests")
@allure.severity(Severity.NORMAL)
def test_fail5():
    assert False

@allure.feature("Fail tests")
@allure.severity(Severity.MINOR)
def test_fail6():
    assert False

@allure.feature("Fail tests")
@allure.severity(Severity.TRIVIAL)
def test_fail7():
    assert False