import requests
import threading
import lxml.html as lh
import Queue
import sys
import csv
import random

def wait2write():

    while not urlq.empty():
        book_url = urlq.get()
        try:
            headers = {
                'User-Agent' : random.choice(ua)
            }
            url = requests.get(book_url, headers=headers)
        except:
            sys.exit("[*] " + url + " cannot been downloaded.")
        else:
            html = url.text

        tree = lh.fromstring(html)

        try:
            book_name = tree.cssselect('span[property="v:itemreviewed"]')[0].text.strip().encode('utf-8')
        except:
            book_name = '**'
        try:
            author = tree.cssselect('span.pl')[0].getnext().text.strip().encode('utf-8')
        except:
            author = '**'
        try:
            rating_nums = tree.find_class('ll rating_num')[0].text.strip()
        except:
            rating_nums = 0
        try:
            voting_nums = tree.cssselect('span[property="v:votes"]')[0].text.strip()
        except:
            voting_nums = 0
        star5, star4, star3, star2, star1 = [ e.text.strip() for e in tree.cssselect('span.rating_per') ] if voting_nums else [0] * 5
        t = [book_name, author, book_url, rating_nums, voting_nums, star5, star4, star3, star2, star1]
        bookq.put(t)
        print '[*] %{book_url} has been saved!'.format(book_url=book_url)

def write2csv():
    with open('book.csv', 'w') as f:
        csvfile = csv.writer(f)
        csvfile.writerow(['book_name', 'author', 'book_url', 'rating_nums', 'voting_nums', 'star5', 'star4', 'star3', 'star2', 'star1'])

        while not bookq.empty():
            csvfile.writerow(bookq.get())
        print '[*] File has saved successfully !'


def urlsgen(url):
    start = range(0,250,25)
    urls = []
    urlq = Queue.Queue()

    for i in start:
        s = requests.get(url+str(i))
        if s.ok:
            html = s.text
            tree = lh.fromstring(html)
            a = tree.cssselect("div.pl2>a")
            urls.extend(a)
        else:
            sys.exit("http code != 200")

    urls = map(lambda x:x.attrib["href"], urls)
    for i in urls:
        urlq.put(i)
    return urlq

def run(threads_num):
    threads = []
    for i in range(threads_num):
        t = threading.Thread(target=wait2write, args=())
        threads.append(t)
        t.start()
    for i in threads:
        i.join()
    print "[*] all threads have done!"

def main():
    url = "https://book.douban.com/top250?start="
    global ua
    ua = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
        'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50']
    global urlq
    global bookq
    urlq = urlsgen(url)
    bookq = Queue.Queue()
    run(4)
    write2csv()

if __name__ == "__main__":
    main()