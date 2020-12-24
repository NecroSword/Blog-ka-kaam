from flask import Flask,render_template, session, request, flash, redirect, abort, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config
from makedb import sab_kuch
import database
import recommend

app = Flask(__name__)
app.config["DEBUG"] = True

with open('secret_key.txt','rb') as f:
    app.secret_key = f.read()

cfg  = Config()
sendx = sab_kuch()

def andar_aa_gaya():
    #User hai to id do warna -1
    user_id = session.get('user_id')            #User id nikalni hai
    db = database.Db(cfg.db_file)            
    if user_id:                                 #Id exist karti hai to reccomend karna hai    
        user = db.get_user(user_id)
        return user_id if user else -1
    else:                                       #Nahi to Pehli fursat me nikal
        return -1

def data_de(rows,user_id):              #Dictionary banake fir sab iski matad se sab kuch print hoga
    data = {'titles':[],'links':[],'statuses':[],'article_ids':[],'user_id':user_id}
    for r in rows:
        title = r['title']
        if len(title) > 100:
            title = title[:100] + "..."
        data['titles'].append(title)
        data['links'].append(r['url'])
        data['article_ids'].append(r['article_id'])
        if r['lib_id']:
            data['statuses'].append('saved')
        else:
            data['statuses'].append('unsaved')
    return data

@app.route('/')
def home():
    user_id = andar_aa_gaya()
    db = database.Db(cfg.db_file)
    num_articles = cfg.num_articles_home
    msg = None
    data = None
    if user_id < 0:
        rec  = recommend.Rec(db,cfg.xfile,cfg.num_recs)
        ids = rec.get_user_recs(user_id)
        rows = db.get_articles_by_time(user_id,num_articles)
        msg = "Please login or create an accout to get Personalized recommendations"
    else:
        rec  = recommend.Rec(db,cfg.xfile,cfg.num_recs)
        ids = rec.get_user_recs(user_id)
        if ids:
            rows = db.get_articles_by_id(user_id,ids)
        else:
            msg = 'Please read more articles to ger Personalized Recommmendations'
            rows = db.get_articles_by_time(user_id,num_articles)
    data = data_de(rows,user_id)
    return render_template('articles.html',data=data, user_id=user_id,msg=msg,page_type="home")



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Kuch nahi hai yahan, pehli fursat me nikal</p>", 404


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/user_login',methods = ['POST'])
def user_login():                   #Login karne ke liye
    uname = request.form['username']
    pwd   = request.form['password']
    db = database.Db(cfg.db_file)
    pw_hash = generate_password_hash(pwd)
    user_info = db.get_user_info(uname)
    if not user_info:
        flash('Username does not exist')
        return redirect(url_for('login'))
    if not check_password_hash(user_info[0]['pw_hash'],pwd):
        flash('Invalid password')
        return redirect(url_for('login'))
    else:
        session['user_id'] = user_info[0]['user_id']
        return redirect(url_for('home'))


@app.route('/new_user',methods = ['POST'])
def naya_bakra():               #Naya usr banane ke liye
    uname = request.form['username']
    pwd   = request.form['password']
    cpwd  = request.form['confirm_password']
    email = request.form['e-mail']
    if pwd != cpwd:
        flash('Passwords must match')
        return redirect(url_for('signup'))
    else:
        db = database.Db(cfg.db_file)
        pw_hash = generate_password_hash(pwd)
        user_id = db.add_user(uname,pw_hash,email)
        if user_id < 0:
            flash('An account already exists with that username')
            return redirect(url_for('signup'))
        else:
            session['user_id'] = user_id
            return redirect(url_for('home'))


@app.route('/logout',methods = ['GET'])
def logout():
    session.pop('user_id',None)
    return render_template('signup.html')



@app.route('/save/<article_id>',methods=['GET'])
def save_article(article_id):
    user_id = andar_aa_gaya()
    if user_id < 0:
        return {'status':False}
    else:
        db = database.Db(cfg.db_file)
        db.add_article_to_lib(user_id,article_id)
        return {'status':True}


@app.route('/remove/<article_id>',methods=['GET'])
def remove_article(article_id):
    user_id = andar_aa_gaya()
    if user_id < 0:
        return {'status':False}
    else:
        db = database.Db(cfg.db_file)
        db.remove_article_from_lib(user_id,article_id)
        return {'status':True}

@app.route('/library',methods = ['GET'])
def library():
    user_id = andar_aa_gaya()
    msg = None
    data = None
    if user_id < 0:
        msg = "Please login or create an account to add articles to the library"
    else:
        db = database.Db(cfg.db_file)
        rows = db.get_user_articles(user_id)
        data = data_de(rows,user_id)

    return render_template('articles.html',data=data, user_id=user_id,msg=msg,page_type="library")

@app.route('/upload',methods = ['POST'])
def publish():
    user_id = andar_aa_gaya()
    if user_id < 0:
        flash('Please login or create an accout to Publish an article')
    else:
        title1 = request.form['title']
        text1 = request.form['text']
        keywords1 = request.form['keywords']
        sendx.check_to_do(0, title = title1, keywords=keywords1,text=text1)
        flash('Successfully Published')
    return redirect(url_for('publish'))
        

@app.route('/visit',methods = ['GET'])
def oof():                  #recommendation ke liye
    user_id = andar_aa_gaya()
    msg = None
    data = None
    if user_id < 0:
        msg = "Please login or create an accout to access recommendations"
    else:
        if 'id' in request.args:
            idx = int(request.args['id'])
            db = database.Db(cfg.db_file)
            rec  = recommend.Rec(db,cfg.xfile,cfg.num_recs, idx)
            ids = rec.get_user_recs(user_id)
            if ids:
                rows = db.get_articles_by_id(user_id,ids)
                data = data_de(rows,user_id)
            else:
                msg = "Nothing Similar to This article was found"
        else:
            abort(400)

    return render_template('articles.html',data=data, user_id=user_id,msg=msg,page_type="recommended")


if __name__ == '__main__':
    sendx.check_to_do(1, articles_csv=cfg.data_path)
    print('running in debug')
    app.run(port=5000, debug=True)