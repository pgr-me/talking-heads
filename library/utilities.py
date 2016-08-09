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
        #temp_list = [x for x in temp_list if '/transcript/' in x]
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
    transcript_dates = []
    for transcript in transcripts:
        date_list = transcript.split('transcript/')[1].split('/')[:3]
        date_list = [int(x) for x in date_list]
        transcript_date = date(date_list[0], date_list[1], date_list[2])
        transcript_dates.append(transcript_date)
    zipped_transcripts_dates = zip(transcript_dates, transcripts)
    return pd.DataFrame(zipped_transcripts_dates, columns=('date', name + '_links')).set_index('date')


def fox_to_df(fox_hosts):
    for idx, host in enumerate(fox_hosts):
        dates_trans = fox_dates_transcripts(host)
        if idx == 0:
            df = dates_trans
        else:
            df = pd.merge(df, dates_trans, how='outer', right_index=True, left_index=True)
    return df
