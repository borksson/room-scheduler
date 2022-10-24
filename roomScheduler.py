from multiprocessing.connection import wait
import os
import time
from datetime import date, datetime
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

with open('appData.json', 'r') as f:
    appData = json.load(f)

options = webdriver.ChromeOptions()
#options.add_argument('headless')

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

print("Navigating to homepage...")
driver.get('https://groupstudy.lib.byu.edu/')

loginButton = driver.find_element(By.CSS_SELECTOR, appData['elements']['login']['by']['css'])
loginButton.click()
username = driver.find_element(By.CSS_SELECTOR, appData['elements']['username']['by']['css'])
username.send_keys(USERNAME)
password = driver.find_element(By.CSS_SELECTOR, appData['elements']['password']['by']['css'])
password.send_keys(PASSWORD)
submitButton = driver.find_element(By.CSS_SELECTOR, appData['elements']['submit']['by']['css'])
submitButton.click()
input("Press enter after duo...")
print("Logged in!")

dateElement = driver.find_element(By.XPATH, appData['elements']['date']['by']['xpath'])
dateSelect = Select(dateElement)
floorSelect = Select(driver.find_element(By.XPATH, appData['elements']['subarea']['by']['xpath']))
numOptions = len(dateSelect.options)

reserveRooms = []

appData['currentSchedule'] = {i:x for (i, x) in appData['currentSchedule'].items() if datetime.strptime(x['roomDetails']['date']+' 2022', '%A, %B %d %Y')  >= datetime.now()}

print(appData['currentSchedule'])
input("Press enter to continue...")

optimalSchedule = appData['optimalSchedule']
for key in optimalSchedule.keys():
    if(key in appData['currentSchedule'].keys()):
        print(f"Skipping {key} because it is already been reserved with the following rooms: {appData['currentSchedule'][key]['room']} at {appData['currentSchedule'][key]['roomDetails']['start']}")
        continue
    i = [i for i, x in enumerate(dateSelect.options) if key in x.text.lower()][0]
    dateSelect.select_by_index(i)
    date = dateSelect.options[i].text
    floorIndex = [i for i, x in enumerate(floorSelect.options) if str(optimalSchedule[key]['floor']) in x.text.lower()][0]
    floorSelect.select_by_index(floorIndex)
    floor = floorSelect.options[floorIndex].text
    print("Getting rooms for " + date + ", " + floor + "...")
    go = driver.find_element(By.XPATH, appData['elements']['go']['by']['xpath'])
    go.click()
    grid = driver.find_element(By.XPATH, appData['elements']['grid']['by']['xpath'])
    rooms = grid.find_elements(By.CSS_SELECTOR, appData['elements']['rooms']['by']['css'])[0]
    rooms = rooms.find_elements(By.XPATH, "./*")
    optimalTime = optimalSchedule[key]['start']
    times = grid.find_elements(By.XPATH, appData['elements']['times']['by']['xpath'])
    timeRow = [timeRow for timeRow in times if optimalTime in timeRow.get_attribute('innerHTML')]
    if len(timeRow) > 0:
        timeRowItem = timeRow[0]
        timeRow = timeRowItem.find_elements(By.XPATH, "./*")
        # TODO: add preferred room logic
        # TODO: Add logic if preferred room, floor, time is not available
        maxTime = {'timeAvailable': 0, 'room': None, 'roomDetails': None}
        for j in range(1, len(timeRow)):
            if 'Reserved' not in timeRow[j].get_attribute('innerHTML'):
                roomData = rooms[j].text.split('\n')
                roomNumber = roomData[0]
                numberOfSeats = int(roomData[1].split(' ')[0])
                if numberOfSeats >= optimalSchedule[key]['numSeats']:
                    timeAvailable = 0.5
                    index = times.index(timeRowItem)+1                        
                    while index < len(times):
                        currRow = times[index].find_elements(By.XPATH, "./*")
                        if 'Reserved' not in currRow[j].get_attribute('innerHTML'):
                            index += 1
                            timeAvailable += 0.5
                        else:
                            break
                    roomDetails = {'roomNumber': roomNumber, 'numberOfSeats': numberOfSeats, 'date': date, 'floor': floor, 'day': key, 'start': optimalTime}
                    if timeAvailable > maxTime['timeAvailable']:
                        maxTime['timeAvailable'] = timeAvailable
                        maxTime['room'] = roomNumber
                        maxTime['link'] = timeRow[j].find_element(By.XPATH, "./*").get_attribute('href')
                        maxTime['roomDetails'] = roomDetails
        print("Room " + maxTime['roomDetails']['roomNumber'] + " is available at " + optimalTime + " on " + date + " with " + str(maxTime['roomDetails']['numberOfSeats']) + " seats for " + str(timeAvailable) + " hours.")
        reserveRooms.append(maxTime)
    else: print("No time row for found.")

    if i < (numOptions - 1):
        WebDriverWait(driver, 10).until(EC.staleness_of(dateElement))
        dateElement = driver.find_element(By.XPATH, appData['elements']['date']['by']['xpath'])
        dateSelect = Select(dateElement)        
        floorSelect = Select(driver.find_element(By.XPATH, appData['elements']['subarea']['by']['xpath']))
if(len(reserveRooms) > 0):print("Reserving rooms...")
for room in reserveRooms:
    driver.get(room['link'])
    # Check is duration is 2 hours
    duration = Select(driver.find_element(By.CSS_SELECTOR, appData['elements']['duration']['by']['css']))
    numOptions = len(duration.options)
    duration.select_by_index(numOptions - 1)
    description = driver.find_element(By.CSS_SELECTOR, appData['elements']['description']['by']['css'])
    # TODO: Add description
    description.send_keys("Reserved for group study")
    reserveButton = driver.find_element(By.CSS_SELECTOR, appData['elements']['reserve']['by']['css'])
    input("FINISH CAPTCHA, then press Enter to continue...")
    reserveButton.click()
    appData['currentSchedule'][room['roomDetails']['day']] = room
    print("Reserved room!")

input("Press Enter to terminate...")
with open('appData.json', 'w') as outfile:
    json.dump(appData, outfile, indent=4)
driver.close()