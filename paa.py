from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open Google and perform the search
query = "what are good hotels morocco?"
driver.get("https://www.google.com/?hl=en")
time.sleep(2)

# Locate the search box, type the query, and hit 'Enter'
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys(query)
search_box.send_keys(Keys.RETURN)
time.sleep(3)

# Initialize storage for questions and answers
questions_and_answers = []
max_questions = 200  # Limit to avoid processing too many questions
click_delay = 2  # Time to wait after clicking a question

# Process the PAA questions dynamically
for i in range(max_questions):
    try:
        # Re-locate all PAA question elements each time to handle dynamic DOM changes
        paa_questions = driver.find_elements(By.XPATH, "//div[@jsname='yEVEwb']") 

        # Break if we've processed all available questions
        if i >= len(paa_questions):
            print("No more questions available.")
            break

        # Scroll to the current question and ensure it is clickable
        paa_question = paa_questions[i]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", paa_question)

        # Check visibility and use ActionChains for reliable clicking
        if paa_question.is_displayed() and paa_question.is_enabled():
            ActionChains(driver).move_to_element(paa_question).click().perform()
            print(f"Processing question {i + 1}: {paa_question.text.strip()}")
            time.sleep(click_delay)
        else:
            print(f"Question {i + 1} not clickable or visible.")
            continue

        # Extract the expanded content after clicking
        expanded_answer = None
        try:
            # Look for the expanded answer container
            parent_div = paa_question.find_element(By.XPATH, "..").find_element(By.XPATH, "..")
            expanded_answer = parent_div.find_element(By.XPATH, ".//div[contains(@class, 'wQiwMc related-question-pair')]").text.strip()
        except Exception as e:
            print(f"Could not locate expanded answer for question {i + 1}: {e}")

        # If no answer is found, skip to the next question
        if not expanded_answer:
            print(f"No answer found for question {i + 1}.")
            continue

        # Store the question and answer
        questions_and_answers.append({
            "question": paa_question.text.strip(),
            "answer": expanded_answer
        })
    except Exception as e:
        print(f"Error processing question {i + 1}: {e}")
        continue


# Close the browser
driver.quit()
