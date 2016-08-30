# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Seconds
# WAITING_TIME = 10

# def when_visible(driver, ID=None, CLASS_NAME=None):
#     condition = None

#     if ID is not None:
#         condition = By.ID, ID
#     elif CLASS_NAME is not None:
#         condition = By.CLASS_NAME, CLASS_NAME

#     if condition is not None:
#         return WebDriverWait(driver, WAITING_TIME).until(
#             EC.visibility_of_element_located(condition)
#         )

# def when_condition(driver, condition):
#     return WebDriverWait(driver, WAITING_TIME).until(
#         condition
#     )

# def reset_driver(driver):
#     if driver:
#         driver.close()

#     return webdriver.Firefox()
