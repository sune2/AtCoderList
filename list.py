#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import cookielib
import getpass
import sys
import lxml.html
import collections
from Cheetah.Template import Template

class ProblemResult:
    def __init__(self):
        self.dic = collections.defaultdict(int)

    def update(self, pid, res):
        if self.dic[pid] < res:
            self.dic[pid] = res

    def update_pres(self, pres):
        for key, val in pres.dic.items():
            self.update(key, val)

    def __getitem__(self, idx):
        return self.dic[idx]

    def __len__(self):
        return len(self.dic)

colors = ['#ffffff', '#ffe3e3', 'lightyellow', '#d4edc9']

class Problem:
    def __init__(self, pid, name, url):
        self.pid = pid
        self.name = name
        self.url = url
        self.result = 0
        self.color = ""

    def set_result(self, res):
        self.result = res
        self.color = colors[res]

class AtCoder:
    def __init__(self):
        name = raw_input("Name: ")
        pswd = getpass.getpass()
        self.opener = urllib2.build_opener()
        self.opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        url = 'https://abc019.contest.atcoder.jp/login'
        self.opener.open(urllib2.Request(url, 'name=%s&password=%s' % (name, pswd)))

    def result_with_page(self, url, page):
        url = '%s/submissions/me/%d' % (url, page)
        conn = self.opener.open(urllib2.Request(url))
        res = conn.read()
        print url, res
        dom = lxml.html.fromstring(res)
        pres = ProblemResult()
        for row in dom.xpath('//tbody/tr'):
            texts = []
            for a in row.xpath('td'):
                texts.append(a.text_content())
            pid = texts[1][0]
            if texts[4] == "AC":
                pres.update(pid, 3)
            else:
                if texts[3] != "0":
                    pres.update(pid, 2)
                else:
                    pres.update(pid, 1)
        return pres

    def result_with_url(self, url):
        pres = ProblemResult()
        for i in range(100):
            t = self.result_with_page(url, i+1)
            if len(t) == 0: break
            pres.update_pres(t)
        return pres

    def problems_with_url(self, url):
        aurl = '%s/assignments' % (url)
        conn = self.opener.open(urllib2.Request(aurl))
        res = conn.read()
        dom = lxml.html.fromstring(res)
        problems = []
        for row in dom.xpath('//tr'):
            texts = []
            for a in row.xpath('td'):
                texts.append(a.text_content())
            if len(texts) >= 2:
                purl = url + row.xpath('td/a')[0].attrib['href']
                problems.append(Problem(texts[0], texts[1], purl))
        name_cand = dom.xpath('//span[@class="contest-name"]')
        if len(name_cand) > 0:
            name = name_cand[0].text
        else:
            name = None
        return name, problems

    def get_list(self, url):
        name, problems = self.problems_with_url(url)
        pres = self.result_with_url(url)
        for i,p  in enumerate(problems):
            problems[i].set_result(pres[p.pid])
        return name, problems

    def get_all_list(self):
        url = 'http://atcoder.jp/'
        dom = lxml.html.fromstring(urllib2.urlopen(url).read())
        contests = []
        for a in dom.xpath('//a'):
            contest_url = a.attrib['href']
            if 'contest.atcoder.jp' not in contest_url: continue
            if contest_url[-1] == '/': contest_url = contest_url[:-1]
            name, problems = self.get_list(contest_url)
            if name == None: continue
            print name
            contests.append({"name" : name, "url" : contest_url, "problems" : problems})
        return contests

    def run(self):
        contests = self.get_all_list()
        tmpl = Template(file = "list.tmpl")
        tmpl.contests = contests
        f = open("list.html", "w")
        f.write(str(tmpl))

def main():
    atcoder = AtCoder()
    atcoder.result_with_page("http://jag2013autumn.contest.atcoder.jp/", 1)
    # atcoder.run()

main()
