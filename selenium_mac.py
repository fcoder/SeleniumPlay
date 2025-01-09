# This file is for running Selenium with Chrome on a MacBook Pro
# See cmds for some requirements before this program can run
from selenium import webdriver
from selenium.webdriver.common.by      import By
from selenium.webdriver.support.ui     import WebDriverWait
from selenium.webdriver.support        import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from get_server_urls import get_urls_from_server, videos
from get_yt_duration import get_video_duration
import time, random, sys

# Get and check command line arguments
try:
    server      = sys.argv[1]
    num_to_play = int(sys.argv[2])
except ValueError:
    print("The arguments must be integers.")
    sys.exit(1)

if num_to_play < 1:
    print("The last command line argument must be a positive integer")
    sys.exit(1)

if len(sys.argv) != 3 or not (sys.argv[1] == 'linode' or sys.argv[1] == 'local'):
    print("Usage: python selenium_mac.py linode|local <num>, num is # of videos to play")
    sys.exit(1)

# Get the URLs of all songs and bonuses from chinesesong server. Save URLs in video[...]
if get_urls_from_server("All", server) == -1:   # All means all songs
    print("Error: abort")
    sys.exit(1)  # Abort!
if get_urls_from_server("Bonus", server) == -1: # Bonus to get data for all bonuses
    print("Error: abort")
    sys.exit(1)

num_videos = len(videos)  # Total number of songs and bonuses
num_min    = min(num_to_play, num_videos)
random.shuffle(videos)     # Shuffle the items inside array videos
print(f"Got {num_videos} songs and bonus from server, playing the first {num_min}...")

# Configure Chrome driver. For example: Start Chrome with a maximized window
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver_class = webdriver.Chrome     # MacBook can use Chrome or Safari, but Chrome is more stable
driver_path  = "/Users/Yuming/MyInstall/chromedriver-mac-arm64/chromedriver"
service      = Service(executable_path=driver_path)
driver       = driver_class(service=service)

print("Running Selenium with Chrome on a MacBook...")

try:  # Any exception during the loop will jump directly to the finally block.
    for i, video in enumerate(videos):
        if i >= num_min:
            break

        try:
            # Step 1: Get a page for a song/bonus from www.chinesesong.net. which contains an embedded YouTube
            driver.get(video['url'])

            # Step 2: Set screen size to 90% using JavaScript, so it is easer to be moved around
            screen_width  = driver.execute_script("return window.screen.availWidth;")
            screen_height = driver.execute_script("return window.screen.availHeight;")
            width  = int(screen_width  * 0.9)     # Calculate 90% dimensions
            height = int(screen_height * 0.9)
            driver.set_window_size(width, height) # Resize the window to 90% of the screen size

            # Step 3: Ensure the YouTube iframe is fully in view them switch to it
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "youtube-iframe"))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", iframe)
            driver.switch_to.frame(iframe)        # Switch to the YouTube iframe

            # Step 4: Ensure the play button is clickable and fully in view
            play_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-large-play-button"))
            )

            # Scroll the play button into view (Not necessary because now we always render iframe on top)
            # driver.execute_script("""
            #    var rect = arguments[0].getBoundingClientRect();
            #    var isVisible = (rect.top >= 0 && rect.left >= 0
            #        && rect.bottom <= (window.innerHeight || document.documentElement.clientHeight)
            #        && rect.right <= (window.innerWidth || document.documentElement.clientWidth));
            #    if (!isVisible) {
            #        arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
            #    }
            # """, play_button)

            # Add a brief pause after scrolling
            time.sleep(2)

            # Step 5: Call get_yt_video_duration(video['url']) to get the duration of the YouTube video from YouTube website
            duration = get_video_duration(video['url']) + 3
            minutes, seconds = divmod(int(duration), 60)
            formatted_time = f"{minutes}:{seconds:02}"  # Format as "minutes:seconds"
            # Print video title and duration, reserve 3 spaces for aligning the numbers in 1~999
            print(f"{i+1:3}: {video['title']} {formatted_time}")

            #! Step 6: Click the play button at the center of the embedded YouTube video
            ActionChains(driver).move_to_element(play_button).click(play_button).perform()

            # Step 7: Use JavaScript to set the volume of the embedded video to maximum
            volume_script = """
            var video = document.querySelector('video');
            if (video) {
                video.volume = 1.0;  // Set volume to maximum (1.0 = 100%)
            }
            """
            driver.execute_script(volume_script)

            # Step 8: Wait for the embedded video to play for the specified duration
            time.sleep(duration)

            # Step 8: Switch back to the main content
            driver.switch_to.default_content()

        except Exception as e:
            # Handle exceptions for individual URLs
            print(f"Error processing URL {video['url']}: {e}")
            continue  # Skip to the next video

except KeyboardInterrupt:
    print("\nExecution interrupted by user (CTRL-C). Cleaning up...")

finally:
    # Ensure WebDriver quits only if initialized
    if 'driver' in locals() and driver:
        driver.quit()
        print("WebDriver quit successfully.")

# Why ChatGPT Recommended ChromeDriver
#  o Known Issues with Safari WebDriver: Safari WebDriver has known limitations and quirks that can
#    hinder the smooth execution of automated tests.
#  o Wide Usage of ChromeDriver: ChromeDriver's stability, flexibility, and compatibility make it
#    the preferred choice for most Selenium users.
#  o User Interaction Allowed: Since you needed functionality where users could
