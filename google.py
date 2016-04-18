from flask import Flask,jsonify,request,Response,render_template,redirect,url_for
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
import urllib2
import json
import MySQLdb
from datetime import datetime
from bs4 import BeautifulSoup
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,SelectField
from wtforms.validators import Required

app = Flask(__name__);
app.config['SECRET_KEY'] = 'big change will real';
manager = Manager(app);
bootstrap = Bootstrap(app);
moment = Moment(app);

def get_package_info(packagename):
    link = 'https://play.google.com/store/apps/details?id=';
    package_link = link + packagename;
    request = urllib2.Request(package_link,headers={'Accept-Language': 'en_US'});
    web = urllib2.urlopen(request).read();
    data = BeautifulSoup(web,'html5lib');

    app_name = data.find('div',{'class': 'id-app-title'}).string;
    app_developer = data.find('span',{'itemprop': 'name'}).string;
    app_category = data.find('span',{'itemprop': 'genre'}).string;
    app_rate = data.find('span',{'class':'reviewers-small'}).get('aria-label');
    app_score = data.find('div',{'class': 'score'}).string;
    app_description = data.find('div',{'jsname': 'C4s9Ed'}).get_text();
    app_datepublish = data.find('div',{'itemprop': 'datePublished'}).string;
    app_datepublish = app_datepublish.replace(',','');
    app_datepublish = str(datetime.strptime(app_datepublish,'%B %d %Y'));
    app_softversion = data.find('div',{'itemprop': 'softwareVersion'}).string;
    app_filesize = data.find('div',{'itemprop': 'fileSize'}).string;
    app_operatingSystems = data.find('div',{'itemprop': 'operatingSystems'}).string;
    app_downloads = data.find('div',{'itemprop': 'numDownloads'}).string;
    app_package_name = packagename;
    meta_app_screenshot = data.find_all('img',{'itemprop': 'screenshot'}); #screenshot image url list
    app_screenshot = [];
    for app_url in meta_app_screenshot:
        url = app_url.get("src");
        app_screenshot.append(url);

    app_data = {
        'name': app_name,
        'packagename': app_package_name,
        'developer': app_developer,
        'category': app_category,
        'rate:': app_rate,
        'score': app_score,
        'description': app_description,
        'datepublish': app_datepublish,
        'softwareVersion': app_softversion,
        'fileSize': app_filesize,
        'operatingSystems': app_operatingSystems,
        'numDownloads': app_downloads,
        }

    return app_data;

def get_app_info_from_mysql(packagename):
    conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='123456',db='2016_04_12_google_app',charset='utf8');
    cursor = conn.cursor();
    select_sql = "SELECT name,developer,category,rate,score,description,datepublish,softwareVersion,fileSize,operatingSystems,numDownloads,app_icon_url,app_screenshot,Google_Play_Link,packagename FROM app_info WHERE packagename = '%s'" %(packagename);
    cursor.execute(select_sql);
    results = cursor.fetchall();
    print results;
    app_info = {'name':results[0][0],'developer':results[0][1],'category':results[0][2],'rate':results[0][3],'score':results[0][4],'description':results[0][5],'datapublish':results[0][6],'softwareVersion':results[0][7],'fileSize':results[0][8],'operatingSystems':results[0][9],'numDownloads':results[0][10],'app_icon_url':results[0][11],'app_screenshot':results[0][12],'Google_Play_Link':results[0][13],'packagename':results[0][14]};
    return app_info;


def get_package(link):
    #link = 'https://play.google.com/store/apps/collection/topselling_free';
    request = urllib2.Request(link,headers={'Accept-Language': 'en_US'});
    web = urllib2.urlopen(request).read();
    data = BeautifulSoup(web,"html5lib");
    meta_data = data.find_all("span","preview-overlay-container");
    package_list = [];
    for package in meta_data:
        package_name = package.get('data-docid');
        package_list.append(package_name);
        #print(package.get('data-docid'));
    return package_list;

class PackageForm(Form):
    packagename = StringField('Please enter your package name',validators=[Required()]);
    submit = SubmitField('Lookup');

class LinkForm(Form):
    link = StringField('Please enter your google play link',validators=[Required()]);
    submit = SubmitField('search');

class SelectForm(Form):
    price = SelectField(coerce=str,choices=[('paid','paid'),('free','free')]);
    category = SelectField(coerce=str,choices=[('BOOKS_AND_REFERENCE','Books & Reference'),('BUSINESS','BUSINESS'),('COMICS','COMICS')]);
    date = SelectField(coerce=str,choices=[('2016_04_12_google_app','2016_04_12_google_app'),('2016_04_17_google_app','2016_04_17_google_app')]);
    num = SelectField(coerce=int,choices=[(10,10),(20,20),(30,30)]);
    submit = SubmitField('submit');

@app.route('/top_chart',methods=['GET','POST'])
def select():
    form = SelectForm();
    if form.validate_on_submit():
        price = form.price.data;
        category = form.category.data;
        date = form.date.data;
        num = form.num.data;
        return redirect(url_for('.display',price=price,category=category,date=date,num=num));
    return render_template('index.html',form=form);

@app.route('/display',methods=['GET','POST'])
def display():
    price = request.args.get('price');
    category = request.args.get('category');
    date = request.args.get('date');
    num = request.args.get('num');
    num =int(num);
    database = date;
    conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='123456',db=database,charset='utf8');
    cursor = conn.cursor();
    if price == 'paid':
        select_sql = "SELECT packagename FROM %s WHERE paid_rank < %i" %(category,num);
    else:
        select_sql = "SELECT packagename FROM %s WHERE free_rank < %i" %(category,num);
    print select_sql;
    cursor.execute(select_sql);
    results = cursor.fetchall();
    result_dict = {};
    for i in results:
        packname = str(i[0]);
        result_dict[packname] = get_app_info_from_mysql(i);
        print i[0];
    resp = jsonify(result_dict);
    resp.status_code = 200;
    return resp;


@app.route('/app_lookup',methods=['GET','POST'])
def index():
    form = PackageForm();
    if form.validate_on_submit():
        packagename = form.packagename.data;
        return redirect(url_for('.info',packagename=packagename));
    return render_template('index.html',form=form);

@app.route('/app/info/<path:packagename>',methods=['GET','POST'])
def info(packagename):
    packagename = packagename;
    #app_data = get_package_info(packagename);
    app_data = get_app_info_from_mysql(packagename);
    resp = jsonify(app_data);
    resp.status_code = 200;
    return resp;


@app.route('/get_package_name',methods=['GET','POST'])
def get_package_name():
    form = LinkForm();
    if form.validate_on_submit():
        link = form.link.data;
        return redirect(url_for('.packagelist',link = link));
    return render_template('index.html',form=form);

@app.route('/packagelist/<path:link>',methods=['GET','POST'])
def packagelist(link):
    link = link;
    pklist = get_package(link);
    return json.dumps(pklist);


if __name__ == '__main__':
    manager.run();