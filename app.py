
from sqlite3 import Timestamp
from flask import Flask, redirect,render_template,request,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib.pyplot as plt

app=Flask(__name__,template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///final.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__='User'
    userid=db.Column(db.Integer,primary_key=True)
    fullname=db.Column(db.String(50),nullable=False)
    username=db.Column(db.String(25),nullable=False)
    password=db.Column(db.String(25),nullable=False)

class Tracker(db.Model):
    __tablename__='Tracker'
    uid=db.Column(db.Integer,db.ForeignKey("User.userid"),nullable=False)
    tid=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(25),nullable=False)
    content=db.Column(db.String(40),nullable=False)
    type=db.Column(db.String(20),nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)

class Todo(db.Model):
    __tablename__='Todo'
    t_id=db.Column(db.Integer,db.ForeignKey("Tracker.tid"),nullable=False)
    logid=db.Column(db.Integer,primary_key=True)
    value=db.Column(db.Integer,nullable=False)
    comment=db.Column(db.String(40),nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
  
def create_graph(value,date_created):
    plt.switch_backend('Agg')
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.xticks(color='w')
    plt.plot(value,date_created)
    plt.savefig("static/graph.png")    


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html')
    else:
        fullname=request.form['fullname']
        username=request.form['username']
        password=request.form['password']
        user=User(fullname=fullname,password=password,username=username)
        db.session.add(user)
        db.session.commit()
        return redirect('/')    

@app.route('/login',methods=['GET','POST'])
def login():
    count=0
    users=User.query.all()
    if request.method=='GET':
        return render_template('login.html')
    else:
        username=request.form['username']
        password=request.form['password']
        for user in users:
            if user.username==username and user.password==password:
                temp=User.query.filter(User.username==username).first()
                count=1
                return render_template('tracker.html',user=temp)
        if count==0:
            return 'Invalid credentials!'        
        
@app.route('/login/<int:userid>/trackers',methods=['GET','POST'])
def track(userid):
    user=User.query.get_or_404(userid)
    trackers=Tracker.query.filter(Tracker.uid==user.userid).all()
    if request.method=='POST':
        name=request.form['name']
        type=request.form['type']
        content=request.form['content']
        tracker=Tracker(name=name,type=type,content=content,uid=user.userid)
        try:
            db.session.add(tracker)
            db.session.commit()
            return redirect(f'/login/{user.userid}/trackers')
        except:
            return 'There was an error creating the tracker.Try again!'
    else:
        return render_template('tracker.html',trackers=trackers,user=user)                

@app.route('/login/<int:userid>/trackers/update/<int:tid>',methods=['GET','POST'])
def update(userid,tid):
    user=User.query.get_or_404(userid)
    tracker=Tracker.query.get_or_404(tid)
    if request.method=='POST':
        tracker.name=request.form['name']
        tracker.type=request.form['type']
        tracker.content=request.form['content']
        try:
            db.session.commit()
            return redirect(f'/login/{user.userid}/trackers')
        except:
            return 'There was an error updating the tracker.Try again!' 
    else:
        return render_template('update.html',tracker=tracker,user=user)        


@app.route('/login/<int:userid>/trackers/delete/<int:tid>',methods=['GET','POST'])
def delete(userid,tid):
    user=User.query.get_or_404(userid)
    tracker_del=Tracker.query.get_or_404(tid)
    logs = Todo.query.filter(Todo.t_id == tid)
    for log in logs:
        db.session.delete(log)
    db.session.commit()
    try:
        db.session.delete(tracker_del)
        db.session.commit()
        return redirect(f'/login/{user.userid}/trackers')
    except:
        return 'There was an error deleting the tracker.Try again!'

@app.route('/login/<int:userid>/trackers/<int:tid>',methods=['GET','POST'])
def log(userid,tid):
    user=User.query.get_or_404(userid)
    tracker=Tracker.query.get_or_404(tid)
    values=[]
    timestamp=[]
    if request.method=='GET':
        logs=Todo.query.filter(Todo.t_id==tracker.tid).all()
        for log in logs:
                values.append(log.value)
                timestamp.append(log.date_created)
        create_graph(timestamp,values)
        return render_template('log.html',user=user,tracker=tracker,logs=logs)
    else:
        comment=request.form['comment']
        value=request.form['value']
        logs=Todo.query.filter(Todo.t_id==tracker.tid).all()
        newlog=Todo(comment=comment,value=value,t_id=tracker.tid)
        try:
            db.session.add(newlog)
            db.session.commit()
            return redirect(f'/login/{user.userid}/trackers/{tracker.tid}')
        except:
            return 'There was an error adding the log.Try again!'        

@app.route('/login/<int:userid>/trackers/<int:tid>/update/<int:logid>',methods=['GET','POST'])
def up_log(userid,tid,logid):
    user=User.query.get_or_404(userid)
    tracker=Tracker.query.get_or_404(tid)
    log=Todo.query.get_or_404(logid)
    if request.method=='POST':
        log.value=request.form['value']
        log.comment=request.form['comment']
        try:
            db.session.commit()
            return redirect(f'/login/{user.userid}/trackers/{tracker.tid}')
        except:
            return 'There was an error updating the log.Try again!'
    else:
        return render_template('updatelog.html',user=user,tracker=tracker,log=log)            

@app.route('/login/<int:userid>/trackers/<int:tid>/delete/<int:logid>',methods=['GET','POST'])
def del_log(userid,tid,logid):
    user=User.query.get_or_404(userid)
    tracker=Tracker.query.get_or_404(tid)
    del_log=Todo.query.get_or_404(logid)
    try:
        db.session.delete(del_log)
        db.session.commit()
        return redirect(f'/login/{user.userid}/trackers/{tracker.tid}')
    except:
        return 'There was an error deleting the log.Try again!'


if __name__=='__main__':
    app.run(debug=True)    
