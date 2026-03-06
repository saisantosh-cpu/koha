import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Get credentials from GitHub Secrets
USERNAME = os.environ["VIT_USER"]
PASSWORD = os.environ["VIT_PASS"]

# Chrome options for GitHub Actions
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# Start driver
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 20)

try:
    print("Opening VIT Library...")

    driver.get("https://webopac.vit.ac.in")

    # Wait for login page
    wait.until(EC.visibility_of_element_located((By.ID, "userid")))

    # Login
    driver.find_element(By.ID, "userid").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "#auth input[type='submit']").click()

    # Wait for login success
    wait.until(EC.url_contains("opac-main.pl"))
    print("Login successful!")

    # Open checkouts page
    driver.get("https://webopac.vit.ac.in/cgi-bin/koha/opac-user.pl?op=checkouts")

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    today = datetime.today().date()
    renew_needed = False

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    print("\nChecking borrowed books...\n")

    book_index = 1

    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")

        if len(columns) < 5:
            continue

        title = columns[1].text.strip()
        due_date_text = columns[4].text.strip()

        try:
            due_date = datetime.strptime(due_date_text, "%Y-%m-%d").date()
        except:
            continue

        print(f"{book_index}. {title}")
        print(f"   Due Date: {due_date}")

        if due_date == today:
            print("   Due today → selecting for renewal")
            renew_needed = True

            try:
                checkbox = row.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                driver.execute_script("arguments[0].click();", checkbox)
                print("   Checkbox selected")
            except Exception as e:
                print("   Failed to select checkbox:", e)

        book_index += 1

    # Renew selected books
    if renew_needed:
        try:
            print("\nAttempting renewal...")

            renew_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[contains(@value,'Renew')] | //button[contains(text(),'Renew')]")
                )
            )

            driver.execute_script("arguments[0].click();", renew_button)

            # Wait for confirmation message
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert"))
            )

            print("Renewal completed successfully!")

        except Exception as e:
            print("Renewal failed:", e)

    else:
        print("\nNo books need renewal today.")

finally:
    print("\nClosing browser...")
    driver.quit()
