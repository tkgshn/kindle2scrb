#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys

from urllib.parse import urlparse
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

import signal

from time import sleep
from datetime import datetime
import re
import numpy as np
import csv
import json
import collections as cl


def main():
    USER = 'amaname'
    PASS = 'amapass'


    # options = Options()
    # options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # driver = webdriver.Chrome(chrome_options=options)
    # UserAgent = "Safari/537.36 Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66"
    # driver = webdriver.PhantomJS(
    #     desired_capabilities={'phantomjs.page.settings.userAgent': UserAgent,
    #     },
    # )
    options = Options()
    options.add_experimental_option('prefs', {'intl.accept_languages': 'ja'})
    options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    driver = webdriver.Chrome(chrome_options=options)
    # driver.set_window_size(1920, 1080)
    print('drive start')
    # url = 'https://www.amazon.co.jp/ap/signin?clientContext=375-4875962-6582025&openid.return_to=https%3A%2F%2Fread.amazon.co.jp%2Fkp%2Fnotebook%3FamazonDeviceType%3DA2CLFWBIMVSE9N&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_kp_jp&openid.mode=checkid_setup&marketPlaceId=A1VC38T7YXB528&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=amzn_kp_notebook_us&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.pape.max_auth_age=1209600&siteState=clientContext%3D355-3088953-6443912%2CsourceUrl%3Dhttps%253A%252F%252Fread.amazon.co.jp%252Fkp%252Fnotebook%253FamazonDeviceType%253DA2CLFWBIMVSE9N%2Csignature%3DSZXy31cn2x1mpyj2FotQcZRR2j2Bq3gj3D&language=ja_JP&auth=Customer+is+not+authenticated'
    url = 'https://read.amazon.co.jp/kp/notebook?amazonDeviceType=A2CLFWBIMVSE9N'
    driver.get(url)
    sleep(3)

    uid = driver.find_element_by_id('ap_email')
    upw = driver.find_element_by_id('ap_password')


    uid.send_keys(USER)
    upw.send_keys(PASS)
    sleep(5)
    driver.find_element_by_id('signInSubmit').click()
    sleep(5)

    print('url:', driver.current_url)

    # amazon.com may be accessed only 4 times in an hour by phantomjs.
    if not driver.current_url=='https://read.amazon.co.jp/kp/notebook?amazonDeviceType=A2CLFWBIMVSE9N':
        print(' はいれなかったー　')
        driver.save_screenshot('reject.png')
        return

    html = driver.page_source.encode('utf-8')
    bsObj = BeautifulSoup(html, "html.parser")
    objs = bsObj.find_all('div', class_='kp-notebook-library-each-book')

    prevExecDate = None
    if os.path.exists('./assets/last.json'): # = if this is not the first execution.
        with open('./assets/last.json', 'r') as f:
            json_data = json.load(f)
            for key in json_data:
                prevExecDate = int(key)

    if not os.path.exists('./assets/highlight/'):
        os.mkdir('./assets/highlight/')

    titlesThatHasNewHighlight = []
    for obj in objs:
        # memoContents = []
        memoContents = cl.OrderedDict()
        print('  obj.id:', obj['id'])
        idname = 'div#'+str(obj['id'])+' > span > a'
        print('  idname:', idname)

        # road time
        sleep(5)
        driver.find_element_by_css_selector(idname).click()
        sleep(10)

        html2 = driver.page_source.encode('utf-8')
        bsObjInpage = BeautifulSoup(html2, "html.parser")
        tmpDate = bsObjInpage.find('span', id='kp-notebook-annotated-date')
        tmpDate = re.split('[^0-9]', re.split('日', str(tmpDate.text))[0])
        tmpDate = np.array(tmpDate, dtype=np.int)
        lastUpDateOfThisBook = tmpDate[0]*10000 + tmpDate[1]*100 + tmpDate[2]
        if not prevExecDate==None: # after second.
            if lastUpDateOfThisBook < prevExecDate:
                break

        print('  npate:', lastUpDateOfThisBook)
        title = bsObjInpage.find('h3', class_='kp-notebook-metadata').text
        print('  title:', title)


        bf_annotations = bsObjInpage.find('div', id='kp-notebook-annotations')
        bf_highlights = bf_annotations.find_all('div', class_='a-spacing-base')
        memoContentDatas = cl.OrderedDict()
        for bf_highlight in bf_highlights:
            highlight = bf_highlight.find('span', id='highlight').text
            print('   highlight:', highlight)
            pos = bf_highlight.find('span', id='annotationHighlightHeader')
            pos = re.split(':', pos.text)[-1]
            pos = pos.replace(' ', '').replace(',', '')
            print('   pos:', pos)
            memoContentDatas[pos] = highlight.replace('', '').replace('　', '').replace('\n', '').replace('\r', '')
        memoContents[str(lastUpDateOfThisBook)] = memoContentDatas

        nospacetitle = title.replace(' ', '').replace('　', '')
        titlesThatHasNewHighlight.append(nospacetitle)
        with open('./assets/highlight/'+nospacetitle+'.json', 'w') as fw:
            json.dump(memoContents, fw, indent=4, ensure_ascii=False)


    nowtime = datetime.now()
    toDate = nowtime.year*10000 + nowtime.month*100 + nowtime.day
    lastcl = cl.OrderedDict()
    lastcl[toDate] = titlesThatHasNewHighlight
    with open('./assets/last.json', 'w') as f:
        json.dump(lastcl, f, indent=4, ensure_ascii=False)

    # with open('./assets/last.csv', 'w') as f:
    #     writer = csv.writer(f, lineterminator='\n')
    #     forjsonsave = [toDate] + titlesThatHasNewHighlight
    #     writer.writerow(fortmp)


    driver.close()
    driver.service.process.send_signal(signal.SIGTERM)
    driver.quit()
    print('driver quit')

    print('do pushscrbbyhlesschrome.py')

    os.system('ls -la')
    # os.system('sudo mv ./assets/last.json /var/www/html/')
    # os.system('sudo mv ./assets/highlight /var/www/html/')
    sleep(10)
    os.system('python pushscrbbyhlesschrome.py')



if __name__=='__main__':
    main()
