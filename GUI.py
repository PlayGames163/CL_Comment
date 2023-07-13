import os, sys, random, requests, pickle, re
from tkinter import *
from tkinter.filedialog import *
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

class Window:
    def __init__(self):
        self.window= Tk()
        self.window.title('小草自动评论')
        self.window.config(background = "whitesmoke")
        self.__base_data()  # 基础数据
        self.__get_base_info()  # 基础文件信息

        self.window.mainloop()
    def __base_data(self):
        # 基础数据
        self.web_info_file = StringVar()
        self.web_info_file.set(os.sep.join([cur_dir, 'data', 'web']))
        self.user_info_file = StringVar()
        self.user_info_file.set(os.sep.join([cur_dir, 'data', 'user_info']))
        self.comment_content_file = StringVar()
        self.comment_content_file.set(os.sep.join([cur_dir, 'data', 'comment_content']))

        self.commented_file = StringVar()
        self.commented_file.set(os.sep.join([cur_dir, 'data', 'commented']))
        self.to_comment_info_file = StringVar()
        self.to_comment_info_file.set(os.sep.join([cur_dir, 'data', 'to_comment']))
        self.to_comment_url = StringVar()

        self.web_info = self.__read_content(self.web_info_file)
        self.user_info = self.__read_content(self.user_info_file)
        self.comment_content = self.__read_content(self.comment_content_file)
        self.commented_info = self.__read_content(self.commented_file)
        self.to_comment_info = self.__read_content(self.to_comment_info_file)
        self.to_comment_info = [x.split('\t') for x in self.to_comment_info]
        self.to_comment_url.set(self.to_comment_info[0][1] if len(self.to_comment_info) else '')

    def __get_base_info(self):
        self.__web_window()
        self.__comment_content_window()
        self.__user_window()
        self.__commented_window()
        self.__to_comment_window()
        self.__comment_window()

    def __comment_window(self):
        Message(self.window, textvariable=StringVar(value='评论链接'), width=400, background = "whitesmoke").grid(row=12, column=1)
        Message(self.window, textvariable=self.to_comment_url, width=400, background = "whitesmoke").grid(row=12, column=2)
        Button(self.window, text='评论', command=self.__comment).grid(row=12, column=4)
    
    def __comment(self):
        reply_url = f"{self.base_url}post.php"
        comment_content = random.choice(self.comment_content)
        tid, url_path, title = tuple(self.to_comment_info[0])
        reply_data = {
            "atc_money": 0,
            "atc_rvrc": 0,
            "atc_title": f"Re:{title}",
            "atc_usesign": 1,
            "atc_convert": 1,
            "atc_autourl": 1,
            "atc_content": f"{comment_content}",
            "step": 2,
            "action": "reply",
            "verify": "verify",
            "fid": 7,
            "tid": tid,
            "editor": 0,
        }
        try:
            resp = self.login.session.post(url=reply_url, data=reply_data, headers=headers, timeout=10)
            if '發貼完畢點擊進入主題列表' in resp.text:
                self.commented_info.append(tid)
                self.to_comment_info = self.to_comment_info[1:]
                with open(self.commented_file.get(), 'w', encoding='utf-8') as f:
                    for t in self.commented_info:
                        f.write(f'{t}\n')
                with open(self.to_comment_info_file.get(), 'w', encoding='utf-8') as f:
                    for data_lst in self.to_comment_info:
                        data_save = '\t'.join(data_lst)
                        if data_lst[0] not in self.commented_info and 'font color' not in data_save and '禁言' not in data_save and '灌水' not in data_save and '大乐透' not in data_save:
                            f.write(f"{data_save}\n")
                self.commented_msg.set(f'已经评价数量: {len(self.commented_info)}')
                self.to_comment_msg.set(f'可以评价数量: {len(self.to_comment_info)}')
                print(f'评论成功: {comment_content} {title} {f"{self.base_url}{url_path}"}')
            else:
                print(resp.text)
        except:
            print(resp.text)
        
    def __to_comment_window(self):
        Message(self.window, textvariable=StringVar(value='可以评论链接'), width=400, background = "whitesmoke").grid(row=9, column=1)
        Entry(self.window, width=35, textvariable=self.to_comment_info_file).grid(row=9, column=2, columnspan=2)
        Button(self.window, text='打开文件', command=self.__read_to_comment_info).grid(row=9, column=4)

        self.to_comment_msg = StringVar()
        self.to_comment_msg.set(f'可以评价数量: {len(self.to_comment_info)}')
        Message(self.window, textvariable=self.to_comment_msg,width=400, background = "whitesmoke").grid(row=10, column=1, columnspan=3)
        Button(self.window, text='更新', command=self.__update_to_comment).grid(row=10, column=4)
    def __update_to_comment(self):
        comment_url = f'https://cl.{random.choice(self.web_info)}{random.choice("xyz")}.xyz/thread0806.php?fid=7'
        session = requests.session()
        response = session.get(url=comment_url, headers=headers, timeout=5)
        all_pattern = r'<a href="htm_data/(\d+)/7/(\d+)\.html" target="_blank" id="(.+)">(.+)</a>'
        pattern_match = re.findall(all_pattern, response.text)
        num = 0
        with open(self.to_comment_info_file.get(), 'w', encoding='utf-8') as f:
            for d, tid, _, title in pattern_match:
                if tid not in self.commented_info and 'font color' not in title and '禁言' not in title and '灌水' not in title and '大乐透' not in title:
                    num += 1
                    content = [tid,f"htm_data/{d}/7/{tid}.html", title]
                    self.to_comment_info.append(content)
                    content = '\t'.join(content)
                    f.write(f"{content}\n")
        print(f'一共有: {num}条更新')
        self.to_comment_msg.set(f'可以评价数量: {len(self.to_comment_info)}')
        # print(self.to_comment_info)

    def __commented_window(self):
        Message(self.window, textvariable=StringVar(value='已经评论'), width=400, background = "whitesmoke").grid(row=7, column=1)
        Entry(self.window, width=35, textvariable=self.commented_file).grid(row=7, column=2, columnspan=2)
        Button(self.window, text='打开文件', command=self.__read_commented_info).grid(row=7, column=4)

        self.commented_msg = StringVar()
        self.commented_msg.set(f'已经评价数量: {len(self.commented_info)}')
        Message(self.window, textvariable=self.commented_msg,width=400, background = "whitesmoke").grid(row=8, column=1, columnspan=3)
        Button(self.window, text='更新', command=self.__update_commented).grid(row=8, column=4)
    def __update_commented(self):
        commented_tids = set()
        commented_url = f"{self.base_url}personal.php?action=post"
        resp = self.login.session.get(url = commented_url, headers=headers)
        pattern = r"this.value='(\d+)/(\d+)'"
        match_content = re.search(pattern, resp.text)
        _, page_num = match_content.group(1), match_content.group(2)
        pattern = r'<a href="read.php\?tid=(\d+)&pid=(\d+)" target="_blank" class="a2">'
        for i in range(1, int(page_num)+1):
            url = f'{self.base_url}personal.php?action=post&page={i}'
            resp = self.login.session.get(url = url, headers=headers)
            match_content = re.findall(pattern, resp.text)
            print(f'{i}/{page_num}: {len(match_content)}')
            for tid, _ in match_content:
                commented_tids.add(tid)
        with open(self.commented_file.get(), 'w', encoding='utf-8') as f:
            for tid in commented_tids:
                f.write(f'{tid}\n')
        self.commented_info = list(commented_tids)
        self.commented_msg.set(f'已经评价数量: {len(commented_tids)}')

    def __user_window(self):
        Message(self.window, textvariable=StringVar(value='用户信息'), width=400, background = "whitesmoke").grid(row=5, column=1)
        Entry(self.window, width=35, textvariable=self.user_info_file).grid(row=5, column=2, columnspan=2)
        Button(self.window, text='打开文件', command=self.__read_user_info).grid(row=5, column=4)

        self.user_name_msg = StringVar()
        self.user_passwd_msg = StringVar()
        user_name = self.user_info[0] if len(self.user_info)>=2 else ''
        self.user_name_msg.set(user_name)
        user_passwd = self.user_info[1] if len(self.user_info)>=2 else ''
        self.user_passwd_msg.set(user_passwd)
        Entry(self.window, textvariable=self.user_name_msg, width=10).grid(row=6, column=1)
        Entry(self.window, textvariable=self.user_passwd_msg, width=10).grid(row=6, column=2)
        Button(self.window, text='修改', command=self.__change_user_info).grid(row=6, column=3)
        Button(self.window, text='登录', command=self.__login).grid(row=6, column=4)
    def __login(self):
        self.base_url = f'https://cl.{random.choice(self.web_info)}{random.choice("xyz")}.xyz/'
        self.login = Login(self.user_name_msg.get(), self.user_passwd_msg.get(), self.base_url)
    def __change_user_info(self):
        self.user_info = [self.user_name_msg.get(), self.user_passwd_msg.get()]
        self.__write(self.user_info, self.user_info_file.get())

    def __web_window(self):
        Message(self.window, textvariable=StringVar(value='网站信息'), width=400, background = "whitesmoke").grid(row=1, column=1)
        Entry(self.window, width=35, textvariable=self.web_info_file).grid(row=1, column=2, columnspan=2)
        Button(self.window, text='打开文件', command=self.__read_web_info).grid(row=1, column=4)

        self.web_info_msg = StringVar()
        self.web_info_msg.set(', '.join(self.web_info))
        Message(self.window, textvariable=self.web_info_msg, width=400, background = "whitesmoke").grid(row=2, column=1)
        self.web_input_window = Text(self.window, width=10, height=1)
        self.web_input_window.grid(row=2, column=2)
        Button(self.window, text='删除网站', command=self.__delete_web).grid(row=2, column=3)
        Button(self.window, text='加入网站', command=self.__add_web).grid(row=2, column=4)
        self.base_url = f'https://cl.{random.choice(self.web_info)}{random.choice("xyz")}.xyz/'
    def __delete_web(self):
        new_input = [x.strip() for x in self.web_input_window.get('0.0', 'end').split('\n')]
        for n in new_input:
            if n in self.web_info:
                self.web_info.remove(n)
                self.web_info_msg.set(', '.join(self.web_info))
        self.__write(self.web_info, self.web_info_file.get())
        self.web_input_window.delete('0.0', 'end')
    def __add_web(self):
        new_input = [x.strip() for x in self.web_input_window.get('0.0', 'end').split('\n')]
        for n in new_input:
            if n not in self.web_info:
                self.web_info.append(n)
                self.web_info_msg.set(', '.join(self.web_info))
        self.__write(self.web_info, self.web_info_file.get())
        self.web_input_window.delete('0.0', 'end')

    def __comment_content_window(self):
        Message(self.window, textvariable=StringVar(value='评论内容'), width=400, background = "whitesmoke").grid(row=3, column=1)
        Entry(self.window, width=35, textvariable=self.comment_content_file).grid(row=3, column=2, columnspan=2)
        Button(self.window, text='打开文件', command=self.__read_comment_content_info).grid(row=3, column=4)

        self.comment_content_msg = StringVar()
        self.comment_content_msg.set('\n'.join(self.comment_content))
        Message(self.window, textvariable=self.comment_content_msg, width=400, background = "whitesmoke").grid(row=4, column=1)
        self.comment_content_input_window = Text(self.window, width=10, height=1)
        self.comment_content_input_window.grid(row=4, column=2)
        Button(self.window, text='删除评论', command=self.__delete_comment_content).grid(row=4, column=3)
        Button(self.window, text='加入评论', command=self.__add_comment_content).grid(row=4, column=4)
    def __delete_comment_content(self):
        new_input = [x.strip() for x in self.comment_content_input_window.get('0.0', 'end').split('\n')]
        for n in new_input:
            if n in self.comment_content:
                self.comment_content.remove(n)
                self.comment_content_msg.set('\n'.join(self.comment_content))
        self.__write(self.comment_content, self.comment_content_file.get())
        self.comment_content_input_window.delete('0.0', 'end')
    def __add_comment_content(self):
        new_input = [x.strip() for x in self.comment_content_input_window.get('0.0', 'end').split('\n')]
        for n in new_input:
            if n not in self.comment_content:
                self.comment_content.append(n)
                self.comment_content_msg.set('\n'.join(self.comment_content))
        self.__write(self.comment_content, self.comment_content_file.get())
        self.comment_content_input_window.delete('0.0', 'end')

    def __write(self, content, file):
        with open(file, 'w', encoding='utf-8') as f:
            for n in content:
                f.write(f'{n}\n')
    def __read_file(self, info_file:StringVar, path_name: str):
        file_path = askopenfilename(initialdir=os.sep.join([cur_dir, 'data', path_name]))
        info_file.set(file_path)
        return self.__read_content(info_file)
    def __read_content(self, file_name: StringVar):
        print(file_name.get())
        file_content = []
        try:
            with open(file_name.get(), 'r', encoding='utf-8') as f:
                file_content = [x.strip() for x in f.readlines() if len(x.strip())>1]
        except Exception as exc:
            print(f'{exc}')
        return file_content

    def __read_web_info(self):
        self.web_info = self.__read_file(self.web_info_file, 'web')
    def __read_user_info(self):
        self.user_info = self.__read_file(self.user_info_file, 'user_info')
    def __read_comment_content_info(self):
        self.comment_content = self.__read_file(self.comment_content_file, 'comment_content')
    def __read_commented_info(self):
        self.commented_info = self.__read_file(self.commented_file, 'commented')
        if not self.commented_info:
            self.__update_commented()
    def __read_to_comment_info(self):
        self.to_comment_info = self.__read_file(self.to_comment_info_file, 'to_comment')
        self.to_comment_info = [x.split('\t') for x in self.to_comment_info]


if __name__ == '__main__':
    Window()
