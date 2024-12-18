from flask import Flask,render_template,request,make_response,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_manager,LoginManager
import random

app=Flask(__name__)
app= Flask(__name__)
bcry= Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///Timeline.db"
app.config["SECRET_KEY"] = "end is beginning"
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(255), nullable=False)
    blogs = db.relationship('Blog', backref='user', lazy=True)
    profile = db.relationship('Profile', backref='user', lazy=True)

class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    img = db.Column(db.String)
    description = db.Column(db.String)
    likes=db.Column(db.Integer)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.String(60),unique=True)
    pic = db.Column(db.String)
    bio = db.Column(db.String)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

with app.app_context():
    db.create_all()

# @login_manager.user_loader
# def loader_user(user_id):
#     return User.query.get(user_id)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        return render_template('index.html')


@app.route('/register',methods=['POST','GET'])
def register():
    msg=''
    if request.method == 'POST':
        user=User.query.filter_by(username=request.form['username']).first()
        email=User.query.filter_by(email=request.form['email']).first()
        if user and email:
            if user.username==email.username:
                if bcry.check_password_hash (user.password, request.form['password']):
                    msg=' is already registered , please login!'
                    return render_template('popup.html',msg=msg,username=user.username)
                else:
                    msg='Password is wrong but user exists so please login!'
                    return render_template('popup.html',msg=msg)
            else:
                msg='Please change your username and email both are exists!'
                return render_template('popup.html',msg=msg)
        elif user:
            if user.email!=request.form['email']:
                msg='Username already exists , please change your username!'
                return render_template('popup.html',msg=msg)
        elif email:
            if email.username!=request.form['username']:
                msg='Email already exists , please change your Email!'
                return render_template('popup.html',msg=msg)
        else:
            user=User(username=request.form['username'],email=request.form['email'],password=bcry.generate_password_hash(request.form['password']).decode('utf-8'))
            
            db.session.add(user)
            db.session.commit()
            pid=(user.username)+'_'+str(random.randrange(1,99999,2))+str(random.randrange(1,99999,2))
            pic='https://i.pinimg.com/736x/75/46/fe/7546feb15edb3f2d46f22a737042b552.jpg'
            bio='Hey! There i am using Blogapp'

            profile=Profile(profile_id=pid,pic=pic,bio=bio,user_id=user.id)

            db.session.add(profile)
            db.session.commit()
            
            msg=' registration successful'
            session['username']=user.username                                                                                               
            render_template('popup.html',msg=msg)
            return redirect(url_for('home'))
    else:
        return render_template('register.html',msg=msg)

@app.route('/login',methods=['POST','GET'])
def login():
    msg=''
    if request.method == 'POST':
        user=User.query.filter_by(username=request.form['username']).first()
        if user:
            
            if bcry.check_password_hash (user.password, request.form['password']):
                
                msg=' login successful'
                session['username']=user.username
                        
                return redirect(url_for('home'))
            else:
                msg='Wrong password!'
                return render_template('login.html',msg=msg)
        else:
            msg='User doesn\'t exits!'
        return render_template('login.html',msg=msg)
    else:
        return render_template('login.html',msg=msg)

@app.route("/logout")
def logout():
    session.pop('username', None)
    msg='This user was logout!'
    render_template('popup.html',msg=msg)
    return redirect(url_for('login'))
    

@app.route('/home')
def home(): 
    blog=Blog.query.all()
    if 'username' in session:
        user=User.query.filter_by(username=session['username']).first()
        p=Profile.query.filter_by(user_id=user.id).first()
        print(p,user.id)
        bl=[]
        for b in blog:
            if b.user_id!=user.id:
                bl.append(b)
        try:
            pic=p.pic
        except Exception as e:
            pic='https://i.pinimg.com/originals/75/46/fe/7546feb15edb3f2d46f22a737042b552.jpg'
        
        return render_template('home.html',blog=bl,username=user.username,pic=pic)
    else:
       
        return render_template('home.html',blog=blog,username='')




@app.route("/profile")
def profile():
    if 'username' in session:
        user=User.query.filter_by(username=session['username']).first()
        profile=Profile.query.filter_by(user_id=user.id).first()
        
        return render_template('profile.html',username=user.username,profile=profile)
    else:
        return redirect(url_for('login'))
@app.route("/changeProfile",methods=["GET", "POST"])
def changeProfile():
    user=User.query.filter_by(username=session['username']).first()
    profile=Profile.query.filter_by(user_id=user.id).first()
    if request.method=='POST':
        profile.profile_id=request.form['pid']
        profile.pic=request.form['pic']
        profile.bio=request.form['bio']
        db.session.commit()
        return redirect(url_for('profile'))
    
    return render_template('changeprofile.html',p=profile)

@app.route("/blog")
def blog():
    user=User.query.filter_by(username=session['username']).first()
    blog=Blog.query.filter_by(user_id=user.id).all()
    p=Profile.query.filter_by(user_id=user.id).first()
    try: 
        
        coun=len(blog)
        
    except TypeError:
        coun=0
    
    pic=p.pic
    
        
    return render_template('blog.html',blog=blog,coun=coun,username=user.username,pic=pic)

@app.route('/addblog',methods=['POST','GET'])
def addblog():
    if request.method == 'POST':
        user=User.query.filter_by(username=session['username']).first()
        
        blog=Blog(title=request.form['titl'],img=request.form['img'],description=request.form['description'],likes=0,user_id=user.id)
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('blog'))
    return render_template('addblog.html',b='',title='')

@app.route('/editblog/<int:id>',methods=['POST','GET'])
def editblog(id):
    b=Blog.query.filter_by(id=id).first()
    if request.method == 'POST':
        
        b.title=request.form['titl']
        b.img=request.form['img']
        b.description=request.form['description']
        
        db.session.commit()
        return redirect(url_for('blog'))
    return render_template('addblog.html',b=b,title=b.title)

@app.route('/delblog/<int:id>',methods=['GET'])
def delblog(id):
    blog=Blog.query.filter_by(id=id).first()
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('blog'))

@app.route('/viewblog/<int:id>')
def viewblog(id):
    blog=Blog.query.filter_by(id=id).first()
    user=User.query.filter_by(username=session['username']).first()
    pic=Profile.query.filter_by(user_id=user.id).first()
    
    return render_template('viewblog.html',b=blog,pc=pic.pic,username=user.username)
@app.route('/delaccount')
def delaccount():
    
    user=User.query.filter_by(username=session['username']).first()
    blog=Blog.query.filter_by(user_id=user.id).all()
    for b in blog:
        b.user_id=0
        db.session.commit()
    profile=Profile.query.filter_by(user_id=user.id).all()
    for b in profile:
        b.user_id=0
        db.session.commit()
    db.session.delete(user)
    db.session.commit()
    session.pop('username', None)
    msg='Account deleted'
    # render_template('popup.html',msg=msg)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)