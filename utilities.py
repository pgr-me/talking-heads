import os
from urllib2 import urlopen, URLError, HTTPError
import zipfile


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

    
def get_kelly_transcripts(base_url, page_ids, pickle_dst):
    links_list = []
    wd = webdriver.Firefox()
    wd.get(base_url)
    for page in page_ids:

        html_content = wd.page_source

        # get links
        soup = BeautifulSoup(html_content, 'lxml')
        soup.find_all('a')
        temp_list = []
        for i in soup.find_all('a'):
            link = i.get('href')
            temp_list.append(link)
        temp_list = filter(None, temp_list)
        temp_list = [x for x in temp_list if 'http://www.foxnews.com/transcript/' in x]
        links_list.extend(temp_list)
        print 'Page is %s' % str(page)

        # navigate to next page
        elem = wd.find_element_by_link_text(str(page)).click()
    links_list = list(set(links_list))
    pickle.dump(links_list, open(pickle_dst, "wb" ) )
    return links_list

