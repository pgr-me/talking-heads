import os
from urllib2 import urlopen, URLError, HTTPError
import zipfile
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pickle
from bs4 import BeautifulSoup
import time
import urllib2


def mkdir(data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


def dlfile(url, data_dir, filename):
    # Open the url
    try:
        f = urlopen(url)
        print "downloading " + url
        # File path
        file_path = os.path.join(data_dir, filename)
        # Open our local file for writing
        with open(file_path, "wb") as local_file:
            local_file.write(f.read())
        print file_path
        print os.path.basename(file_path)
    # handle errors
    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url


def unzip_file(src_path, dst_dir):
    zip_ref = zipfile.ZipFile(src_path, 'r')
    zip_ref.extractall(dst_dir)
    zip_ref.close()


def get_fox_links(base_url, pages, pickle_dst, delay=5):
    links_list = []

    # cycle through each page
    for page in pages:
        url = base_url + '?page=' + str(page)
        f = urllib2.urlopen(url)
        f.geturl()

        # get list of links in html and append to links_list
        soup = BeautifulSoup(f.read(), 'lxml')
        soup.find_all('a')
        temp_list = []

        for i in soup.find_all('a'):
            link = i.get('href')
            temp_list.append(link)
        temp_list = filter(None, temp_list)
        temp_list = [x for x in temp_list if 'http://www.foxnews.com/transcript/' in x]
        links_list.extend(temp_list)

        # print page number and current output
        print 'Page is %s' % str(page)
        print temp_list

        url_next = base_url + '#si=' + str(page)

        # print page number and current output
        print 'Page is %s' % str(page)
        print temp_list
        print url_next

    links_list = list(set(links_list))
    pickle.dump(links_list, open(pickle_dst, "wb"))
    return links_list


def get_cnn_links(url, pickle_dst):
    f = urllib2.urlopen(url)
    f.geturl()
    soup = BeautifulSoup(f, 'lxml')
    links_list = []
    for i in soup.find_all('a'):
        link = i.get('href')
        links_list.append(link)
    links_list = filter(None, links_list)
    links_list = [x for x in links_list if '/TRANSCRIPTS/' in x]
    links_list = list(set(links_list))
    pickle.dump(links_list, open(pickle_dst, "wb"))
    return links_list


def get_msnbc_links(base_url, pickle_dst, filter_str, pages):
    links_list = []
    for page in pages:
        temp_list = []
        url = base_url + page
        f = urllib2.urlopen(url)
        f.geturl()
        soup = BeautifulSoup(f, 'lxml')
        for i in soup.find_all('a'):
            link = i.get('href')
            temp_list.append(link)
        links_list.append(temp_list)
    links_list = filter(None, links_list)
    links_list = [x for x in links_list if filter_str in x]
    links_list = list(set(links_list))
    pickle.dump(links_list, open(pickle_dst, "wb"))
    return links_list
