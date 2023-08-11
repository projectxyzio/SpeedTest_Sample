import time
import unittest
import argparse
from time import sleep
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib3
import sys
import os
import time
urllib3.disable_warnings()



root_dir = os.path.dirname(__file__)
lib_dir = os.path.join(root_dir, 'lib')
pages_dir = os.path.join(root_dir, 'pages')
fixture_data_dir = os.path.join(root_dir, 'fixture_data')
sys.path.append(lib_dir)

from hs_api import hsApi


class SpeedtestAndroidTest(unittest.TestCase):

    test_name = "SpeedTest_Android"
    package = "org.zwanoo.android.speedtest"
    activity = "com.ookla.mobile4.screens.main.MainActivity"


#                   ******* Test  Script Function   ************
    #TEST script  part to setup the Capabilites and start the driver
    def setUp(self):

        self.desired_caps = {}
        self.desired_caps['platformName'] = "Android"
        self.desired_caps['headspin:testName'] =self.test_name 
        self.desired_caps['headspin:session.name'] =self.test_name 
        self.desired_caps['udid'] = udid
        self.desired_caps['deviceName'] = udid
        self.desired_caps['appPackage'] = self.package
        self.desired_caps['appActivity'] = self.activity
        self.desired_caps['disableWindowAnimation'] = True
        self.desired_caps['newCommandTimeout'] = 300
        self.desired_caps['headspin:capture.video'] = True
        self.desired_caps['headspin:capture.network'] = False
        self.desired_caps['noReset'] = False
        self.desired_caps['automationName'] = "UiAutomator2"
        self.desired_caps['autoGrantPermissions'] = True
        self.desired_caps['autoLaunch'] = False
        
        #Initializing Kpis
        self.kpi_labels = {}
        self.kpi_labels["Launch"] = {"start" : None, "end" : None}
        
        self.kpi_labels["Status Loading Time"] = {"start" : None, "end" : None}
        self.kpi_labels["Status Loading Time"]['start_sensitivity'] = 0.99

        self.data_kpis = {}
        self.data_kpis["Download_speed"] = None
        self.data_kpis["Upload_speed"] = None
        self.data_kpis["Launch"] = None
        self.data_kpis["Status Loading Time"] = None
        
        # headspin api module object creation
        self.hs_api_call = hsApi(udid, access_token)
        
        
        self.driver = webdriver.Remote(url, self.desired_caps)
        
        self.wait = WebDriverWait(self.driver,30)
        self.short_wait = WebDriverWait(self.driver, 0.1)
        self.long_wait = WebDriverWait(self.driver, 90)
        self.session_id = self.driver.session_id

    #TEST script function  to  call  all the  test script function.
    def test_SpeedTest(self):

        self.driver.terminate_app(self.package)
        sleep(3)
        
        self.kpi_labels["Launch"]['start'] = int(round(time.time() * 1000))
        self.driver.launch_app()
        self.manage_permission()
        self.get_status_loading_kpi()
        self.get_network_kpis()

        self.status = "Passed"

    #TEST script part to manage the starting pop ups and permissions.
    def manage_permission(self):
        self.status="Failed_Grand_the_app_permission"

        self.wait.until(EC.presence_of_element_located((MobileBy.CLASS_NAME, "android.widget.Button")))
        sleep(3)
        self.kpi_labels["Launch"]['end'] = int(round(time.time() * 1000))
        print("\nApp launched\n")

        sleep(2)
        # ELEMENT LIST 
        next = (MobileBy.ANDROID_UIAUTOMATOR,'text("Next")')
        continue_banner = (MobileBy.ANDROID_UIAUTOMATOR,'textContains("Continue")')
        allow_btn = (MobileBy.ANDROID_UIAUTOMATOR,'text("Allow")')
        done_button = (MobileBy.ANDROID_UIAUTOMATOR,'textContains("Done")')
        allow_all_time  = (MobileBy.ANDROID_UIAUTOMATOR,'text("Allow all the time")')
        go_btn = (MobileBy.ID,'org.zwanoo.android.speedtest:id/go_button')
        while_uing_app = (MobileBy.ANDROID_UIAUTOMATOR,'textContains("While using the app")')
        back = (MobileBy.ACCESSIBILITY_ID,'Back')

        element_list = [next,back, continue_banner, allow_btn,while_uing_app,
                        allow_all_time, done_button, go_btn]


        for _ in range(10):
            element,locator = self.find_element_from_locator_list(element_list)
            if locator  ==  go_btn :
                print("\nReady to Start SpeedTest\n")
                break 
            else:
                sleep(1)
                element.click()

        sleep(3)

    def get_status_loading_kpi(self):
        self.status = "Status Loading Failed"
        status = self.wait.until(EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, "Status")))
        self.kpi_labels["Status Loading Time"]['start'] = int(round(time.time() * 1000))
        status.click()
        self.wait.until(EC.presence_of_element_located((MobileBy.ID, 'org.zwanoo.android.speedtest:id/site_name')))
        self.kpi_labels["Status Loading Time"]['end'] = int(round((time.time()+2) * 1000))
        sleep(2)
    #TEST script part to get the download and upload speed from the app.
    def get_network_kpis(self):
        self.status="Fail_Start_Speed_Test"
        self.wait.until(EC.presence_of_element_located((MobileBy.ACCESSIBILITY_ID, "Speed"))).click()
        begin_button = self.wait.until(EC.presence_of_element_located((MobileBy.ID,'org.zwanoo.android.speedtest:id/go_button')))
        sleep(2)

        #Begin SpeedTest
        begin_button.click()
        print("\nStarted Speedtest\n")

        self.status= "Speedtest_failed"
        self.long_wait.until(EC.presence_of_element_located((MobileBy.ID,'org.zwanoo.android.speedtest:id/shareIcon')))
        print("\nSpeedtest Finished\n")
        results = self.wait.until(EC.presence_of_all_elements_located((MobileBy.ID,'org.zwanoo.android.speedtest:id/txt_test_result_value')))

        #DOWLOAD VALUE
        self.status="Fail_to_get_Download_value"
        self.download_speed = results[0].text
        self.data_kpis["Download_speed"] = float(self.download_speed)
        print("\nDownload value is ", self.download_speed, "Mbps")
        
        #UPLOAD VALUE
        self.status="Fail_to_get_Upload_value"
        self.upload_speed = results[1].text
        self.data_kpis["Upload_speed"] = float(self.upload_speed)
        print("\nUpload value is ", self.upload_speed, "Mbps")
        
        self.status="Passed"

    #TEST Script Post Processing Function
    def tearDown(self):
        state = "Passed" if "Fail" not in self.status else "Failed"
        self.driver.execute_script('headspin:quitSession', {'status': state})
        session_url = "https://ui-dev.headspin.io/sessions/" + self.session_id + "/waterfall"

        print("\nURL :", session_url)

        self.get_video_start_timestamp()

        self.wait_for_session_video_becomes_available()
        print("Video Available for post processing")
        # adding labels
        self.add_session_annotations()
        print("Added session Annotation ")

        session_data , session_tags = self.get_general_session_data()

        # adding data to session
        self.hs_api_call.add_session_data(session_data=session_data)
        print("Added session data ")
        # adding tags to session
        self.hs_api_call.add_session_tags(session_id=self.session_id, tag_list=session_tags)
        print("Added session tags ")

        description_string = ""
        for data in session_data['data']:
            description_string += data['key'] + " : " + str(data['value']) + "\n"
        # adding name and description to session.
        self.hs_api_call.update_session_name_and_description(session_id=self.session_id, name=self.test_name, description=description_string)
        print("updated the session  description")

