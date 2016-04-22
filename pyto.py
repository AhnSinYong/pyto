# encoding: utf-8
from urllib.request import urlopen, Request, quote
from bs4 import BeautifulSoup
from tkinter import *
from tkinter.ttk import *
import requests, threading, re, time

DIC_CATEGORY = {
    "torrent_variety": "예능",
    "torrent_movie": "영화",
    "torrent_game": "게임",
    "torrent_mid": "해외tv",
    "torrent_song": "노래",
    "torrent_ani": "애니",
    "torrent_bluray": "고화질",
    "torrent_tv": "드라마",
    "torrent_docu": "다큐",
    "torrent_sports": "스포츠",
    "torrent_util": "유틸",
    "torrent_iphone": "모바일",
    "torrent_child": "유아/어린이",
    "torrent": "기타",
    "torrent_etc": "기타",
    "torrent_book": "도서"}

def souping(url, decode='utf-8'):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) ' \
                 'Gecko/20071127 Firefox/2.0.0.11'
    req = Request(url, headers={'User-Agent': user_agent})
    resp = urlopen(req)
    html = resp.read()
    soup = BeautifulSoup(html.decode(decode, 'ignore'), 'html.parser')
    return soup

class Torrent():
    BASE_URL = "https://torrentkim3.net"

    def __init__(self, master):
        self.root = root

        # notice frame
        self.notice_frame = Frame(self.root)
        self.notice_frame.grid(row=0, sticky=N + S + W + E)

        # notice frame / notice text
        self.notice_text = Text(self.notice_frame, height=6)
        ysb_notice_text = Scrollbar(self.notice_frame, orient='vertical', command=self.notice_text.yview)
        self.notice_text.configure(yscroll=ysb_notice_text.set)

        ysb_notice_text.pack(side=RIGHT, fill=Y)
        self.notice_text.pack(side=LEFT, fill=BOTH, expand=1)

        # get notice text from jinsyu.com
        self.notice_text.insert(END, self.get_notice()+'\n')
        self.notice_text.see("end")

        # button frame
        self.button_frame = Frame(self.root)
        self.button_frame.grid(row=1, sticky=W + E)

        # button frame / 검색어 button label
        self.search_label = Label(self.button_frame, text="검색어", width=6)
        self.search_label.pack(side=LEFT, padx=(4,0))

        # button frame / search text input entry
        self.search_entry = Entry(self.button_frame)
        self.search_entry.pack(side=LEFT, fill=X, expand=1, padx=(2,2))
        self.search_entry.bind('<Return>', self.search_torrent)
        self.search_entry.focus_set()

        # button frame / search button
        self.search_button = Button(self.button_frame, text="검색", command=self.search_torrent)
        self.search_button.pack(side=LEFT)
        
        # button frame / quit button
        self.quit_button = Button(self.button_frame, text="종료", command=root.destroy)
        self.quit_button.pack(side=LEFT)
        root.bind('<Control-Key-x>', lambda e: root.destroy())

        # hot_button_frame
        self.hot_button_frame = Frame(self.root)
        self.hot_button_frame.grid(row=2, sticky=W + E)

        # button frame / best 100 button
        self.hot_label = Label(self.hot_button_frame, text="베스트10", width=6)
        self.hot_label.pack(side=LEFT, padx=(5,0))
        self.hot_movie_button = Button(self.hot_button_frame, text="인기영화", command=lambda: self.get_hot('torrent_movie'))
        self.hot_movie_button.pack(side=LEFT, fill=X, expand=1)
        self.hot_variety_button = Button(self.hot_button_frame, text="인기예능", command=lambda: self.get_hot('torrent_variety'))
        self.hot_variety_button.pack(side=LEFT, fill=X, expand=1)
        self.hot_drama_button = Button(self.hot_button_frame, text="드라마", command=lambda: self.get_hot('torrent_tv'))
        self.hot_drama_button.pack(side=LEFT, fill=X, expand=1)
        self.hot_docu_button = Button(self.hot_button_frame, text="다큐", command=lambda: self.get_hot('torrent_docu'))
        self.hot_docu_button.pack(side=LEFT, fill=X, expand=1)
        self.hot_mid_button = Button(self.hot_button_frame, text="미드", command=lambda: self.get_hot('torrent_mid'))
        self.hot_mid_button.pack(side=LEFT, fill=X, expand=1)
        self.hot_ani_button = Button(self.hot_button_frame, text="애니", command=lambda: self.get_hot('torrent_ani'))
        self.hot_ani_button.pack(side=LEFT, fill=X, expand=1)

        # torrent_lists_frame
        self.torrent_lists_frame = Frame(self.root)
        self.torrent_lists_frame.grid(row=3, sticky=W + E + N + S)

        # torrent_lists_frame / torrent lists tree
        self.torrent_lists_tree = Treeview(self.torrent_lists_frame)
        self.ysb_torrent_lists_tree = Scrollbar(self.torrent_lists_frame, orient='vertical',
                                                    command=self.torrent_lists_tree.yview)
        self.torrent_lists_tree.configure(yscroll=self.ysb_torrent_lists_tree.set)

        self.torrent_lists_tree['columns'] = ('recommendation', 'category', 'name', 'link')

        self.torrent_lists_tree.heading("#0", text="", anchor=W)
        self.torrent_lists_tree.heading("#1", text="추천", anchor=W)
        self.torrent_lists_tree.heading("#2", text="분류", anchor=W)
        self.torrent_lists_tree.heading("#3", text="이름", anchor=W)
        self.torrent_lists_tree.heading("#4", text="링크", anchor=W)

        self.torrent_lists_tree.column("#0", width=0, stretch=0, minwidth=0)
        self.torrent_lists_tree.column("#1", width=60, stretch=0, minwidth=0)
        self.torrent_lists_tree.column("#2", width=60, stretch=0, minwidth=0)
        self.torrent_lists_tree.column("#3", stretch=1, minwidth=0)
        self.torrent_lists_tree.column("#4", width=0, stretch=0, minwidth=0)

        self.torrent_lists_tree.bind("<Double-1>", self.asyncdownload)
        self.ysb_torrent_lists_tree.pack(side=RIGHT, fill=Y)
        self.torrent_lists_tree.pack(side=LEFT, fill=BOTH, expand=1)

        # progressbar
        self.progressbar = Progressbar(orient=HORIZONTAL, length=200, mode='determinate')
        self.progressbar.grid(row=4, sticky=W + E + N + S)
        
        # grid setting to expand
        Grid.columnconfigure(root, 0, weight=1)
        Grid.rowconfigure(root, 3, weight=1)
    
    def reset_progress(self):
        time.sleep(1)
        self.setprogress(0)
    
    # insert hot article lists
    def get_hot(self, board_name):
        self.delete_torrent_lists_tree()
        self.setprogress(0)
        soup = souping("https://torrentkim3.net/bbs/popular.html")
        self.setprogress(30)
        lists = soup.findAll('a')
        hot_lists = []
        for li in lists:
            if li.get('href') and '/'+board_name+'/' in li.get('href'):
                if board_name in DIC_CATEGORY:
                    category_kor = DIC_CATEGORY[board_name]
                    bbs_name = li.get_text().strip()
                    bbs_link = li.get('href').replace('..', '')
                    hot_lists.append({'category_kor': category_kor, 'bbs_name': bbs_name, 'bbs_link': bbs_link})
        
        for index, hot_list in enumerate(hot_lists):
            self.torrent_lists_tree.insert("", 'end', hot_list['bbs_link'], values=('HOT10', 
                                                                        hot_list['category_kor'], 
                                                                        hot_list['bbs_name'], 
                                                                        hot_list['bbs_link']))
            self.setprogress(50 + index*50/10)
        self.setprogress(100)
        threading.Thread(target=self.reset_progress).start()

    def setprogress(self, progress):
        self.progressbar["value"] = progress
    
    def delete_torrent_lists_tree(self):
        for item in self.torrent_lists_tree.get_children():
            self.torrent_lists_tree.delete(item)
    
    def search_torrent(self, event=0):
        self.delete_torrent_lists_tree()
        search_text = self.search_entry.get()
        search_text = search_text.strip()
        if len(search_text) > 1:
            threading.Thread(target=self.search_torrent_kim, args=(search_text,)).start()
        else:
            self.notice_text.insert(END, "한 자 이상의 검색어를 입력하세요.\n")
            self.notice_text.see("end")
        self.search_entry.delete(0, END)

    def search_torrent_kim(self, search_text):
        url = self.BASE_URL + "/bbs/s.php?k=" + quote(search_text)

        self.setprogress(0)

        soup = souping(url)

        self.setprogress(30)

        torrent_bbs_lists = []
        for li in soup.findAll('tr', {'class': 'bg1'}):
            bbs_recommendation = li.findAll('td')[1].get_text().strip()
            bbs_link_raw = li.find('td', {'class': 'subject'})
            bbs_link = bbs_link_raw.findAll('a')[1].get('href')
            bbs_link = bbs_link.split('/')
            bbs_category = bbs_link[1]
            bbs_detail_link = bbs_link[2]
            bbs_name = bbs_link_raw.findAll('a')[1].get_text().strip()

            if bbs_category in DIC_CATEGORY:
                bbs_category_korean = DIC_CATEGORY.get(bbs_category)
            else:
                bbs_category_korean = "N/A"

            torrent_bbs_lists.append({
                'bbs_recommendation': bbs_recommendation,
                'eng_category': bbs_category,
                'korean_category': bbs_category_korean,
                'bbs_detail_link': bbs_detail_link,
                'bbs_name': bbs_name
            })

        self.setprogress(50)

        # delete duplicate dictionary list
        torrent_bbs_lists = list({v['bbs_detail_link']: v for v in torrent_bbs_lists}.values())

        torrent_bbs_lists_size = len(torrent_bbs_lists)

        if torrent_bbs_lists_size > 0:
            self.notice_text.insert(END, "\"" + search_text + "\" 검색 결과 총 " + str(
                torrent_bbs_lists_size) + " 개의 토렌트가 검색되었습니다.\n")
            self.notice_text.see("end")

            for index, torrent_bbs_list in enumerate(torrent_bbs_lists):
                self.torrent_lists_tree.insert("", 'end',
                                               '/' + torrent_bbs_list['eng_category'] + '/' + torrent_bbs_list[
                                                   'bbs_detail_link'],
                                               values=(torrent_bbs_list['bbs_recommendation'],
                                                       torrent_bbs_list['korean_category'],
                                                       torrent_bbs_list['bbs_name'],
                                                       torrent_bbs_list['bbs_detail_link']))

                self.setprogress(50 + index*50/torrent_bbs_lists_size)

        else:
            self.notice_text.insert(END, "There's no result for \"" + search_text + "\"\n")
            self.notice_text.see("end")

        self.setprogress(100)
        threading.Thread(target=self.reset_progress).start()

    def asyncdownload(self, event):
        url = self.BASE_URL + self.torrent_lists_tree.focus()
        threading.Thread(target=self.down_torrent_kim, args=(url,)).start()

    def down_torrent_kim(self, url):
        try:
            self.setprogress(0)

            soup = souping(url)

            if len(soup) > 50:
                self.setprogress(10)
                   

                for post in soup.findAll('span', {'style': 'color:#888;'}):

                    torrent_name = post.contents[0]
                    torrent_link = self.BASE_URL + post.parent.get('href')

                    if 'torrent' in torrent_name[-10:]:
                        torrent_name = torrent_name[:-2]

                    elif 'smi' in torrent_name[-15:]:
                        torrent_name = re.sub(r'\(\d+\.\dK\)', '', torrent_name).rstrip()
                        torrent_link = self.BASE_URL + re.search(r'\'(/bbs.+?)\'', torrent_link).group(1)

                    elif 'srt' in torrent_name[-15:]:
                        torrent_name = re.sub(r'\(\d+\.\dK\)', '', torrent_name).rstrip()
                        torrent_link = self.BASE_URL + re.search(r'\'(/bbs.+?)\'', torrent_link).group(1)

                    else:
                        self.setprogress(0)
                        self.notice_text.insert(END, "토렌트 링크가 존재하지 않습니다.\n")
                        self.notice_text.see("end")
                        return

                    # 특수문자 포함시 오류가 나서 파일 이름에서 제거함
                    torrent_name = torrent_name.replace("'", "")
                    torrent_name = torrent_name.replace("\\", "")

                    r = requests.get(torrent_link, stream=True, headers={'referer': url})


                    size = float(r.headers['content-length']) / 1024.0

                    with open(torrent_name, 'wb') as f:
                        chunks = enumerate(r.iter_content(chunk_size=1024))
                        for index, chunk in chunks:
                            if chunk:
                                self.setprogress(10.0 + index*90.0/size)
                                f.write(chunk)
                                f.flush()

                    is_file = os.path.exists(torrent_name)

                    self.notice_text.insert(END, "다운완료: " + torrent_name + "\n")
                    self.notice_text.see("end")
                    
                    self.setprogress(100)
                    threading.Thread(target=self.reset_progress).start()
            
            else:
                self.setprogress(0)
                self.notice_text.insert(END, "삭제된 자료거나, 올바르지 않은 링크입니다. 다른 자료를 이용하세요.\n")
                self.notice_text.see("end")

        except Exception as e:
            self.notice_text.insert(END, "다운로드 과정에 오류가 발생했습니다 (error: " + str(e) + "). 관리자에게 문의하세요.\n")
            self.notice_text.see("end")

    def get_notice(self):
        url = "http://jinsyu.com/python/pyto/notice"
        notice_text = urlopen(url).read().decode('utf-8')
        return notice_text

if __name__ == "__main__":
    root = Tk()
    root.title('Pyto V1.1')
    root.geometry('650x600+200+100')
    # root.resizable(width=FALSE, height=FALSE)
    torrent = Torrent(root)
    root.mainloop()
