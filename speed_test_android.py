"""
This script is designed to perform automated testing and performance analysis of the Speedtest Android app using Appium and Headspin.
It launches the Speedtest app, performs various actions, captures key performance indicators (KPIs), and sends the analysis to the Headspin platform.

Requirements:
- Python 3.x
- Appium (Python library)
- Selenium (Python library)
- Appium server running
- Headspin account and access token

Usage:
python script_name.py --udid device_udid --url headspin_api_url

"""


import time
import unittest
import argparse
from time import sleep
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib3
import requests
import time

# Disable SSL warnings
urllib3.disable_warnings()

class SpeedtestAndroidTest(unittest.TestCase):

    # Test configuration
    test_name = "SpeedTest"
    package = "org.zwanoo.android.speedtest"
    activity = "com.ookla.mobile4.screens.main.MainActivity"
    description = "Headspin Page Load Analysis Sample Session"
    
    def setUp(self):
        """
        Set up the test environment by configuring the desired capabilities and establishing a connection to the Appium server.

        This function initializes the necessary parameters and establishes a connection with the Appium server.
        It configures desired capabilities for the Android platform, app package, activity, automation, and Headspin integration.
        It also initializes key performance indicator (KPI) labels and sets up various wait and session-related attributes.

        Note:
            - This function relies on the availability of the `udid`, `url`, and `self.package` values.
            - The `self.wait`, `self.short_wait`, and `self.long_wait` attributes are used for different waiting scenarios.
            - The `self.driver` attribute is the main WebDriver instance for the Appium connection.

        Raises:
            selenium.common.exceptions.WebDriverException: If there is an issue establishing the Appium connection.
        """
        # Initialize desired capabilities
        self.desired_caps = {}

        # Appium Capabilities
        self.desired_caps['platformName'] = "Android"
        self.desired_caps['udid'] = udid
        self.desired_caps['deviceName'] = udid
        self.desired_caps['appPackage'] = self.package
        self.desired_caps['appActivity'] = self.activity
        self.desired_caps['newCommandTimeout'] = 300
        self.desired_caps['noReset'] = True
        self.desired_caps['automationName'] = "UiAutomator2"
        self.desired_caps['autoLaunch'] = False
        # Headspin Capabilities
        self.desired_caps['headspin:capture.autoStart'] = True
        self.desired_caps['headspin:capture.video'] = True
        self.desired_caps['headspin:capture.network'] = False
        self.desired_caps['headspin:testName'] = self.test_name 
        self.desired_caps['headspin:session.name'] = self.test_name 
        self.desired_caps['headspin:session.description'] = self.description
        
        # Initialize KPI labels
        self.kpi_labels = {}
        self.kpi_labels["Launch Time"] = {"start" : None, "end" : None}
        self.kpi_labels["Status Loading Time"] = {"start" : None, "end" : None}
        
        # Initialize the Appium WebDriver instance
        self.driver = webdriver.Remote(url, self.desired_caps)
        
        # Initialize wait instances
        self.wait = WebDriverWait(self.driver,30)
        self.short_wait = WebDriverWait(self.driver, 0.1)
        self.long_wait = WebDriverWait(self.driver, 90)

        # Store the session ID
        self.session_id = self.driver.session_id

    def test_SpeedTest(self):
        """
        Main test function that orchestrates the execution of other test script functions.

        This function serves as the main entry point for the test execution. It controls the flow by calling
        other functions responsible for specific test steps, such as measuring app launch time, loading status,
        performing Speedtest, and updating the test status.

        Note:
            - This function relies on the availability of `self.driver`, `self.package`, `self.status`, and other functions
            within the same class for the test execution.

        Side Effects:
            This function sets the `self.status` attribute to "Passed" to indicate a successful test execution.
        """
        # Terminate the app to start a fresh session
        self.driver.terminate_app(self.package)
        sleep(3)
        
        # Measure app launch time
        self.get_launch_kpi()
        
        # Measure status loading time
        self.get_status_loading_kpi()
        
        # Perform Speedtest and capture network KPIs
        self.get_network_kpis()

        # Update the test status as "Passed"
        self.status = "Passed"

    
    def get_launch_kpi(self):
        """
        Measure the time taken to launch the Speedtest app and update the KPIs accordingly.

        This function calculates the time it takes to launch the Speedtest app and captures this duration as a KPI.
        It updates the "Launch Time" KPI in the `self.kpi_labels` dictionary with the recorded start and end times.

        Note:
            - This function relies on the availability of the `self.driver` attribute for interacting with the app.
            - The `self.wait` attribute is used for element presence verification.
            - The `self.kpi_labels` dictionary is updated to store the captured KPI.

        Side Effects:
            - This function sets the `self.status` attribute to indicate whether the launch was successful or not.
            - It updates the "Launch Time" KPI in the `self.kpi_labels` dictionary.
        """
        # Set status to indicate launch failure by default
        self.status = "Launch Failed"
        
        # Record the start time of app launch
        self.kpi_labels["Launch Time"]['start'] = time.time()
        
        # Launch the Speedtest app
        self.driver.launch_app()
        
        # Wait for the presence of a specific element (e.g., "Go" button) to ensure successful launch
        self.wait.until(EC.presence_of_element_located((MobileBy.ID, 'org.zwanoo.android.speedtest:id/go_button')))
        
        # Record the end time of app launch
        self.kpi_labels["Launch Time"]['end'] = time.time()
        
        sleep(2)  # Allow some time for stability


    def get_status_loading_kpi(self):
        """
        Measure the time taken to load the status section in the app and update the KPIs accordingly.

        This function measures the time it takes to load the status section within the Speedtest app and
        captures this duration as a KPI. It also updates sensitivity values for analysis.

        The captured time values are stored in the KPI dictionary under "Status Loading Time". The sensitivity
        value is set to 0.99 by default.

        This function relies on the `self.wait` attribute for element presence verification and `self.kpi_labels`
        dictionary for KPI storage.

        Raises:
            selenium.common.exceptions.TimeoutException: If the status element does not appear within the specified timeout.
        """
        # Set status loading status
        self.status = "Status Loading Failed"
        
        # Wait for the "Status" element to be present
        status = self.wait.until(EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, "Status")))
        
        # Record the start time of status loading
        self.kpi_labels["Status Loading Time"]['start'] = time.time()
        
        # Click on the "Status" element
        status.click()
        
        # Wait for the desired section to load
        self.wait.until(EC.presence_of_element_located((MobileBy.ID, 'org.zwanoo.android.speedtest:id/site_name')))
        
        # Record the end time of status loading
        self.kpi_labels["Status Loading Time"]['end'] = time.time() 
        
        # Set sensitivity value for analysis
        self.kpi_labels["Status Loading Time"]['start_sensitivity'] = 0.99
        
        sleep(2)

    def get_network_kpis(self):
        """
        Perform the Speedtest .

        This function initiates the Speedtest within the Speedtest Android app. It clicks on the "Speed" element,
        triggers the Speedtest process

        """
        # Set initial Speedtest status
        self.status = "Speedtest Failed"
        
        # Click on the "Speed" element to initiate the Speedtest
        self.wait.until(EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, "Speed"))).click()
        
        # Find and click the "Begin Test" button
        begin_button = self.wait.until(EC.presence_of_element_located((MobileBy.ID,'org.zwanoo.android.speedtest:id/go_button')))
        sleep(2)  # Wait for stability
        begin_button.click()
        print("\nStarted Speedtest\n")
        
        # Update Speedtest status to indicate initiation
        self.status = "Speedtest_failed"  # This status change if the test completes successfully
        
        # Wait for the Speedtest to complete
        self.long_wait.until(EC.presence_of_element_located((MobileBy.ID,'org.zwanoo.android.speedtest:id/shareIcon')))
        print("\nSpeedtest Finished\n")

    def tearDown(self):
        """
        Clean up after the test execution, including sending KPI data to the Headspin platform.

        This function performs cleanup operations after the test execution. It sets the Headspin session status
        based on the test status (passed or failed). It also prints the session URL for reference.

        Additionally, it calls the `perform_page_load_analysis` function to send captured KPI data for page load analysis.

        Note:
            The session status is determined by the presence of "Fail" in the `self.status` attribute.

        """
        # Determine the session_status based on test status
        session_status = "Passed" if "Fail" not in self.status else "Failed"

        # Set Headspin session status and quit the appium driver.
        self.driver.execute_script('headspin:quitSession', {'status': session_status})

        # Generate session URL for reference
        session_url = "https://ui-dev.headspin.io/sessions/" + self.session_id + "/waterfall"
        print("\nURL :", session_url)

        # Calling the function to perform page load analysis
        self.perform_page_load_analysis()

    
    def perform_page_load_analysis(self):
        """
        Perform page load analysis by sending captured KPI data to the Headspin platform.

        This function constructs a payload containing the captured key performance indicators (KPIs) and sends it
        to the Headspin API for page load analysis.

        The constructed payload includes the timestamp and sensitivity values for each KPI. The analysis results
        are sent to the specified Headspin session for further evaluation.

        Raises:
            requests.exceptions.HTTPError: If there is an error in sending the payload to the Headspin API.

        Note:
            This function relies on the `self.kpi_labels` dictionary populated during the test execution.
        """

        # Preparing pay_load for page load analysis api.
        pay_load = {"regions": [], "wait_timeout_sec": 600}
        for key in self.kpi_labels:
            if self.kpi_labels[key]["start"] is not None and self.kpi_labels[key]["end"] is not None:
                label_item = {"name": key}
                for item in ["start", "end"]:
                    label_item[f"ts_{item}"] = self.kpi_labels[key][item]

                if self.kpi_labels[key].get("start_sensitivity") :
                    label_item["start_sensitivity"] = self.kpi_labels[key]["start_sensitivity"]

                if self.kpi_labels[key].get("end_sensitivity"):
                    label_item["end_sensitivity"] = self.kpi_labels[key]["end_sensitivity"]
                pay_load["regions"].append(label_item)

        # API call to perform page load analysis
        request_url = f"https://api-dev.headspin.io/v0/sessions/analysis/pageloadtime/{self.session_id}"
        r = requests.post(
            request_url, headers=headers, json=pay_load)
        r.raise_for_status()

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--udid', dest='udid',
                        type=str, nargs='?',
                        default=None,
                        required=True,
                        help="udid")
    parser.add_argument('--url', dest='url',
                        type=str, nargs='?',
                        default=None,
                        required=True,
                        help="url")
    
    args = parser.parse_args()
    udid = args.udid
    url = args.url
    access_token = url.split('/')[-3]
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    # Load and run the test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(SpeedtestAndroidTest)
    unittest.TextTestRunner(verbosity=2).run(suite)


