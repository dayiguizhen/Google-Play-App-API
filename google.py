from flask import Flask,jsonify,request,Response,render_template,redirect,url_for
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
import urllib2
import json
from bs4 import BeautifulSoup
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__);
app.config['SECRET_KEY'] = 'big change will real'
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
    app_softversion = data.find('div',{'itemprop': 'softwareVersion'}).string;
    app_filesize = data.find('div',{'itemprop': 'fileSize'}).string;
    app_operatingSystems = data.find('div',{'itemprop': 'operatingSystems'}).string;
    app_downloads = data.find('div',{'itemprop': 'numDownloads'}).string;
    
    meta_app_screenshot = data.find_all('img',{'itemprop': 'screenshot'}); #screenshot image url list
    app_screenshot = [];
    for app_url in meta_app_screenshot:
        url = app_url.get("src");
        app_screenshot.append(url);

    app_data = {
        'name': app_name,
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
    app_data = get_package_info(packagename);
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
