#coding: utf8
from bs4 import BeautifulSoup
import urllib2
import urllib
import MySQLdb
import datetime


today = str(datetime.date.today());
database = today + '_google_app';
database = database.replace('-','_');
con = MySQLdb.connect(host='127.0.0.1',user=username,passwd=password);
cur = con.cursor();
create_database_sql = 'CREATE DATABASE ' + database + '   DEFAULT CHARACTER SET utf8   DEFAULT COLLATE utf8_general_ci;';
cur.execute(create_database_sql);
conn = MySQLdb.connect(host='127.0.0.1',user=username,passwd=password,db=database,charset='utf8');
cursor = conn.cursor();

def create_all_table():
    for category in category_list:
        sql = 'create table ' + category + ' ( id int primary key auto_increment, packagename varchar(2000), paid_rank int(80), free_rank int(80), price varchar(20) );';
        cursor.execute(sql);
        conn.commit();

def create_app_info_table():
    sql = 'create table app_info ( id int primary key auto_increment, packagename varchar(200), description varchar(15000), datepublish varchar(80), fileSize varchar(80), numDownloads varchar(80), category varchar(80), name varchar(80), softwareVersion varchar(80), score varchar(8), operatingSystems varchar(80), developer varchar(100), rate varchar(80), app_icon_url varchar(500), app_screenshot varchar(5000), Google_Play_Link varchar(200) );';
    cursor.execute(sql);
    conn.commit();

def get_package(category,price):
    """ 
       type:free or paid
    """
    package_name_list = [];
    package_price_list = [];
    for num in range(0,9):
        form_data = {"start": 60 * num,"num": 60,"numChildren": 0,"cctcss": 'square-cover',"cllayout": 'NORMAL',"ipf": 1,"xhr": 1,"token": 'you can get this token from browser'};
        cookie_str = 'you cookie str';
        link = 'https://play.google.com/store/apps/category/' + category + '/collection/topselling_' + price + '?authuser=0';
        params = urllib.urlencode(form_data);
        request = urllib2.Request(link,params,headers={'Accept-Language': 'en_US','Cookie': cookie_str});
        try:
            web = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            if e.code != 200:
                print category + 'is' + str(e.code);
                package_name_list=[];
                package_price_list=[];
                return package_name_list,package_price_list;
        web = web.read();
        data = BeautifulSoup(web,"html5lib");
        meta_data = data.find_all("span","preview-overlay-container");
        price_data = data.find_all("span","display-price");
        package_list = [];
        for package in meta_data:
            package_name = package.get('data-docid');
            package_list.append(package_name);
        package_name_list.extend(package_list);
        package_price = [];
        for app_price in price_data:
            pk_price = app_price.string;
            package_price.append(pk_price);
        package_price_list.extend(package_price);
    return package_name_list,package_price_list;

def mysql_insert(category):
    package_list_free,free_price = get_package(category,'free');
    print len(package_list_free);
    for free_rank,packagename in enumerate(package_list_free):
        free_insert_sql = u"INSERT INTO %s ( packagename,free_rank,price ) VALUES ('%s',%i,'%s')" % (category,packagename,free_rank,u'free');
        cursor.execute(free_insert_sql);
        conn.commit();
    package_list_paid,paid_price = get_package(category,'paid');
    print len(package_list_paid);
    for paid_rank,packagename in enumerate(package_list_paid):
        paid_insert_sql = u"INSERT INTO %s ( packagename,paid_rank,price ) VALUES ('%s',%i,'%s')" % (category,packagename,paid_rank,paid_price[paid_rank*2]);
        cursor.execute(paid_insert_sql);
        conn.commit();

if __name__ == '__main__':   
    category_list = ['BOOKS_AND_REFERENCE','BUSINESS','COMICS','COMMUNICATION','EDUCATION','ENTERTAINMENT','FINANCE','HEALTH_AND_FITNESS','LIBRARIES_AND_DEMO','LIFESTYLE','APP_WALLPAPER','MEDIA_AND_VIDEO','MEDICAL','MUSIC_AND_AUDIO','NEWS_AND_MAGAZINES','PERSONALIZATION','PHOTOGRAPHY','PRODUCTIVITY','SHOPPING','SOCIAL','SPORTS','TOOLS','TRANSPORTATION','TRAVEL_AND_LOCAL','WEATHER'];
    game_subcategory_list = ['GAME_ACTION','GAME_ADVENTURE','GAME_ARCADE','GAME_BOARD','GAME_CARD','GAME_CASINO','GAME_CASUAL','GAME_EDUCATIONAL','GAME_MUSIC','GAME_PUZZLE','GAME_RACING','GAME_ROLE_PLAYING','GAME_SIMULATION','GAME_SPORTS','GAME_STRATEGY','GAME_TRIVIA','GAME_WORD'];
    category_list.extend(game_subcategory_list);
    create_all_table();
    for category in category_list:
        print category;
        mysql_insert(category);