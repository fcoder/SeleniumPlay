# This file is for running Selenium with Chrome on WinTel system (Not fully tested)
# See cmds for some requirements before this program can run

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from get_server_urls import get_urls_from_server, videos
from get_yt_duration import get_video_duration
import time, random, sys
import platform

# Get the command line argument
try:
    server    = sys.argv[1]
    num_input = int(sys.argv[2])
except ValueError:
    print("The arguments must be integers.")
    sys.exit(1)

if num_input < 1:
    print("The last command line argument must be a positive integer")
    sys.exit(1)

if len(sys.argv) != 3 or not (sys.argv[1] == 'linode' or sys.argv[1] == 'local'):
    print("Usage: python selenium_play.py linode|local <num>, num is # of videos to play")
    sys.exit(1)

if get_urls_from_server("All", server) == -1:     # All means all songs
    print("Error: abort")
    sys.exit(1)  # Abort!
if get_urls_from_server("Bonus", server) == -1:   # Bonus will get data for all bonuses
    print("Error: abort")
    sys.exit(1)  # Abort!

num_videos = len(videos)
num_min    = min(num_input, num_videos)
print(f"Got {num_videos} songs and bonus from server, playing the first {num_min}...")

random.shuffle(videos)  # Shuffle the items inside array videos

# Check if this program is running on a WinTel computer
arch = platform.machine()
if arch == "x86_64" or arch == "AMD64":    # Don't confuse AMD64 with ARM64!
    print(f"Running Selenium with Chrome on Windows with {arch} CPU")
else:
    print("Error: CPU is not x86_64 or ARM64")
    sys.exit(1)

# Configure Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start Chrome maximized

driver_class = webdriver.Chrome
driver_path  = r"C:\Users\swang\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
service      = Service(executable_path=driver_path)
driver       = driver_class(service=service)

try:  # Any exception during the loop will jump directly to the finally block.
    for i, video in enumerate(videos):
        if i >= num_min:
            break

        try:
            # Step 1: Get a web page from chinesesong.net which contains an embedded YouTube
            driver.get(video['url'])

            # Step 2: Set screen size to 90% of the Window using JavaScript, so it is easer to move the window around
            screen_width  = driver.execute_script("return window.screen.availWidth;")
            screen_height = driver.execute_script("return window.screen.availHeight;")

            # Calculate 90% dimensions
            width = int(screen_width * 0.9)
            height = int(screen_height * 0.9)

            # Resize the window to 90% of the screen size
            driver.set_window_size(width, height)

            # Step 3: Ensure the YouTube iframe is fully in view before switching to it
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "youtube-iframe"))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", iframe)

            # Switch to the YouTube iframe
            driver.switch_to.frame(iframe)

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

            # Step 5: Click the play button at the center of the embedded YouTube video
            ActionChains(driver).move_to_element(play_button).click(play_button).perform()

            # Use JavaScript to set the volume of the embedded video to maximum
            volume_script = """
            var video = document.querySelector('video');
            if (video) {
                video.volume = 1.0;  // Set volume to maximum (1.0 = 100%)
            }
            """
            driver.execute_script(volume_script)


            # Step 6: Call get_yt_video_duration(video['url']) to get the duration of the YouTube video from YouTube website
            duration = get_video_duration(video['url']) + 3
            minutes, seconds = divmod(int(duration), 60)
            formatted_time = f"{minutes}:{seconds:02}"  # Format as "minutes:seconds"

            # Print video title and duration, reserve 3 spaces for aligning the numbers in 1~999
            print(f"{i+1:3}: {video['title']} {formatted_time}")

            # Step 7: Wait for the embedded video to play for the specified duration
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
