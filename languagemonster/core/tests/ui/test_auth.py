import random
import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from util import when_visible

URL = 'http://localhost:8000'
TEST_EMAIL = ''
TEST_PASSWD = ''

def login(driver):
    driver.get(URL)

    assert 'Language Monster' in driver.title

    login_link = driver.find_element_by_id('login')
    login_link.click()

    # login_popup = WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located((By.ID, "modal-login"))
    # )

    login_popup = when_visible(driver, ID='modal-login')

    input_email = login_popup.find_element_by_id('modal-login-email')
    input_email.send_keys(TEST_EMAIL)

    input_passwd = login_popup.find_element_by_id('modal-login-password')
    input_passwd.send_keys(TEST_PASSWD)

    btn_submit = login_popup.find_element_by_class_name('btn-submit')
    btn_submit.click()

    login_success = False

    try:
        hello_str = driver.find_element_by_class_name('hello-screen')
        login_success = True
    except NoSuchElementException as e:
        login_success = False
        print e

    return login_success

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.close()

    def test_login(self):
        self.assertTrue(login(self.driver), 'Login failed')


# 

# 
#     play_btns = driver.find_elements_by_class_name('learn')
#     random.choice(play_btns).click()
# 
#     elem = driver.find_element_by_id('btn-all')
#     elem.click()
# 
#     elem = driver.find_element_by_id('all')
# 
#     dataset_btns = elem.find_elements_by_class_name('play')
#     random.choice(dataset_btns).click()
# 
#     WebDriverWait(driver, 10).until(
#         lambda driver: driver.execute_script('return window.game.to_ask != undefined;')
#     )
# 
#     print driver.execute_script('return window.game.to_ask.length;')
# 
# 
# 

# 

if __name__ == '__main__':
    unittest.main()
