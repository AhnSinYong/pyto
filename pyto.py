# encoding: utf-8
from urllib.request import urlopen, Request, quote
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import ttk
import requests, threading

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
        ysb_notice_text = ttk.Scrollbar(self.notice_frame, orient='vertical', command=self.notice_text.yview)
        self.notice_text.configure(yscroll=ysb_notice_text.set)

        self.notice_text.pack(side=LEFT, fill=BOTH, expand=YES)
        ysb_notice_text.pack(side=LEFT, fill=Y)

        # get notice text from jinsyu.com
        self.notice_text.insert(INSERT, self.get_notice())

        # button frame
        self.button_frame = Frame(self.root)
        self.button_frame.grid(row=1, sticky=W + E)

        # button frame / 검색어 button label
        self.search_label = Label(self.button_frame, text="검색어")
        self.search_label.pack(side=LEFT)

        # button frame / search text input entry
        self.search_entry = Entry(self.button_frame)
        self.search_entry.pack(side=LEFT, fill=X, expand=1)
        self.search_entry.bind('<Return>', self.search_torrent)
        self.search_entry.focus_set()

        # button frame / search button
        self.search_button = Button(self.button_frame, text="Search torrent", command=self.search_torrent)
        self.search_button.pack(side=LEFT)

        # button frame / quit button
        self.quit_button = Button(self.button_frame, text="Exit", command=root.quit)
        self.quit_button.pack(side=LEFT)
        # root.bind('<Control-Key-x>', exit)

        # progressbar
        self.progressbar = ttk.Progressbar(orient=HORIZONTAL, length=200, mode='determinate')
        self.progressbar.grid(row=2, sticky=W + E + N + S)

        # torrent_lists_frame
        self.torrent_lists_frame = Frame(root, height=100)
        self.torrent_lists_frame.grid(row=3, sticky=W + E + N + S)

        # torrent_lists_frame / torrent lists tree
        self.torrent_lists_tree = ttk.Treeview(self.torrent_lists_frame, height=100)
        self.ysb_torrent_lists_tree = ttk.Scrollbar(self.torrent_lists_frame, orient='vertical',
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
        self.torrent_lists_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        self.ysb_torrent_lists_tree.pack(side=LEFT, fill=Y)

        # grid setting to expand
        Grid.columnconfigure(root, 0, weight=1)
        Grid.columnconfigure(self.button_frame, 1, weight=1)
        Grid.columnconfigure(self.torrent_lists_frame, 2, weight=1)

    def exit(self, event=0):
        self.root.quit()

    def setprogress(self, progress):
        self.progressbar["value"] = progress

    def search_torrent(self, event=0):
        for item in self.torrent_lists_tree.get_children():
            self.torrent_lists_tree.delete(item)

        search_text = self.search_entry.get()
        search_text = search_text.strip()
        if len(search_text) > 1:
            threading.Thread(target=self.search_torrent_kim, args=(search_text,)).start()
        else:
            self.notice_text.insert(0.0, "Please Insert a word or phrase.\n")
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
            self.notice_text.insert(0.0, "There are " + str(
                torrent_bbs_lists_size) + " results related \"" + search_text + "\"\n")

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
            self.notice_text.insert(0.0, "There's no result for \"" + search_text + "\"\n")

        self.setprogress(100)

    def asyncdownload(self, event):
        url = self.BASE_URL + self.torrent_lists_tree.focus()
        threading.Thread(target=self.down_torrent_kim, args=(url,)).start()

    def down_torrent_kim(self, url):
        self.setprogress(0)

        soup = souping(url)

        self.setprogress(10)

        try:
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

                r = requests.get(torrent_link, stream=True, headers={'referer': url})

                size = float(r.headers['content-length']) / 1024.0

                with open(torrent_name, 'wb') as f:
                    chunks = enumerate(r.iter_content(chunk_size=1024))
                    for index, chunk in chunks:
                        if chunk:
                            self.setprogress(10.0 + index*90.0/size)
                            f.write(chunk)
                            f.flush()

                self.notice_text.insert(0.0, "다운완료: " + torrent_name + "\n")

                self.setprogress(100)

        except Exception as e:
            self.notice_text.insert(INSERT, e)

    def get_notice():
        url = "http://jinsyu.com/python/pyto/notice"
        notice_text = urlopen(url).read().decode('utf-8')
        return notice_text

if __name__ == "__main__":
    root = Tk()
    root.title('Pyto V1.0')
    root.geometry('650x600+200+100')
    # root.resizable(width=FALSE, height=FALSE)
    torrent = Torrent(root)
    root.mainloop()
