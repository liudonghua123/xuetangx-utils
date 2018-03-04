#!/usr/bin/env python
# coding=utf-8

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException  
from selenium.webdriver.chrome.options import Options
import re
import os
import urllib.request

# construct the regex to normalize filename
regex = re.compile(r"[\s\\/]+", re.IGNORECASE)
def normalize_filename(filename):
    return regex.sub("_", filename)

def check_exists_by_xpath(driver, xpath):
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    except (NoSuchElementException, TimeoutException) as e:
        return False
    return True

def check_exists_by_tag_name(driver, tag_name):
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))
    except (NoSuchElementException, TimeoutException) as e:
        return False
    return True    

def get_downloadInfo(courseUrl):
    # create driver
    chrome_options = Options()
    # read HEADLESS environment to detect whether to use --headless argument
    if 'HEADLESS' in os.environ:
        chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    # create WebDriverWait instance
    wait = WebDriverWait(driver, 10)
    # open course home page
    driver.get(courseUrl)

    # now in home page
    button = wait.until(EC.element_to_be_clickable((By.ID, 'join_free')))
    button.click()

    # wait for loading page
    username = wait.until(EC.element_to_be_clickable((By.NAME, 'username')))
    password = driver.find_element_by_name('password')

    # fill username with USERNAME environment value
    username.send_keys(os.environ['USERNAME'])
    # fill password with USERNAME environment value
    password.send_keys(os.environ['PASSWORD'])
    # login
    password.submit()
    # re-click join_free button
    button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, '进入课程')))
    button.click()
    # get all the chapter links
    atags = driver.find_elements_by_xpath("//div[@id='accordion']/nav/div/ul/li/a")
    atagsUrl = [atag.get_attribute('href') for atag in atags]
    downloadInfo = []
    for atagUrl in atagsUrl:
        # print(atagUrl)
        driver.get(atagUrl)
        # get all tabs which contains video
        tabs = driver.find_elements_by_xpath("//ol[@id='sequence-list']/li/a")
        for tab in tabs:
            tab.click()
            # check if there is a video tag
            if check_exists_by_tag_name(driver, 'video'):
                # get chapter\subChapter\title information 
                chapter = re.split('\s+', driver.find_element_by_xpath("//div[@class='chapter is-open']/h3/a[1]").text)[0]
                subChapter = re.split('\s+', driver.find_element_by_xpath("//div[@class='chapter is-open']/ul/li/a/p[1]").text)[0]
                title = driver.find_element_by_xpath("//div[@class='xblock xblock-student_view xmodule_display xmodule_VideoModule xblock-initialized']/h2").text
                # get video element
                video = driver.find_element_by_tag_name('video')
                downloadInfo.append(("{chapter} {subChapter} {title}".format(chapter=chapter, subChapter=subChapter, title=title), video.get_attribute('src')))
    return downloadInfo


def downloadFile(downloadInfo):
    count = len(downloadInfo)
    for index, entry in enumerate(downloadInfo):
        filename = normalize_filename(entry[0])
        filePath = "videos/{filename}.mp4".format(filename=filename)
        url = entry[1]
        print("{index}/{count} downloading {filename}.mp4".format(index=index,count=count,filename=filename))
        urllib.request.urlretrieve (url, filePath)

if __name__ == "__main__":
    # get course url, if not set in environment then use a default one
    downloadInfo = get_downloadInfo(os.environ['COURSEURL'] if 'COURSEURL' in os.environ else 'http://www.xuetangx.com/courses/course-v1:CAU+08110140_1x+sp/about')
    downloadFile(downloadInfo)