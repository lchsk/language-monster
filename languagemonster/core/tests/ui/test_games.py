import random
import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from test_auth import login
from util import (
    when_visible,
    when_condition,
    reset_driver,
)

TEST_TO_ASK_CNT = 4

# Number of times we'll try to load a random game
RUN_RANDOM_GAMES_TEST = 10

def load_random_game(driver):
    btns_play = driver.find_elements_by_class_name('learn')
    # btns_play = when_visible(driver, CLASS_NAME='learn')
    when_condition(driver, lambda _: len(btns_play) > 0)
    random.choice(btns_play).click()

    # tab_all = driver.find_element_by_id('btn-all')
    tab_all = when_visible(driver, ID='btn-all')
    tab_all.click()

    # tab_content = driver.find_element_by_id('all')
    tab_content = when_visible(driver, ID='all')

    btns_dataset = tab_content.find_elements_by_class_name('play')
    when_condition(driver, lambda _: len(btns_dataset) > 0)
    # btns_dataset = when_visible(driver, CLASS_NAME='play')
    random.choice(btns_dataset).click()

    when_condition(
        driver,
        lambda driver: driver.execute_script(
            'return window.game.to_ask != undefined;'
        )
    )

    # WebDriverWait(driver, 10).until(
    #     lambda driver: driver.execute_script(
    #         'return window.game.to_ask != undefined;'
    #     )
    # )

    return driver.execute_script(
        'return window.game.to_ask.length;'
    )

class TestGames(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.close()

    def test_random_game_loaded(self):
        self.assertTrue(login(self.driver), 'Login failed')

        self.assertEqual(load_random_game(self.driver), TEST_TO_ASK_CNT)

    def test_random_game_loaded_many(self):
        driver = None

        for i in xrange(RUN_RANDOM_GAMES_TEST):
            driver = reset_driver(driver)

            print '{0} of {1}'.format(i + 1, RUN_RANDOM_GAMES_TEST)

            self.assertTrue(login(driver), 'Login failed')
            self.assertEqual(load_random_game(driver), TEST_TO_ASK_CNT)

if __name__ == '__main__':
    unittest.main()