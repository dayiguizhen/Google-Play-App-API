from bs4 import BeautifulSoup
import urllib2
import urllib
import MySQLdb
import datetime

today = str(datetime.date.today());
database = today + '_google_app';
database = database.replace('-','_');
con = MySQLdb.connect(host='127.0.0.1',user='root',passwd='123456');
cur = con.cursor();
create_database_sql = 'CREATE DATABASE ' + database + '   DEFAULT CHARACTER SET utf8   DEFAULT COLLATE utf8_general_ci;';
print create_database_sql;
cur.execute(create_database_sql);

conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='123456',db=database,charset='utf8');
cursor = conn.cursor();

category_list = ['BOOKS_AND_REFERENCE','BUSINESS','COMICS','COMMUNICATION','EDUCATION','ENTERTAINMENT','FINANCE','HEALTH_AND_FITNESS','LIBRARIES_AND_DEMO','LIFESTYLE','APP_WALLPAPER','MEDIA_AND_VIDEO','MEDICAL','MUSIC_AND_AUDIO','NEWS_AND_MAGAZINES','PERSONALIZATION','PHOTOGRAPHY','PRODUCTIVITY','SHOPPING','SOCIAL','SPORTS','TOOLS','TRANSPORTATION','TRAVEL_AND_LOCAL','WEATHER'];

def create_all_table():
    for category in category_list:
        sql = 'create table ' + category + ' ( id int primary key auto_increment, packagename varchar(500), paid_rank int(80), free_rank int(80) );';
        cursor.execute(sql);
        conn.commit();

def get_package(category,price):
    """ 
       type:free or paid
    """
    package_name_list = [];
    for num in range(0,9):
        form_data = {"start": 60 * num,"num": 60,"numChildren": 0,"cctcss": 'square-cover',"cllayout": 'NORMAL',"ipf": 1,"xhr": 1,"token": 'ope8A7jXMKISufw4HA8rzG5_uDI:1459912367279'};
        cookie_str = 'you cookie str';
        link = 'https://play.google.com/store/apps/category/' + category + '/collection/topselling_' + price + '?authuser=0';
        params = urllib.urlencode(form_data);
        request = urllib2.Request(link,params,headers={'Accept-Language': 'en_US','Cookie': cookie_str});
        web = urllib2.urlopen(request).read();
        data = BeautifulSoup(web,"html5lib");
        meta_data = data.find_all("span","preview-overlay-container");
        package_list = [];
        for package in meta_data:
            package_name = package.get('data-docid');
            package_list.append(package_name);
        package_name_list.extend(package_list);
    return package_name_list;

def mysql_insert(category):
    package_list_free = get_package(category,'free');
    for free_rank,packagename in enumerate(package_list_free):
        free_insert_sql = "INSERT INTO %s ( packagename,free_rank ) VALUES ('%s',%i)" % (category,packagename,free_rank);
        cursor.execute(free_insert_sql);
        conn.commit();
    package_list_paid = get_package(category,'paid');
    print len(package_list_paid);
    for paid_rank,packagename in enumerate(package_list_paid):
        paid_insert_sql = "INSERT INTO %s ( packagename,paid_rank ) VALUES ('%s',%i)" % (category,packagename,paid_rank);
        cursor.execute(paid_insert_sql);
        conn.commit();


create_all_table();

for category in category_list:
    print category;
    mysql_insert(category);
