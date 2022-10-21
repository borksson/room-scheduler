import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']


options = webdriver.ChromeOptions()
#options.add_argument('headless')

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)