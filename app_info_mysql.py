#coding: utf8
import urllib2,time
import MySQLdb
import httplib
import urlparse
import datetime
from bs4 import BeautifulSoup

today = str(datetime.date.today());
database = today + '_google_app';
database = database.replace('-','_');
cookie_str = 'you cookie str';

def get_package_info(packagename):
    print "[" + datetime.datetime.now().strftime('%b-%d-%y %H:%M:%S') + "] " + packagename;
    link = 'https://play.google.com/store/apps/details?id=';
    package_link = link + packagename;
    request = urllib2.Request(package_link,headers={'Accept-Language': 'en_US','Cookie':cookie_str});
    try:
        web = urllib2.urlopen(request);
    except urllib2.HTTPError as e:
        if e.code == 404:
            print packagename + ' is 404';
            app_data = {};
            return app_data;
        if e.code == 403:
            print packagename + "403";
            app_data = {};
            return app_data;
    web = web.read();
    data = BeautifulSoup(web,"html.parser",from_encoding="utf-8");
    app_name = data.find('div',{'class': 'id-app-title'}).string;
    app_name = app_name.encode('utf-8');
    if data.find('span',{'itemprop': 'name'}) is not None:
        app_developer = data.find('span',{'itemprop': 'name'}).string;
        app_developer = app_developer.encode('utf-8');
    else:
        app_developer = None;
    app_category = data.find('span',{'itemprop': 'genre'}).string;
    app_category = app_category.encode('utf-8');
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
    if data.find('div',{'itemprop': 'datePublished'}) is not None:
        app_datepublish = data.find('div',{'itemprop': 'datePublished'}).string;
        app_datepublish = app_datepublish.encode('utf-8');
    else:
        app_datepublish = None;
    app_icon_url = app_icon = data.find('img',{'class': 'cover-image'}).get('src');
    if data.find('div',{'itemprop': 'softwareVersion'}) is not None:
        app_softversion = data.find('div',{'itemprop': 'softwareVersion'}).string;
        app_softversion = app_softversion.encode('utf-8');
    else:
        app_softversion = None;
    if data.find('div',{'itemprop': 'fileSize'}) is not None:
        app_filesize = data.find('div',{'itemprop': 'fileSize'}).string;
    else:
        app_filesize = None;
    if data.find('div',{'itemprop': 'operatingSystems'}) is not None:
        app_operatingSystems = data.find('div',{'itemprop': 'operatingSystems'}).string;
    else:
        app_operatingSystems = None;
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
    return app_data;

conn = MySQLdb.connect(host='127.0.0.1',user=username,passwd=password,db=database,charset='utf8');
cursor = conn.cursor();

def mysql_insert(packagename):
    myDict = get_package_info(packagename);
    for key in myDict:
        if myDict[key] is not None:
            if isinstance(myDict[key],str):
                myDict[key] = myDict[key].decode('utf8');
            elif isinstance(myDict[key],int):
                myDict[key] = str(myDict[key]).decode('utf8');
            else:
                myDict[key] = u'' + myDict[key];
    
    placeholders = ','.join(['%s']* len(myDict));
    colums = ','.join(myDict.keys());
    insert_sql = "INSERT INTO app_info ( %s ) VALUES ( %s )" % (colums,placeholders);
    cursor.execute(insert_sql,myDict.values());
    conn.commit();

def mysql_select(packagename):
    select_sql = "SELECT * FROM app_info WHERE packagename = '%s'" %(packagename);
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

if __name__ == '__main__':
    category_list = ['BOOKS_AND_REFERENCE','BUSINESS','COMICS','COMMUNICATION','EDUCATION','ENTERTAINMENT','FINANCE','HEALTH_AND_FITNESS','LIBRARIES_AND_DEMO','LIFESTYLE','APP_WALLPAPER','MEDIA_AND_VIDEO','MEDICAL','MUSIC_AND_AUDIO','NEWS_AND_MAGAZINES','PERSONALIZATION','PHOTOGRAPHY','PRODUCTIVITY','SHOPPING','SOCIAL','SPORTS','TOOLS','TRANSPORTATION','TRAVEL_AND_LOCAL','WEATHER'];
    game_subcategory_list = ['GAME_ACTION','GAME_ADVENTURE','GAME_ARCADE','GAME_BOARD','GAME_CARD','GAME_CASINO','GAME_CASUAL','GAME_EDUCATIONAL','GAME_MUSIC','GAME_PUZZLE','GAME_RACING','GAME_ROLE_PLAYING','GAME_SIMULATION','GAME_SPORTS','GAME_STRATEGY','GAME_TRIVIA','GAME_WORD'];
    category_list.extend(game_subcategory_list);
    package_list = [];
    
    for category in category_list:
        meta_list = mysql_get_name(category);
        package_list.extend(meta_list);

    print len(package_list);

    for packagename in package_list:
        if mysql_select(packagename):
            continue;
        else:
            mysql_insert(packagename);
