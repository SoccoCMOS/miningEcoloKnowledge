from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
option = webdriver.ChromeOptions()
option.add_argument(" — incognito")
timeout = 20
browser = webdriver.Chrome()
browser.get("https://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&search_mode=GeneralSearch")
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/h1/div/img")))
    inputElement = browser.find_element_by_id("value(input1)")
    inputElement.send_keys("diet collembola")
    inputElement.send_keys(Keys.ENTER)
    browser.find_element_by_id("RECORD_2")
    ab=browser.find_element_by_id("ViewAbstract2_text")
    ab.click()
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ViewAbstract_TextArea2']")))

    abb=browser.find_element_by_id("ViewAbstract_TextArea2")
    text=abb.get_attribute("innerText")
    page= browser.find_element_by_xpath("//*[@id='RECORD_2']/div[3]/div[1]/div/a")
    print(text)
    page.click()
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='records_form']/div/div/div/div[1]/div/div[3]/p[3]/value")))
    keywords=browser.find_element_by_xpath("//*[@id='records_form']/div/div/div/div[1]/div/div[5]")
    keywordsList= keywords.find_elements_by_xpath(".//*")
    keywo=[]
    for t in keywordsList:
        y= t.find_elements_by_xpath("*")
        for z in y:
           keywo.append(z.get_attribute('innerText'))
    print("KEYWORDS :"+str(keywo))
    doi= browser.find_element_by_xpath("//*[@id='records_form']/div/div/div/div[1]/div/div[3]/p[3]/value")
    doi=doi.get_attribute('innerText')
    print(doi)
    browser.close()


except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()
