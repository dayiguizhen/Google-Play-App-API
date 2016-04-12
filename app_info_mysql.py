#coding: utf8
import urllib2,time
import MySQLdb
import httplib
import urlparse
from bs4 import BeautifulSoup
import datetime

today = str(datetime.date.today());
database = today + '_google_app';
database = database.replace('-','_');


cookie_str = 'you cookie str';

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
        #data = BeautifulSoup(web,'html5lib');
        data = BeautifulSoup(web,"html.parser");
        print packagename;
        
        app_name = data.find('div',{'class': 'id-app-title'}).string;
        app_name = app_name.encode('utf-8');
        app_developer = data.find('span',{'itemprop': 'name'}).string;
        app_developer = app_developer.encode('utf-8');
        app_category = data.find('span',{'itemprop': 'genre'}).string;
        app_category = app_category.encode('utf-8')
        #获取App的应用评价数
        if data.find('span',{'class':'reviewers-small'}) is not None:
            app_rate = data.find('span',{'class':'reviewers-small'}).get('aria-label');
        else:
            app_rate = 0;
        #获取App的应用评分
        if data.find('div',{'class': 'score'}) is not None:
            app_score = data.find('div',{'class': 'score'}).string;
        else:
            app_score = None;
        app_description = data.find('div',{'jsname': 'C4s9Ed'}).get_text();
        app_description = app_description.encode('utf-8');
        app_datepublish = data.find('div',{'itemprop': 'datePublished'}).string;
        app_icon_url = app_icon = data.find('img',{'class': 'cover-image'}).get('src');
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
        app_screenshot = str(app_screenshot);
        
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
            'app_icon_url': app_icon_url,
            'app_screenshot': app_screenshot,
            'Google_Play_Link': package_link,
            'packagename': packagename,
            }
        
        #print app_data;
        return app_data;

conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='123456',db=database,charset='utf8');
cursor = conn.cursor();

def mysql_insert(packagename):
    myDict = get_package_info(packagename);
    placeholders = ','.join(['%s']* len(myDict));
    colums = ','.join(myDict.keys());
    insert_sql = "INSERT INTO app_info ( %s ) VALUES ( %s )" % (colums,placeholders);
    cursor.execute(insert_sql,myDict.values());
    conn.commit();

def mysql_select(packagename):
    select_sql = "SELECT * FROM app_info WHERE packagename = '%s'" %(packagename);
    print select_sql;
    flag = cursor.execute(select_sql);
    results = cursor.fetchall();
    return flag;


def mysql_update(packagename):
    myDict = get_package_info(packagename);
    myDict.pop("id",None);
    placeholders = ','.join(['%s']* len(myDict));
    colums = ','.join(myDict.keys());
    update_sql = "UPDATE app_info SET category = %s, name = %s, datepublish = %s, app_icon_url = %s, Google_Play_Link = %s, description = %s, softwareVersion = %s, operatingSystems = %s, rate = %s,score = %s, fileSize = %s, app_screenshot = %s, numDownloads = %s, developer = %s WHERE packagename = %s";
    cursor.execute(update_sql,myDict.values());
    conn.commit();

def mysql_get_name(category):
    select_sql = "SELECT packagename FROM " + category + ";";
    flag = cursor.execute(select_sql);
    results = cursor.fetchall();
    meta_list = [];
    for row in results:
        meta_list.append(row[0]);
    return meta_list;


category_list = ['BOOKS_AND_REFERENCE','BUSINESS','COMICS','COMMUNICATION','EDUCATION','ENTERTAINMENT','FINANCE','HEALTH_AND_FITNESS','LIBRARIES_AND_DEMO','LIFESTYLE','APP_WALLPAPER','MEDIA_AND_VIDEO','MEDICAL','MUSIC_AND_AUDIO','NEWS_AND_MAGAZINES','PERSONALIZATION','PHOTOGRAPHY','PRODUCTIVITY','SHOPPING','SOCIAL','SPORTS','TOOLS','TRANSPORTATION','TRAVEL_AND_LOCAL','WEATHER'];
package_list = [];

for category in category_list:
    meta_list = mysql_get_name(category);
    package_list.extend(meta_list);

print len(package_list);

if __name__ == '__main__':
    for packagename in package_list:
        if mysql_select(packagename):
            continue;
            #mysql_update(packagename);
        else:
            mysql_insert(packagename);
