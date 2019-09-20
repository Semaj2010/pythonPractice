#!/usr/bin/env python

import http.cookiejar
import urllib.parse
import urllib.request

ID_USERNAME = 'id_username'
ID_PASSWORD = 'id_password'
USERNAME = 'semaj9310@gmail.com'
PASSWORD = 'wpdlatm265%'
LOGIN_URL = 'https://bitbucket.org/account/signin/?next=/'
NORMAL_URL = 'http://bitbucket.org'

def extract_cookie_info():
    """Fake login to a site with a cookie"""
    # Setup cookie jar
    cj = http.cookiejar.LWPCookieJar()
    login_data = urllib.parse.urlencode({ID_USERNAME : USERNAME, ID_PASSWORD : PASSWORD})
    login_data = login_data.encode('utf-8')

    # create url opener
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    resp = opener.open(LOGIN_URL, login_data)

    # send login info
    for cookie in cj:
        print("------First time cookie : %s --> %s " % (cookie.name, cookie.value))
    print("Headers : %s " % resp.headers)

    # now access without any login info
    resp = opener.open(NORMAL_URL)
    for cookie in cj:
        print("++++++++Second time cookie: %s --> %s" % (cookie.name, cookie.value))

    print("Headers : %s" % resp.headers)

if __name__ == '__main__':
    extract_cookie_info()