import allure
from selene import have, command
from selene.support.shared import browser
from selene.support import by

@allure.feature("Форма регистрации")
@allure.story("Успешное заполнение всех полей")
@allure.label("owner", "D Chudnov")
@allure.link("https://demoqa.com", name="Testing")
def test_form_allure_dynamic_steps(setup_browser):
    with allure.step("Open registrations form"):
        browser.open("https://demoqa.com/automation-practice-form")
        browser.element(".practice-form-wrapper").should(have.text("Student Registration Form"))

    with allure.step("Fill registration form data"):
        browser.element("#firstName").type("Frodo")
        browser.element("#lastName").type("Baggins")
        browser.element("#userEmail").type("bagginsFr@shire.com")
        browser.element("#gender-radio-1").click()
        browser.element("#userNumber").type("1231231231")

        browser.element("#dateOfBirthInput").click()
        browser.element('.react-datepicker__month-select').all('option') \
            .element_by(have.exact_text("July")).click()
        browser.element('.react-datepicker__year-select').all('option') \
            .element_by(have.exact_text(str(2000))).click()
        browser.element(".react-datepicker__day--030:not(.react-datepicker__day--outside-month)").click()

        browser.element("#subjectsInput").send_keys("Maths")
        browser.element("#subjectsInput").press_enter()
        browser.element("#hobbiesWrapper").element(by.text("Sports")).click()

        browser.element("#currentAddress").set_value("Some street 1")
        browser.element("#state").click()
        browser.element("#stateCity-wrapper").element(by.text("NCR")).click()
        browser.element("#city").click()
        browser.element("#stateCity-wrapper").element(by.text("Delhi")).click()
        browser.element('#submit').perform(command.js.scroll_into_view)
        browser.element('#submit').perform(command.js.click)


    with allure.step("Check form results"):
        browser.element("#example-modal-sizes-title-lg").should(have.text("Thanks for submitting the form"))
        browser.element('.table').all('td').even.should(have.exact_texts(
            'Frodo Baggins',
            'bagginsFr@shire.com',
            'Male',
            '1231231231',
            '30 July,2000',
            'Maths',
            'Sports',
            '',
            'Some street 1',
            'NCR Delhi'
        ))

@allure.feature("Форма регистрации")
@allure.story("Динамические шаги")
@allure.label("owner", "D Chudnov")
@allure.link("https://demoqa.com", name="Testing")
def test_form_allure_dynamic_steps_failed(setup_browser):
    with allure.step("Open registrations form"):
        browser.open("https://demoqa.com/automation-practice-form")
        browser.element(".practice-form-wrapper").should(have.text("Student Registration Form"))

    with allure.step("Fill registration form data"):
        browser.element("#firstName").type("Frodo")
        browser.element("#lastName").type("Baggins")
        browser.element("#userEmail").type("bagginsFr@shire.com")
        browser.element("#gender-radio-1").click()
        browser.element("#userNumber").type("1231231231")

        browser.element("#dateOfBirthInput").click()
        browser.element('.react-datepicker__month-select').all('option') \
            .element_by(have.exact_text("July")).click()
        browser.element('.react-datepicker__year-select').all('option') \
            .element_by(have.exact_text(str(2000))).click()
        browser.element(".react-datepicker__day--030:not(.react-datepicker__day--outside-month)").click()

        browser.element("#subjectsInput").send_keys("Maths")
        browser.element("#subjectsInput").press_enter()
        browser.element("#hobbiesWrapper").element(by.text("Sports")).click()

        browser.element("#currentAddress").set_value("Some street 1")
        browser.element("#state").click()
        browser.element("#stateCity-wrapper").element(by.text("NCR")).click()
        browser.element("#city").click()
        browser.element("#stateCity-wrapper").element(by.text("Delhi")).click()
        browser.element('#submit').perform(command.js.scroll_into_view)
        browser.element('#submit').perform(command.js.click)


    with allure.step("Check form results"):
        browser.element("#example-modal-sizes-title-lg").should(have.text("Thanks for submitting the form"))
        browser.element('.table').all('td').even.should(have.exact_texts(
            'Bilbo Baggins',
            'bagginsBb@shire.com',
            'Male',
            '321321321321',
            '12 June,1950',
            'Maths',
            'Sports',
            '',
            'Some street 4',
            'NCR Delhi'
        ))

@allure.link("https://demoqa.com", name="Testing")
@allure.feature("Форма регистрации")
@allure.story("Разные пользователи в ассерте и тесте")
@allure.label("owner", "Чуднов")
def test_form_allure_decorator_steps(setup_browser):
    open_registrations_form()
    fill_registration_form_data()
    check_results()

@allure.step("Open registrations form")
def open_registrations_form():
    browser.open("https://demoqa.com/automation-practice-form")
    browser.element(".practice-form-wrapper").should(have.text("Student Registration Form"))

@allure.step("Fill registration form data")
def fill_registration_form_data():
    browser.element("#firstName").type("Frodo")
    browser.element("#lastName").type("Baggins")
    browser.element("#userEmail").type("bagginsFr@shire.com")
    browser.element("#gender-radio-1").click()
    browser.element("#userNumber").type("1231231231")

    browser.element("#dateOfBirthInput").click()
    browser.element('.react-datepicker__month-select').all('option') \
            .element_by(have.exact_text("July")).click()
    browser.element('.react-datepicker__year-select').all('option') \
            .element_by(have.exact_text(str(2000))).click()
    browser.element(".react-datepicker__day--030:not(.react-datepicker__day--outside-month)").click()

    browser.element("#subjectsInput").send_keys("Maths")
    browser.element("#subjectsInput").press_enter()
    browser.element("#hobbiesWrapper").element(by.text("Sports")).click()

    browser.element("#currentAddress").set_value("Some street 1")
    browser.element("#state").click()
    browser.element("#stateCity-wrapper").element(by.text("NCR")).click()
    browser.element("#city").click()
    browser.element("#stateCity-wrapper").element(by.text("Delhi")).click()
    browser.element('#submit').perform(command.js.scroll_into_view)
    browser.element('#submit').perform(command.js.click)

@allure.step("Check results")
def check_results():
    browser.element("#example-modal-sizes-title-lg").should(have.text("Thanks for submitting the form"))
    browser.element('.table').all('td').even.should(have.exact_texts(
            'Frodo Baggins',
            'bagginsFr@shire.com',
            'Male',
            '1231231231',
            '30 July,2000',
            'Maths',
            'Sports',
            '',
            'Some street 1',
            'NCR Delhi'
    ))