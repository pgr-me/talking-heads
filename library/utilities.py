import os
from urllib2 import urlopen, URLError, HTTPError
import zipfile
import pickle
from bs4 import BeautifulSoup
import urllib2
from datetime import date
import pandas as pd


def mkdir(data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


def get_pickle(file_path):
    with open(file_path) as f:
        loaded_obj = pickle.load(f)
    return loaded_obj


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
        print 'soup'
        print soup
        for i in soup.find_all('a'):
            link = i.get('href')
            temp_list.append(link)
            print link
        temp_list = filter(None, temp_list)
        # temp_list = [x for x in temp_list if '/transcript/' in x]
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
    half_links = []
    for i in soup.find_all('a'):
        link = i.get('href')
        half_links.append(link)
    half_links = filter(None, half_links)
    half_links = [x for x in half_links if '/TRANSCRIPTS/' in x]
    half_links = list(set(half_links))
    links = ['http://cnn.com' + x for x in half_links]
    pickle.dump(links, open(pickle_dst, "wb"))
    return links


def get_msnbc_links(base_url, pickle_dst, pages, filter_str='/transcripts/'):
    links_list = []
    for page in pages:
        print page
        temp_list = []
        url = base_url + page
        f = urllib2.urlopen(url)
        f.geturl()
        soup = BeautifulSoup(f, 'lxml')
        for i in soup.find_all('a'):
            link = i.get('href')
            temp_list.append(link)
        links_list.extend(temp_list)
        links_list = filter(None, links_list)
        links_list = [x for x in links_list if filter_str in x]
    links_list = list(set(links_list))
    links_list = ['http://www.msnbc.com' + x for x in links_list]
    pickle.dump(links_list, open(pickle_dst, "wb"))
    return links_list


def fox_dates_transcripts(name):
    dst = os.path.join('data', name, 'links_list.pickle')
    transcripts = get_pickle(dst)
    transcripts = [x for x in transcripts if ('2016' in x) or ('2015' in x)]
    dates = []
    host_name = []
    network = []
    for transcript in transcripts:
        date_list = transcript.split('transcript/')[1].split('/')[:3]
        date_list = [int(x) for x in date_list]
        transcript_date = date(date_list[0], date_list[1], date_list[2])
        dates.append(transcript_date)
        host_name.append(name)
        network.append('fox')
    zipped_transcripts_dates = zip(network, host_name, dates, transcripts)
    return pd.DataFrame(zipped_transcripts_dates, columns=('network', 'host', 'date', 'link'))


def append_fox_hosts(hosts):
    for idx, host in enumerate(hosts):
        if idx == 0:
            df = fox_dates_transcripts(host)
        else:
            df = df.append(fox_dates_transcripts(host))
    return df


def cnn_dates_transcripts(name):
    src = os.path.join('data', name, 'links_list.pickle')
    dates = []
    host_name = []
    network = []
    links_list = pd.read_pickle(src)
    links_list = [x for x in links_list if 'html' in x]
    links_list = [x for x in links_list if 'pr' not in x]
    links_list = [x for x in links_list if '///' not in x]

    for link in links_list:
        year = int(link.split('TRANSCRIPTS/')[1].split('/')[0][:2]) + 2000
        month = int(link.split('TRANSCRIPTS/')[1].split('/')[0][2:])
        day = int(link.split('TRANSCRIPTS/')[1].split('/')[1])
        transcript_date = date(year, month, day)
        dates.append(transcript_date)
        host_name.append(name)
        network.append('cnn')
    zipped_transcripts_dates = zip(network, host_name, dates, links_list)
    return pd.DataFrame(zipped_transcripts_dates, columns=('network', 'host', 'date', 'link'))


def append_cnn_hosts(hosts):
    for idx, host in enumerate(hosts):
        if idx == 0:
            df = cnn_dates_transcripts(host)
        else:
            df = df.append(cnn_dates_transcripts(host))
    return df


def msnbc_dates_transcripts(name):
    src = os.path.join('data', name, 'links_list.pickle')
    dates = []
    host_name = []
    network = []
    links_list = pd.read_pickle(src)
    links_list = [x for x in links_list if len(x.split('/')[-1]) == 10]
    links_list = [x for x in links_list if '///' not in x]
    for link in links_list:
        year, month, day = link.split('/')[-1].split('-')
        year, month, day = int(year), int(month), int(day)
        transcript_date = date(year, month, day)
        dates.append(transcript_date)
        host_name.append(name)
        network.append('msnbc')
    zipped_transcripts_dates = zip(network, host_name, dates, links_list)
    return pd.DataFrame(zipped_transcripts_dates, columns=('network', 'host', 'date', 'link'))


def append_msnbc_hosts(hosts):
    for idx, host in enumerate(hosts):
        if idx == 0:
            df = msnbc_dates_transcripts(host)
        else:
            df = df.append(msnbc_dates_transcripts(host))
    return df


def append_hosts(hosts):
    for idx, host in enumerate(hosts):
        if idx == 0:
            df = msnbc_dates_transcripts(host)
        else:
            df = df.append(msnbc_dates_transcripts(host))
    return df


def get_soup(url):
    f = urlopen(url)
    f.geturl()
    return BeautifulSoup(f.read(), 'lxml')


def cnn_soup_to_list(soup):
    a_list = [x.encode('utf-8').strip() for x in soup.body.prettify().split('<br/>\n')]
    a_list = [x for x in a_list if '<body id' not in x]
    return a_list
