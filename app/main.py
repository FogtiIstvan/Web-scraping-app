from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException


def get_match_results(URL, now = False, team = None):
    # Set up the web driver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Remote(
        command_executor='http://host.docker.internal:4444/wd/hub',
        options=options
    )

    driver.get(URL)

    # Wait for the page to fully load
    driver.implicitly_wait(10)

    # Dismiss the cookie banner if it exists
    try:
        print("Checking for cookie banner")
        cookie_banner_accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
        print("Cookie banner found")
        print(cookie_banner_accept_button.text)
        cookie_banner_accept_button.click()
        print("Cookie banenr clicked")
        driver.implicitly_wait(1000)
    except:
        print("No cookie banner found")
        pass

    loading = 3
    import time

    print("waiting")
    time.sleep(3)
    print("end of waiting")
    # Load more matches
    if now == False:
        while loading > 0:
            try:
                # Find the "Show more matches" button
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "event__more"))
                )
                # Click the button
                driver.execute_script("arguments[0].click();", show_more_button)
                time.sleep(3)
                loading -= 1
                # Wait for the page to fully load
                driver.implicitly_wait(1000)
            except TimeoutException:
                print("Timed out waiting for 'Show more matches' button")
            except StaleElementReferenceException:
                print("Stale element reference: re-finding 'Show more matches' button")
                continue
            except NoSuchElementException:
                print("No such element: 'Show more matches' button not found")
                break
            except Exception as e:
                print("Error occurred while loading more matches:", e)
                break

    # Extract the HTML content
    html = driver.page_source

    # Parse the HTML content
    soup = BeautifulSoup(html, "html.parser")
    # Find the match results
    match_results = soup.find_all(class_="event__match")
    print(len(match_results))
    matches = []
    # Print the match results
    for match in match_results:
        #print(match.prettify())
        home = match.find(class_="event__participant--home").text.strip()
        away = match.find(class_="event__participant--away").text.strip()
        home_goals = match.find(class_="event__score--home").text.strip()
        away_goals = match.find(class_="event__score--away").text.strip()
        match_id = match.get('id')
        match_id = match_id[4:]
        #matches.append([home, home_goals, away_goals, away])
        if team is not None:
            if home.strip().lower() == team.strip().lower() or away.strip().lower() == team.strip().lower():
                matches.append({
                    "id" : match_id,
                    "homeside" : home,
                    "awayside" : away,
                    "homegoals" : home_goals,
                    "awaygoals" : away_goals
                })
        else:
            matches.append({
                "id" : match_id,
                "homeside" : home,
                "awayside" : away,
                "homegoals" : home_goals,
                "awaygoals" : away_goals
            })
        
        #print("=====================================")

    # Close the web driver
    driver.close()
    driver.quit()

    return matches


def generate_urls(leagues, seasons):
    urls = []
    for league in leagues:
        for season in seasons:
            if season == "now":
                urls.append([f"https://www.flashscore.com/football/{league}/results/", True])
            else:
                urls.append([f"https://www.flashscore.com/football/{league}-{season}/results/", False])
    return urls


def load_matches(season, league, team = None):
    URL = "https://www.flashscore.com/football/england/premier-league/results/"

    print("season: " + str(season))
    print("league: " + str(league))

    #seasons = ["now", "2022-2023", "2021-2022"]
    #leagues = ["england/premier-league", "spain/laliga"] #, "germany/bundesliga", "italy/serie-a", "france/ligue-1"]

    #seasons = ["now"]
    #leagues = ["england/premier-league"]

    urls = generate_urls(league, season)
    print(urls)

    results = []
    for url in urls:
        r = get_match_results(url[0], url[1], team)
        if len(r) > 0:
            results.append(r)
        else:
            print(f"No results for {url}")

    for result in results:
        print(result)

    return results

