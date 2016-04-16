# -*- encode: utf-8 -*-
from urllib.request import urlopen, Request, quote
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import ttk
import requests

def souping(url, decode='utf-8'):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) ' \
        'Gecko/20071127 Firefox/2.0.0.11'
    req = Request(url, headers={'User-Agent': user_agent})
    resp = urlopen(req)
    html = resp.read()
    soup = BeautifulSoup(html.decode(decode,'ignore'), 'html.parser')
    return soup

class Torrent():
    def __init__(self, master):
        self.base_url = "https://torrentkim3.net"
        # top notice frame
        # self.notice_frame = Frame(root, height=3)
        # self.notice_frame.pack(side=TOP, fill=X, expand=1)

        # ## scrollbar
        # self.s_notice_text = Scrollbar(self.notice_frame)
        # self.s_notice_text.pack(side=RIGHT, fill=Y)
        
        ## noti 
        self.notice_frame = Frame(root)
        self.notice_frame.grid(row=0, sticky=N+S+W+E)

        self.notice_text = Text(self.notice_frame, height=6)
        ysb_notice_text = ttk.Scrollbar(self.notice_frame, orient='vertical', command=self.notice_text.yview)
        self.notice_text.configure(yscroll=ysb_notice_text.set)

        self.notice_text.pack(side=LEFT, fill=BOTH, expand=YES)
        ysb_notice_text.pack(side=LEFT, fill=Y)

        # # self.notice_text.config(self.notice_frame, yscrollcommand=self.s_notice_text.set)
        # self.s_notice_text.config(command=self.notice_text.yview)
        
        self.notice_text.insert(INSERT, self.get_notice())

        # button frame
        self.button_frame = Frame(root)
        self.button_frame.grid(row=1, sticky="we") 

        self.search_label = Label(self.button_frame, text="검색어")
        self.search_label.pack(side=LEFT)

        self.search_entry = Entry(self.button_frame)
        self.search_entry.pack(side=LEFT, fill=X, expand=1)
        self.search_entry.bind('<Return>', self.search_torrent)
        self.search_entry.focus_set()

        self.search_button = Button(self.button_frame, text="Search torrent", command=self.search_torrent)
        self.search_button.pack(side=LEFT)

        self.quit_button = Button(self.button_frame, text="Exit", command=root.quit)
        self.quit_button.pack(side=LEFT)
        # root.bind('<Control-Key-x>', exit)

        # torrent_lists_frame
        self.torrent_lists_frame = Frame(root, height=100)
        self.torrent_lists_frame.grid(row=2, sticky=W+E+N+S)

        # grid setting to expand
        Grid.columnconfigure(root, 0, weight=1) 
        Grid.columnconfigure(self.button_frame, 1, weight=1)
        Grid.columnconfigure(self.torrent_lists_frame, 2, weight=1)

    def exit(self, event=0):
        self.root.quit 

    def search_torrent(self, event=0):
        for w in self.torrent_lists_frame.winfo_children():
            w.destroy()

        search_text = self.search_entry.get()
        search_text = search_text.strip()
        if len(search_text) > 1:
            self.search_torrent_kim(search_text)
        else: 
            self.notice_text.insert(0.0, "Please Insert a word or phrase.\n")
        self.search_entry.delete(0, END)

    def search_torrent_kim(self, search_text):
        url = self.base_url+"/bbs/s.php?k="+quote(search_text)
        soup = souping(url)

        torrent_bbs_lists = []
        for li in soup.findAll('tr', {'class':'bg1'}):
            bbs_recommendation = li.findAll('td')[1].get_text().strip()
            bbs_link_raw = li.find('td', {'class': 'subject'})
            bbs_link = bbs_link_raw.findAll('a')[1].get('href')
            bbs_link = bbs_link.split('/')
            bbs_category = bbs_link[1]
            bbs_detail_link = bbs_link[2]
            bbs_name = bbs_link_raw.findAll('a')[1].get_text().strip()

            if bbs_category == "torrent_variety":
                bbs_category_korean = "예능"
            elif bbs_category == "torrent_movie":
                bbs_category_korean = "영화"
            elif bbs_category == "torrent_game":
                bbs_category_korean = "게임"
            elif bbs_category == "torrent_mid":
                bbs_category_korean = "해외tv"
            elif bbs_category == "torrent_song":
                bbs_category_korean = "노래"
            elif bbs_category == "torrent_ani":
                bbs_category_korean = "애니"  
            elif bbs_category == "torrent_bluray":
                bbs_category_korean = "고화질"  
            elif bbs_category == "torrent_tv":
                bbs_category_korean = "드라마"
            elif bbs_category == "torrent_docu":
                bbs_category_korean = "다큐"
            elif bbs_category == "torrent_sports":
                bbs_category_korean = "스포츠"
            elif bbs_category == "torrent_util":
                bbs_category_korean = "유틸"
            elif bbs_category == "torrent_iphone":
                bbs_category_korean = "모바일"    
            elif bbs_category == "torrent_child":
                bbs_category_korean = "유아/어린이"    
            elif bbs_category == "torrent" or bbs_category == "torrent_etc":
                bbs_category_korean = "기타"    
            elif bbs_category == "torrent_book":
                bbs_category_korean = "도서"    
            else:
                bbs_category_korean = "정체불명"  

            torrent_bbs_lists.append({
                'bbs_recommendation': bbs_recommendation, 
                'eng_category': bbs_category, 
                'korean_category': bbs_category_korean, 
                'bbs_detail_link' : bbs_detail_link, 
                'bbs_name': bbs_name
                })

        # delete duplicate dictionary list
        torrent_bbs_lists = list({v['bbs_detail_link']: v for v in torrent_bbs_lists}.values())

        torrent_bbs_lists_size = len(torrent_bbs_lists)
        if torrent_bbs_lists_size > 0:
            self.notice_text.insert(0.0, "There are "+str(torrent_bbs_lists_size)+" results related \""+search_text+"\"\n")
           
            self.torrent_lists_tree = ttk.Treeview(self.torrent_lists_frame, height=100)
            ysb_torrent_lists_tree = ttk.Scrollbar(self.torrent_lists_frame, orient='vertical', command=self.torrent_lists_tree.yview)
            self.torrent_lists_tree.configure(yscroll=ysb_torrent_lists_tree.set)


            self.torrent_lists_tree['columns'] = ('recommendation', 'category', 'name', 'link')

            self.torrent_lists_tree.heading("#0", text="", anchor=W)
            self.torrent_lists_tree.heading("#1", text="추천", anchor=W)
            self.torrent_lists_tree.heading("#2", text="분류", anchor=W)
            self.torrent_lists_tree.heading("#3", text="이름", anchor=W)
            self.torrent_lists_tree.heading("#4", text="링크", anchor=W)
            
            self.torrent_lists_tree.column("#0",width=0, stretch=0, minwidth=0)
            self.torrent_lists_tree.column("#1", width=60, stretch=0, minwidth=0)
            self.torrent_lists_tree.column("#2", width=60, stretch=0, minwidth=0)
            self.torrent_lists_tree.column("#3", stretch=1, minwidth=0)
            self.torrent_lists_tree.column("#4", width=0, stretch=0, minwidth=0)

            for torrent_bbs_list in torrent_bbs_lists:
                self.torrent_lists_tree.insert("", 'end', '/'+torrent_bbs_list['eng_category']+'/'+torrent_bbs_list['bbs_detail_link'], 
                    values=(torrent_bbs_list['bbs_recommendation'], 
                            torrent_bbs_list['korean_category'], 
                            torrent_bbs_list['bbs_name'], 
                            torrent_bbs_list['bbs_detail_link']))
                # self.bbs_link_button = Button(
                #     self.torrent_lists_frame, 
                #     text='('+torrent_bbs_list['korean_category']+') '+torrent_bbs_list['bbs_name'], 
                #     command=lambda torrent_bbs_list=torrent_bbs_list: self.down_torrent_kim(torrent_bbs_list['eng_category'], torrent_bbs_list['bbs_detail_link']), 
                #     anchor=W)
                # self.bbs_link_button.pack(side=TOP, fill=BOTH, expand=1) 
            self.torrent_lists_tree.bind("<Double-1>", self.down_torrent_kim)
            self.torrent_lists_tree.pack(side=LEFT, fill=BOTH, expand=YES)
            ysb_torrent_lists_tree.pack(side=LEFT, fill=Y)

        else:
            self.notice_text.insert(0.0, "There is a no result for \""+search_text+"\"\n")

    def down_torrent_kim(self, event):
        self.base_url = "https://torrentkim3.net"
        url = self.base_url+self.torrent_lists_tree.focus()
        soup = souping(url)

        try:
            for post in soup.findAll('span',{'style':'color:#888;'}):
                torrent_name = post.contents[0]
                torrent_link = self.base_url+post.parent.get('href')

                if 'torrent' in torrent_name[-10:]:
                    torrent_name = torrent_name[:-2]

                elif 'smi' in torrent_name[-15:]:
                    torrent_name = re.sub(r'\(\d+\.\dK\)','',torrent_name).rstrip()
                    torrent_link = baseself.base_url_url+re.search(r'\'(/bbs.+?)\'', torrent_link).group(1)

                elif 'srt' in torrent_name[-15:]:
                    torrent_name = re.sub(r'\(\d+\.\dK\)','',torrent_name).rstrip()
                    torrent_link = self.base_url+re.search(r'\'(/bbs.+?)\'', torrent_link).group(1)

                r = requests.get(torrent_link, stream=True, headers={'referer': url})

                with open(torrent_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()

                self.notice_text.insert(0.0, "다운완료: " + torrent_name+"\n")
            
        except Exception as e:
            self.notice_text.insert(INSERT, e)

    def get_notice(self):
        url = "http://jinsyu.com/python/pyto/notice"
        notice_text = urlopen(url).read().decode('utf-8')
        return notice_text

root = Tk()
root.title('Pyto V1.0')
root.geometry('650x600+200+100')
# root.resizable(width=FALSE, height=FALSE)
torrent = Torrent(root)
root.mainloop()    
