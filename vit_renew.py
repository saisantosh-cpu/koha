from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

USERNAME = "23BCE0312"
PASSWORD = "23BCE0312"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 20)

try:
    driver.get("https://webopac.vit.ac.in")

    wait.until(EC.visibility_of_element_located((By.ID, "userid")))

    driver.find_element(By.ID, "userid").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "#auth input[type='submit']").click()

    wait.until(EC.url_contains("opac-main.pl"))

    print("Login successful!")

    # Go to checkouts
    driver.get("https://webopac.vit.ac.in/cgi-bin/koha/opac-user.pl?op=checkouts")

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    print("\nChecking books...\n")

    today = datetime.today().date()
    renew_needed = False

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    for index, row in enumerate(rows, start=1):
        columns = row.find_elements(By.TAG_NAME, "td")

        if len(columns) > 0:
            title = columns[1].text
            due_date_text = columns[4].text.strip()  # Adjust if column index differs

            # Convert due date string to date object
            due_date = datetime.strptime(due_date_text, "%Y-%m-%d").date()

            print(f"{index}. {title}")
            print(f"   Due Date: {due_date}")

            if due_date == today:
                print("   Due today → Renewing...")
                renew_needed = True

                # Tick checkbox
                checkbox = row.find_element(By.XPATH, ".//input[@type='checkbox']")
                checkbox.click()

            else:
                print("   Not due today → No need to renew\n")

    if renew_needed:
        renew_button = driver.find_element(By.XPATH, "//button[contains(text(),'Renew selected')]")
        renew_button.click()
        print("\nRenewal submitted.")
    else:
        print("\nNo books need renewal today.")

    input("\nPress Enter to close...")

finally:
    driver.quit()