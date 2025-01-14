# This file is for running Selenium with Edge on Samsung Snapdragon ARM64 laptop
# See cmds for some requirements before this program can run

from selenium import webdriver
from selenium.webdriver.common.by    import By
from selenium.webdriver.support.ui   import WebDriverWait
from selenium.webdriver.support      import expected_conditions as EC
from selenium.webdriver.edge.service import Service
# from selenium.webdriver.edge.options import Options  Does not help, so comment out
from selenium.webdriver.common.action_chains import ActionChains
from get_server_urls import get_urls_from_server, videos
from get_yt_duration import get_video_duration
import time, random, sys

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

# Actually, there is no Flask ChineseSong app running on localhost:5001 on Snapdragon
if len(sys.argv) != 3 or not (sys.argv[1] == 'linode' or sys.argv[1] == 'local'):
    print("Usage: python selenium_play.py linode|local <num>, num is # of videos to play")
    sys.exit(1)

print(f"Running Selenium with Edge on Windows with Snapdragon ARM64 CPU")
# The following EdgeDriver options are supposed to be able to suppress the following two non
# fatal messages seen when we run:
#     (1) DevTools listening on ws://127.0.0.1:58245/devtools/browser/0b9eb838-130b-4d0b-93a6-a77ca6b7bacf
#     (2) [28000:9296:0109/150350.346:ERROR:fallback_task_provider.cc(127)] ...
# but did not work. ChatGPT believes:
#     They are harmless. These logs do not impact the functionality of your script.
#     Chromium Bug: The fallback_task_provider message refers to a known Chromium issue that remains
#     unresolved.
# Because there is no ChromeDriver for ARM64 CPU, I have to wait for fixes in EdgeDriver or
# a ChromeDriver for ARM64. For now just keep the following block of code comment out
# edge_options = Options()                                        # Needed for Maximize browser window etc
# edge_options.add_argument('--disable-gpu')                      # Disables GPU hardware acceleration.
# edge_options.add_argument('--disable-software-rasterizer')      # May help avoid relying on GPU HW acceleration
# edge_options.add_argument('--force-compositing-mode')           # Forces compositing mode, avoiding GPU issues
# edge_options.add_argument('--disable-accelerated-video-decode') # Disable accelerated video decode
# edge_options.add_argument('--disable-accelerated-video-encode') # Disable accelerated video encode
# edge_options.add_argument('--disable-accelerated-2d-canvas')    # Disable 2D canvas acceleration
# edge_options.add_argument('--use-gl=desktop')                   # Forces use of desktop OpenGL
# edge_options.add_argument('--disable-compositing')              # Disable compositing altogether.
# edge_options.add_argument('--use-angle=direct3d')               # Force Direct3D rendering backend
# edge_options.add_argument('--log-level=3')                      # Set logging to 'ERROR' level
# edge_options.add_argument('--disable-video-overlay')            # Disable video overlay features
# edge_options.add_argument('--disable-video-autoplay')           # Disable video autoplay features
# edge_options.add_argument('--disable-dev-shm-usage')            # Avoid logging related to dev tools

driver_class = webdriver.Edge      # Snapdragon has to use Selenium with Edge browser
driver_path  = r"C:\Users\User\Yuming\edgedriver_arm64\msedgedriver.exe"    # Set path to EdgeDriver
service      = Service(executable_path=driver_path)
driver       = driver_class(service=service)

if get_urls_from_server("All", server) == -1:    # All means all songs
    print("Error: abort")
    sys.exit(1)  # Abort!
if get_urls_from_server("Bonus", server) == -1:  # Bonus will get data for all bonuses
    print("Error: abort")
    sys.exit(1)  # Abort!

num_videos = len(videos)
num_min    = min(num_input, num_videos)

print(f"Playing {num_min} out of {num_videos} songs and bonuses from ", end='')
if server == "linode":
    print("www.chinesesong.net...")
else:
    print("localhost...")

random.shuffle(videos)  # Shuffle the items inside array videos

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
            width  = int(screen_width  * 0.9)     # Calculate 90% dimensions
            height = int(screen_height * 0.9)
            driver.set_window_size(width, height) # Resize the window to 90% of the screen size

            # Step 3: Ensure the YouTube iframe is fully in view and switch to it
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
            # time.sleep(2)

            # Step 5: Click the play button at the center of the embedded YouTube video
            ActionChains(driver).move_to_element(play_button).click(play_button).perform()

            # Step 6: Use JavaScript to set the volume of the embedded video to maximum
            volume_script = """
            var video = document.querySelector('video');
            if (video) {
                video.volume = 1.0;  // Set volume to maximum (1.0 = 100%)
            }
            """
            driver.execute_script(volume_script)

            # Step 7: Call get_yt_video_duration(video['url']) to get the duration of the YouTube video from YouTube website
            # duration = 360  # Default time in seconds for play a video
            duration = get_video_duration(video['url']) + 3
            minutes, seconds = divmod(int(duration), 60)
            formatted_time = f"{minutes}:{seconds:02}"  # Format as "minutes:seconds"
            # Print video title and duration, reserve 3 spaces for aligning the numbers in 1~999
            print(f"{i+1:3}: {video['title']} {formatted_time}")

            # Step 8: Wait for the embedded video to play for the specified duration
            time.sleep(duration)

            # Step 9: Switch back to the main content
            driver.switch_to.default_content()

        except Exception as e:
            # Handle exceptions for individual URLs
            print(f"Error processing {video['title']} at URL {video['url']}: {e}")
            continue  # Skip to the next video

except KeyboardInterrupt:
    print("\nExecution interrupted by user (CTRL-C). Cleaning up...")

finally:
    # Ensure WebDriver quits only if initialized
    if 'driver' in locals() and driver:
        driver.quit()
        print("WebDriver quit successfully.")