#                        ******* FUNCTION  CALLS  ************
    # adding all the captured data to session data which is uploaded the session
    def get_general_session_data(self):

        session_data = {}
        session_tags=[]
        session_data['session_id'] = self.session_id
        session_data['data'] = []
        # app info
        session_data['data'].append({"key": "bundle_id", "value": self.package})
        session_data['data'].append({"key": 'status', "value": self.status})
        
        for key,value in self.data_kpis.items():
            if value:
                session_data['data'].append({"key": key, "value": value })
                session_tags.append({ key:  value })
            else:
                session_data['data'].append({"key": key, "value": -1 })
                session_tags.append({ key:  -1 })
        return session_data ,session_tags

    def add_session_annotations(self):
        page_load = {"regions": [], "wait_timeout_sec": 600}
        print("adding_visual_based_session_annotations")
        for key, value in self.kpi_labels.items():

            if self.kpi_labels[key]["start"] and self.kpi_labels[key]["end"]:
                label_start_time = (
                    self.kpi_labels[key]["start"] - self.video_start_timestamp
                )

                label_end_time = (
                    self.kpi_labels[key]["end"] - self.video_start_timestamp
                )

                if label_start_time < 0:
                    label_start_time = (
                        self.video_start_timestamp - self.video_start_timestamp
                    )
                label_item = {"name": key}
                label_item["start_time"] = label_start_time / 1000

                buffer_time = (
                    self.kpi_labels[key]["buffer_time"]
                    if self.kpi_labels[key].get("buffer_time")
                    else 0
                )

                label_item["end_time"] = (label_end_time / 1000) + buffer_time
                label_item["start_sensitivity"] = (
                    self.kpi_labels[key]["start_sensitivity"]
                    if self.kpi_labels[key].get("start_sensitivity")
                    else 0.9
                )
                label_item["end_sensitivity"] = (
                    self.kpi_labels[key]["end_sensitivity"]
                    if self.kpi_labels[key].get("end_sensitivity")
                    else 0.9
                )
                page_load["regions"].append(label_item)
        # Calling Page_load API
        page_load_response = self.hs_api_call.get_pageloadtime(
            session_id=self.session_id, data_payload=page_load
        )

        screen_change = {"labels": []}
        label_category = "SpeedTest KPI"

        if "page_load_regions" in page_load_response:
            for kpi_item in page_load_response["page_load_regions"]:

                if "start_time" in kpi_item and "end_time" in kpi_item:
                    kpi_label = {
                        "name": kpi_item["request_name"],
                        "category": label_category,
                    }
                    kpi_label["start_time"] = kpi_item["start_time"] / 1000
                    kpi_label["end_time"] = kpi_item["end_time"] / 1000
                    label_item["end_sensitivity"] = (
                        self.kpi_labels[key]["end_sensitivity"]
                        if self.kpi_labels[key].get("end_sensitivity")
                        else 0.9
                    )
                    self.data_kpis[kpi_item["request_name"]]  = round( ( kpi_label["end_time"] - kpi_label["start_time"]) ,2)
                    screen_change["labels"].append(kpi_label)

            # Adding KPI Annotation based on the result from visual page load
            self.hs_api_call.add_label(
                session_id=self.session_id, data_payload=screen_change
            )
    #Function call to get Video Time Stamp
    def get_video_start_timestamp(self):
        t_end = time.time() + 1000.0
        while time.time() < t_end:
            capture_timestamp = self.hs_api_call.get_capture_timestamp(
                self.session_id)
            self.video_start_timestamp = capture_timestamp['capture-started'] * 1000
            if 'capture-complete' in capture_timestamp:
                break
            time.sleep(1)
        return capture_timestamp

    #Function call to check Video Available for Post Processing 
    def wait_for_session_video_becomes_available(self):
        t_end = time.time() + 1200
        while time.time() < t_end:
            status = self.hs_api_call.get_session_video_metadata(self.session_id)
            if status and ("video_duration_ms" in status):
                print("\nVideo Available for Post Processing\n")
                break 

    def find_element_from_locator_list(self, locator_list, finding_time = 30):
        t_end = time.time() + finding_time
        while t_end>time.time():
            for locator in (locator_list):
                try:
                    element = self.short_wait.until(EC.presence_of_element_located(locator))
                    return element,locator
                except:
                    pass
        raise Exception(f"Could not find element from the list: {locator_list}")

if __name__ == '__main__':
    # defining Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--udid', '--udid', dest='udid',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="udid")
    parser.add_argument('--url', '--url', dest='url',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="url")
    
    
    args = parser.parse_args()
    udid = args.udid
    url = args.url
    access_token = url.split('/')[-3]
    headers = {'Authorization': 'Bearer {}'.format(access_token)}


    # perfom repeat runs
    suite = unittest.TestLoader().loadTestsFromTestCase(SpeedtestAndroidTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
        


