from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import date
from datetime import timedelta
from datetime import datetime
import yagmail
import time
import platform

'''
This is an example of a web crawler designed to interface with the now defunct website Amazon Moment
'''

# Amazon moment account info (password expires every 3 months, update accordingly)
username = ''
password = ''
workgroup_name = ''

# tune hyperparameters for this automated web crawler ------------------------------------

def calculate_runtime() -> int:
    # get current host computer name
    hostname = platform.node()
    # set runtime
    if hostname == 'raspberrypi':
        search_time = 80 # long background process
    else:
        search_time = 10 # short process to minimize disruptions
    return search_time

# shift blocks: in order of preference
shifts = ['09:15']
# set amount of minutes spend searching
search_time = calculate_runtime()
# set wait time for each cycle (seconds): max time threshold
wait_time = 60
# headless mode?
headless = False
# activate this weapon?
activate = True

# PERFORM NECESSARY CALCULATIONS: ----------- NO NEED TO CHANGE! ----------------

# calculate shift_date
def calculate_shift_date():
    today = date.today()
    weekday = today.weekday()
    if weekday == 0 or weekday == 1 or weekday == 2 or weekday == 6:
        shift_date = today + timedelta(days = 3)
    elif weekday == 3 or weekday == 4:
        shift_date = today + timedelta(days = 4)
    else: # if today is Saturday (weekday = 5)
        shift_date = None
    return shift_date
shift_date = calculate_shift_date()

# build shift date time strings
def build_shift_strings(shift_date, shifts: list) -> list:
    new_shifts = list()
    for shift in shifts:
        new_shifts.append(str(shift_date) + 'T' + shift)
    return new_shifts

# get shift blocks
def get_shift_blocks(shift_date, shifts):
    new_shifts = build_shift_strings(shift_date, shifts)
    # special case: if today is Sunday, mine next Sunday as well, low priority
    today = date.today()
    if today.weekday() == 6:
        next_sunday = today + timedelta(days = 7)
        additional_shifts = build_shift_strings(next_sunday, shifts)
        # merge
        new_shifts.extend(additional_shifts)
    # return
    return new_shifts

# get all shift blocks to be mined, in order of priority
shifts = get_shift_blocks(shift_date, shifts)

# determine driver_path
def find_driver_path() -> str:
    # set chromedriver path for local machine
    driver_path = '/usr/bin/chromedriver' # Ubuntu
    driver_path2 = '/mnt/c/Users/taiyi/taiyi/automata/1_twitter_bot/sign_up_bot/chromedriver.exe' # Windows 10
    driver_path3 = '/Users/taiyipan/chromedriver' # Mac OSX
    # get current host computer name
    hostname = platform.node()
    # return driver_path
    if hostname == 'Galatea':
        return driver_path2
    elif hostname == 'sol.lan':
        return driver_path3
    elif hostname == 'eternal' or hostname == 'raspberrypi':
        return driver_path
    else: # if host computer is not recognized
        driver.close()
        quit()

driver_path = find_driver_path()

# depending on table layout, change column values
def column_values(columns) -> (int, int, int):
    if len(columns) == 7:
        start_col = '4'
        end_col = '5'
        button_col = '6'
    else:
        start_col = '3'
        end_col = '4'
        button_col = '5'
    return start_col, end_col, button_col

