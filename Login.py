import requests, pickle, os, sys
import ddddocr
ocr = ddddocr.DdddOcr(show_ad=False)
cur_dir = os.path.split(sys.argv[0])[0]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68"}

class Login:
    def __init__(self,
                 username=None,
                 passwd=None,
                 base_url=None):
        self.__set_data(base_url, username, passwd)
        self.login()
    def __set_data(self, base_url, username, passwd):
        self.session = requests.session()
        self.base_url = base_url
        self.username = username
        self.passwd = passwd
        self.validate = None
        self.login_response = ''

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68",
            "Referer": f"{self.base_url}login.php"
        }

        self.__file_name__()
        self.__load_cookies__()

        self.data = {
            "pwuser": self.username,
            "pwpwd": self.passwd,
            "jumpurl": "index.php",
            "step": 2,
            "cktime": 31536000
        }
    def __file_name__(self):
        try:
            file_name = self.base_url.split('/')[-2].split('.')[1]
            self.cookie_file_name = os.path.join(cur_dir, 'cookies', f'{file_name}_{self.username}')
        except:
            self.cookie_file_name = os.path.join(cur_dir, 'cookies', 'default_cookie')
        print(self.cookie_file_name)
    def __load_cookies__(self):
        try:
            with open(self.cookie_file_name, 'rb') as f:
                self.session.cookies = pickle.load(f)
        except:
            pass
    def __save_cookies__(self):
        try:
            with open(self.cookie_file_name, 'wb') as f:
                pickle.dump(self.session.cookies, f)
        except:
            pass
    def __check_cookies__(self):
        response = self.session.get(url=f'{self.base_url}thread0806.php?fid=7', headers=self.headers, timeout=5)
        return True if '退出' in response.text else False
    def __login__(self):
        data = self.data.copy()
        if self.validate:
            data['validate'] = self.validate
        self.login_response = self.session.post(url=f'{self.base_url}login.php', data=data, headers=self.headers,verify=False, timeout=5)
    def __login_vali__(self):
        img_url = f"{self.base_url}require/codeimg.php"
        for _ in range(3):
            response = self.session.get(img_url, 
                                        headers=self.headers, 
                                        stream=True,
                                        timeout=5)
            if response.status_code == 200:
                break
        if response.status_code == 200:
            try:
                self.validate = ocr.classification(response.content)
                with open(os.path.join(cur_dir,'imgs','validate.png'), 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                pass
        else:
            pass
    def login(self):
        try_times = 0
        while not self.__check_cookies__():
            try_times += 1
            self.__login__()
            if self.__check_cookies__():
                self.__save_cookies__()
                break
            if '點擊顯示' in self.login_response.text:
                self.__login_vali__()
            if try_times > 3:
                break
        if self.__check_cookies__() == False:
            self.session = None
