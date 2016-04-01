#coding: utf8
import urllib2,time
import MySQLdb
import httplib
import urlparse
from bs4 import BeautifulSoup

cookie_str = 'my cookie str';

def request(url,cookie=''):
    ret = urlparse.urlparse(url);
    if ret.scheme == 'http':
        conn = httplib.HTTPConnection(ret.netloc);
    elif ret.scheme == 'https':
        conn = httplib.HTTPSConnection(ret.netloc);

    url = ret.path;
    if ret.query: url += '?' + ret.query;
    if ret.fragment: url += '#' + ret.fragment;
    if not url: url = '/';

    conn.request(method="GET",url=url,headers={'Cookie': cookie});
    return conn.getresponse();

def get_package_info(packagename):
    link = 'https://play.google.com/store/apps/details?id=';
    package_link = link + packagename;
    web = request(package_link,cookie_str);
    if web.status == 404:
        print "CR";
        app_data = {};
        return app_data;
    if web.status == 403:
        print "403";
        app_data = {};
        return app_data;
    else:
        web = web.read();
        data = BeautifulSoup(web,"html.parser");
        print packagename;
        
        app_name = data.find('div',{'class': 'id-app-title'}).string;
        app_name = app_name.encode('utf-8');
        app_developer = data.find('span',{'itemprop': 'name'}).string;
        app_developer = app_developer.encode('utf-8');
        app_category = data.find('span',{'itemprop': 'genre'}).string;
        app_rate = data.find('span',{'class':'reviewers-small'}).get('aria-label');
        app_score = data.find('div',{'class': 'score'}).string;
        app_description = data.find('div',{'jsname': 'C4s9Ed'}).get_text();
        app_description = app_description.encode('utf-8');
        app_datepublish = data.find('div',{'itemprop': 'datePublished'}).string;
        if data.find('div',{'itemprop': 'softwareVersion'}) is not None:
            app_softversion = data.find('div',{'itemprop': 'softwareVersion'}).string;
        else:
            app_softversion = None;
        if data.find('div',{'itemprop': 'fileSize'}) is not None:
            app_filesize = data.find('div',{'itemprop': 'fileSize'}).string;
        else:
            app_filesize = None;
        app_operatingSystems = data.find('div',{'itemprop': 'operatingSystems'}).string;
        if data.find('div',{'itemprop': 'numDownloads'}) is not None:
            app_downloads = data.find('div',{'itemprop': 'numDownloads'}).string;
        else:
            app_downloads = 0;
        
        meta_app_screenshot = data.find_all('img',{'itemprop': 'screenshot'}); #screenshot image url list
        app_screenshot = [];
        for app_url in meta_app_screenshot:
            url = app_url.get("src");
            app_screenshot.append(url);
        
        app_data = {
            'id': None,
            'name': app_name,
            'developer': app_developer,
            'category': app_category,
            'rate': app_rate,
            'score': app_score,
            'description': app_description,
            'datepublish': app_datepublish,
            'softwareVersion': app_softversion,
            'fileSize': app_filesize,
            'operatingSystems': app_operatingSystems,
            'numDownloads': app_downloads,
            }
        
        return app_data;

conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='123456',db='google_app',charset='utf8');
cursor = conn.cursor();

def mysql_insert(packagename):
    myDict = get_package_info(packagename);
    insert_table = 'app_info';
    placeholders = ','.join(['%s']* len(myDict));
    colums = ','.join(myDict.keys());
    insert_sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (insert_table,colums,placeholders);
    cursor.execute(insert_sql,myDict.values());
    conn.commit();

f = open('packagename.txt').read();
package_list = f.split('\r\n');

if __name__ == '__main__':
    for packagename in package_list:
        mysql_insert(packagename);
        time.sleep(3);