# START NAVIGATING! ------------------------------------------------------------
try:
    # configure chromedriver options
    options = Options()
    if headless:
        options.headless = True
        options.add_argument('--log-level=3')
        options.add_argument('--window-size=1920x1080')

    # open driver
    driver = webdriver.Chrome(executable_path = driver_path, chrome_options = options)
    # maximize window -- IMPORTANT! Else certain elements won't be visible
    driver.maximize_window()
    # navigate to webpage
    driver.get('https://na.amzheimdall.com/login?clientId=WorkforceManagementGoa'
               '-prod-na&nonce=1%3AC04BKwKmW_KjIeI5oXsd5yvfqwfgWu64Q2lPa1SRcRY&'
               'redirect_uri=https%3A%2F%2Fna.amazonmoment.com%2Fgoa%2Fwfm%2Fauthenticate')
    time.sleep(5)

    # locate username field
    username_field = driver.find_element_by_id('usernameInputField')
    # enter username
    username_field.send_keys(username)
    time.sleep(1)

    # locate submit button
    submit_button = driver.find_element_by_id('submitButton')
    # click submit button
    submit_button.click()
    time.sleep(5)

    # locate password field
    password_field = driver.find_element_by_id('passwordInputField')
    # enter password
    password_field.send_keys(password)
    time.sleep(1)

    # locate submit button
    submit_button = driver.find_element_by_id('submitButton')
    # click submit button
    submit_button.click()
    time.sleep(15) # waiting time is to compensate for slow website loading due to server-side heavy traffic

    # LOGGED IN! -------------------------------------------------------------------

    # switch between "Your schedule" and "Adjust your schedule" pages in a loop
    shift_found = False # boolean flag for shift found
    loop_end = datetime.now() + timedelta(minutes = search_time) # calculate loop end time

    # locate "Adjust your schedule" link
    adjust_schedule_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/associate/div[@class="container p-0"]/nav/div/ul[@class="navbar-nav mr-auto"]/li[2]/a[@class="nav-link"]'))
    )
    # locate "Your schedule" link
    your_schedule_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/associate/div[@class="container p-0"]/nav/div/ul[@class="navbar-nav mr-auto"]/li[1]/a[@class="nav-link active"]'))
    )

    # main loop
    while (not shift_found and datetime.now() < loop_end):

        # click on "Adjust your schedule" link
        adjust_schedule_link.click()

        # wait until table is loaded (this could take a while during heavy web traffic)
        table = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/associate/div[@class="container p-0"]/adjust-schedule/'
                                                      'div/list-adjustments/div[@class="card"]/basecard/div[2]/'
                                                      'div/fieldset/div[@class="card-block"]/table[@class="table table-striped"]'))
        )

        # extract all row elements from sign up table
        try:
            rows = WebDriverWait(driver, 2).until(
                EC.presence_of_all_elements_located((By.XPATH, '/html/body/associate/div[@class="container p-0"]/adjust-schedule/'
                                                               'div/list-adjustments/div[@class="card"]/basecard/div[2]/'
                                                               'div/fieldset/div[@class="card-block"]/table[@class="table table-striped"]/tbody/tr'))
            )
        # if no elements are located (none posted yet), go back to previous page and redo the loop
        except:
            # click on "Your schedule" link
            your_schedule_link.click()
            # re-do loop
            continue

        # prior to looping through the rows, determine how many columns
        columns = WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, '/html/body/associate/div[@class="container p-0"]/adjust-schedule/'
                                                           'div/list-adjustments/div[@class="card"]/basecard/div[2]/'
                                                           'div/fieldset/div[@class="card-block"]/table[@class="table table-striped"]/thead/tr/th'))
        )
        # depending on table layout, change column values
        start_col, end_col, button_col = column_values(columns)

        # match shift time in order down the list
        for shift in shifts:
            # if rows are located, loop through all rows
            for row in rows:
                # extract workgroup element
                workgroup = row.find_element_by_xpath('.//td[1]')
                # locate my workgroup
                if (workgroup.text == workgroup_name):
                    # extract start time element
                    start_time = row.find_element_by_xpath('.//td[' + start_col + ']')
                    # locate my start time
                    if (start_time.text == shift):
                        # extract "Apply" button element
                        apply = row.find_element_by_xpath('.//td[' + button_col + ']/button[@class="btn btn-secondary"]')
                        # click apply
                        apply.click()
                        # acquire new button element: "Confirm" button
                        confirm = WebDriverWait(row, 3).until(
                            EC.presence_of_element_located((By.XPATH, './/td[' + button_col + ']/div/button[@class="btn btn-primary"]'))
                        )
                        # click confirm
                        if (activate):
                            confirm.click()
                        # wait some time
                        time.sleep(wait_time)
                        # set boolean flag to shift_found = True
                        shift_found = True
                        # remember shift time
                        shift_date_begin = shift
                        # break row loop: no need to examine the rest of rows
                        break
            # break shifts loop: no need to match other shift times
            if shift_found:
                break
        # go back to previous page only if shift not found
        if (not shift_found):
            # click on "Your schedule" link
            your_schedule_link.click()

# handle user manually closing browser
except:
    shift_found = False

# SEND EMAIL REPORT ------------------------------------------------------------
try:
    if (shift_found):
        yag = yagmail.SMTP('', '')
        contents = [
            'You have a shift signed up for {}'.format(shift_date_begin),
            'Please double check to confirm.'
        ]
        yag.send('', '{}: Sign Up Bot SUCCESS'.format(platform.node()), contents)
    else:
        yag = yagmail.SMTP('', '')
        contents = [
            'Shift sign up failed for {}'.format(shifts)
        ]
        yag.send('', '{}: Sign Up Bot FAILURE'.format(platform.node()), contents)
except:
    pass

# TERMINATE PROGRAM ------------------------------------------------------------
def terminate():
    # quit all browser windows
    driver.quit()
    # wait 10s
    time.sleep(10)
    # terminate program
    quit()
terminate()
