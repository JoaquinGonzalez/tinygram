import requests
import json
import pickle
import os
from constants import *

class Instagram():

    def __init__(self):
        self.cookiejar = 'session'
        self.checkpoint_url = None
        self.in_chekpoint_mode = False

        self.id = 0
        self.profile = None
        self.posts = None
        self.stories = None

        self.set_session()

    def set_session(self):
        self.session = requests.Session()
        self.session.headers = {'user-agent': CHROME_WIN_UA}
        self.session.cookies.set('ig_pr', '1')
        self.cookies = None
        self.auth = False

    def is_auth(self):
        return self.auth

    def verify_instance(self):
        self.session.headers.update({'Referer': BASE_URL,
                                     'user-agent': STORIES_UA})

        req = self.session.get(BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
        self.session.headers.update({'user-agent': CHROME_WIN_UA})

    def login(self, username, password):
        self.session.headers.update({'Referer': BASE_URL,
                                     'user-agent': STORIES_UA})
        login_data = {'username': username,
                      'password': password}
        login = self.session.post(LOGIN_URL,
                                  data=login_data,
                                  allow_redirects=True)

        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies

        text = json.loads(login.text)

        if text.get('authenticated') and login.status_code == 200:
            self.session.headers.update({'user-agent': CHROME_WIN_UA})
            self.auth = True
            self.id = text.get('userId')
            self.save_cookies()
            return True
        else:
            if 'checkpoint_url' in text:
                self.checkpoint_url = text.get('checkpoint_url')
                self.in_chekpoint_mode = True

        return False

    def login_challenge_start(self, mode):
        self.session.headers.update({'Referer': BASE_URL})
        req = self.session.get(BASE_URL[:-1] + self.checkpoint_url)
        self.session.headers.update({
            'X-CSRFToken': req.cookies['csrftoken'],
            'X-Instagram-AJAX': '1'
        })

        self.session.headers.update({'Referer': BASE_URL[:-1] + self.checkpoint_url})
        challenge_data = {'choice': mode}
        challenge = self.session.post(
            BASE_URL[:-1] + self.checkpoint_url,
            data=challenge_data,
            allow_redirects=True
        )
        self.session.headers.update({
            'X-CSRFToken': challenge.cookies['csrftoken'],
            'X-Instagram-AJAX': '1'
        })

    def login_challenge_validate(self, code):
        code_data = {'security_code': code}
        code = self.session.post(
            BASE_URL[:-1] + self.checkpoint_url,
            data=code_data,
            allow_redirects=True
        )
        self.session.headers.update({'X-CSRFToken': code.cookies['csrftoken']})
        self.cookies = code.cookies
        code_text = json.loads(code.text)

        if code_text.get('status') == 'ok':
            self.auth = True
            self.id = code_text.get('userId')
            self.save_cookies()
            return True

        self.in_chekpoint_mode = False
        self.checkpoint_url = None

        return False

    def load_session(self):
        if self.cookiejar and os.path.exists(self.cookiejar):
            with open(self.cookiejar, 'rb') as f:
                self.session.cookies.update(pickle.load(f))
                self.auth = True
            return True
        return False

    def get_image(self, url):
        resp = self.session.get(url, cookies=self.cookies, stream=True)
        if resp.status_code == 404:
            return False
        return resp.content

    def _get(self, url):
        resp = self.session.get(url, cookies=self.cookies)

        if resp.status_code == 404:
            return False

        return json.loads(resp.text)

    def load_profile(self, username):
        self.profile = self._get(USER_URL.format(username))
        self.posts = self.profile['graphql']['user']['edge_owner_to_timeline_media']

    def load_post(self, shortcode):
        self.post = self._get(VIEW_MEDIA_URL.format(shortcode))
    
    def get_profile_attr(self, key):
        return self.profile.get('graphql')['user'][key]

    def get_posts(self):
        return self.posts

    def get_post(self):
        return self.post['items'][0]

    def save_cookies(self):
        if self.cookiejar:
            with open(self.cookiejar, 'wb') as f:
                pickle.dump(self.session.cookies, f)

