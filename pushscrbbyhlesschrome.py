#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup

import urllib
from urllib.parse import urlparse
import urllib.request

import json
import re

def main():
    USER = os.getenv('SCRAPBOX_USER')
    PASS = os.getenv('SCRAPBOX_PASS')

def getHighlightTitle():
    # aws
    # url = 'http://ec2'
    # response = urllib.request.urlopen(url)
    # update_json = json.loads(response.read().decode('utf8'))

    with open('./assets/last.json', 'r') as f:
        update_json = json.load(f)

    updated = []
    for updated_time in update_json:
        for updated_title in update_json[updated_time]:
            updated.append(updated_title)

    return updated

def getUpdatedHighlight():
    titles = getHighlightTitle()
    print(titles)
    # baseurl = 'http://ec2'
    baseurl = './assets/highlight/'
    highlight_jsons = {}
    for title in titles:
        updated_url = baseurl + title + '.json'

        # regex = r'[^\x00-\x7F]'
        # matchedList = re.findall(regex, updated_url)
        # for m in matchedList:
        #     updated_url = updated_url.replace(m, urllib.parse.quote_plus(m, encoding='utf-8'))

        # response = urllib.request.urlopen(updated_url)
        # update_json = json.loads(response.read().decode('utf8'))
        with open(updated_url, 'r') as f:
            update_json = json.load(f)

        for key in update_json:
            highlight_jsons[title] = update_json[key]
    return highlight_jsons

def main():

    # get newly highlighted title
    updated = getUpdatedHighlight()
    print(updated)

    USER = 'id'
    PASS = 'pass'



    options = Options()
    # options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    # driver = webdriver.Chrome(chrome_options=options)
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')
    try:
        url = 'https://scrapbox.io/tkgshn-private/'
        driver.get(url)
        sleep(4)

        # login with google page
        btn = driver.find_element_by_class_name('btn')
        actions = ActionChains(driver)
        actions.move_to_element(btn)
        actions.click()
        actions.perform()
        sleep(5)

        # mail address
        actions.reset_actions()
        uid = driver.find_element_by_id('identifierId')
        actions.move_to_element(uid)
        actions.click()
        actions.send_keys(USER)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        sleep(3)

        # password
        actions.reset_actions()
        upw = driver.find_element_by_name('password')
        actions.move_to_element(upw)
        actions.click()
        actions.send_keys(PASS)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        sleep(7)


        # update page every highlights.
        for updated_titlekey in updated:
            print('updated_titlekey', updated_titlekey)

            project_home = driver.find_element_by_class_name('project-home')
            actions.reset_actions()
            actions.move_to_element(project_home)
            actions.click()
            actions.perform()
            sleep(2)

            searchform = driver.find_element_by_class_name('form-control')
            actions.reset_actions()
            actions.move_to_element(searchform)
            actions.click()
            actions.send_keys('#'+updated_titlekey)
            actions.send_keys(Keys.RETURN)
            actions.perform()
            sleep(4)
            actions.reset_actions()

            try: #if no updated_title page.
                not_found = driver.find_element_by_class_name('search-not-found')

                print('no:', updated_titlekey, 'memo')
                newbutton = driver.find_element_by_class_name('new-button')
                actions.move_to_element(newbutton)
                actions.click()
                actions.perform()
                sleep(3)
                actions.reset_actions()
                section0 = driver.find_element_by_class_name('section-0')
                actions.move_to_element(section0)
                actions.click()
                actions.key_down(Keys.CONTROL).send_keys("e").key_up(Keys.CONTROL)
                actions.send_keys(Keys.RETURN)
                actions.send_keys('#readings')
                actions.send_keys(Keys.RETURN)
                actions.send_keys('#highlight')
                actions.send_keys(Keys.RETURN)
                actions.send_keys('#'+updated_titlekey)
                actions.send_keys(Keys.RETURN+Keys.RETURN)
                actions.perform()
                sleep(3)


            except: # if there is updated_title page.

                page_list_item = driver.find_element_by_class_name('page-list-item')
                actions.move_to_element(page_list_item)
                actions.click()
                actions.perform()
                sleep(3)


            # memo update
            highlights = updated[updated_titlekey]
            for poskey in highlights:
                print('--poskey:', poskey)
                conti = False
                addpos = -1
                titleclassnum = 0
                # pos check
                html = driver.page_source.encode('utf-8')
                bsObj = BeautifulSoup(html, "html.parser")
                alreadyPoss = bsObj.find_all('div', class_='section-title')
                for alrposdiv in alreadyPoss[1:]: # except page title
                    alrpos = alrposdiv.find_all('span', class_=re.compile('c-[0-9]+'))
                    titleclassnum += 1

                    p = ""
                    for x in alrpos: p += x.text
                    if not p[:4]=='pos:':
                        continue

                    p = p[4:]
                    print('p:',int(p))
                    if int(p) == int(poskey):
                        print('=are samepos')
                        conti = True
                        break
                    elif int(p) < int(poskey):
                        print('next posi')
                        continue
                    else:
                        print('here!')
                        addpos = titleclassnum
                        break
                if conti:
                    continue

                print('addpos:', addpos)

                # insert to last line.
                actions.reset_actions()
                if addpos == -1:
                    lastline = driver.find_element_by_css_selector('div.lines .line:last-child')
                    actions.move_to_element(lastline)
                    actions.click()
                    actions.send_keys(Keys.RETURN)
                    actions.send_keys('pos: ' + str(poskey))
                    actions.send_keys(Keys.RETURN)
                    actions.pause(1)
                    actions.send_keys('> ')
                    actions.send_keys(highlights[poskey])
                    actions.send_keys(Keys.RETURN)
                    actions.send_keys(' memo:')
                    actions.send_keys(Keys.RETURN, Keys.RETURN)
                    actions.send_keys(Keys.DOWN)
                    actions.send_keys(Keys.DOWN)
                    actions.send_keys(Keys.DOWN)
                    actions.send_keys(Keys.DOWN)
                    actions.send_keys(Keys.DOWN)
                    actions.pause(1)
                    actions.perform()
                    actions.reset_actions()

                # insert between already exist highlight.
                else:
                    addline = driver.find_element_by_css_selector('div.lines .line.section-title.section-'+str(addpos))
                    actions.move_to_element(addline)
                    actions.click()
                    actions.pause(1)
                    actions.send_keys(Keys.UP).send_keys(Keys.RETURN)
                    actions.send_keys(Keys.UP).send_keys(Keys.RETURN)
                    actions.send_keys(Keys.UP).send_keys(Keys.RETURN)
                    actions.pause(1)
                    actions.send_keys('pos: ' + str(poskey))
                    actions.send_keys(Keys.RETURN)
                    actions.pause(1)
                    actions.send_keys('> ')
                    actions.send_keys(highlights[poskey])
                    actions.send_keys(Keys.RETURN)
                    actions.send_keys(' memo:')
                    actions.send_keys(Keys.RETURN, Keys.RETURN)
                    actions.send_keys(Keys.DOWN)
                    actions.send_keys(Keys.DOWN)
                    actions.send_keys(Keys.DOWN)
                    actions.send_keys(Keys.DOWN)
                    actions.send_keys(Keys.DOWN)
                    actions.pause(1)
                    actions.perform()
                    actions.reset_actions()


    except:
        import traceback
        traceback.print_exc()
        driver.quit() # for bug.

    driver.quit()

if __name__=='__main__':
    main()
