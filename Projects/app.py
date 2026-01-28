from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
from flask_mail import Mail, Message
import bcrypt

app = Flask(__name__)

def send_email():
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'ashwathr27100@gmail.com'
    app.config['MAIL_PASSWORD'] = 'uzpg hgap bcfh hwki'  # NOT your Gmail password
    app.config['MAIL_DEFAULT_SENDER'] = 'ashwathr27100@gmail.com'

    mail = Mail(app)
    return mail

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ashwath@2008",
        database="teamespada"
    )

@app.route('/')
def index():
    return render_template('teamespada.html')
@app.route('/schedule')
def sh():
    db=get_db()
    cursor=db.cursor()
    cursor.execute("SELECT DATE_FORMAT(event_date, '%d/%m/%Y'), event_day, TIME_FORMAT(event_time, '%h:%i %p'),event_name FROM brscrims_solo")
    br_solo=cursor.fetchall()
    cursor.execute("SELECT DATE_FORMAT(event_date, '%d/%m/%Y'), event_day, TIME_FORMAT(event_time, '%h:%i %p'),event_name FROM brscrims_duo")
    br_duo=cursor.fetchall()
    cursor.execute("SELECT DATE_FORMAT(event_date, '%d/%m/%Y'), event_day, TIME_FORMAT(event_time, '%h:%i %p'),event_name FROM brscrims_squad")
    br_squad=cursor.fetchall()
    cursor.execute("SELECT DATE_FORMAT(event_date, '%d/%m/%Y'), event_day, TIME_FORMAT(event_time, '%h:%i %p'),event_name FROM csscrims")
    cs_result=cursor.fetchall()
    cursor.close()
    db.close()
    if (br_solo!=[] or br_duo!=[] or br_squad!=[]) and cs_result!=[]:
        return render_template('schedule.html',br_soloevents=br_solo,br_duoevents=br_duo,br_squadevents=br_squad,cs_events=cs_result,solo_len=len(br_solo),duo_len=len(br_duo),squad_len=len(br_squad),cs_len=len(cs_result))
    elif br_solo!=[] or br_duo!=[] or br_squad!=[]:
        return render_template('schedule.html',br_soloevents=br_solo,br_duoevents=br_duo,br_squadevents=br_squad,solo_len=len(br_solo),duo_len=len(br_duo),squad_len=len(br_squad),cs_events=cs_result,cs_len=len(cs_result))
    else:
        return render_template('schedule.html',br_status='none',br_soloevents=br_solo,br_duoevents=br_duo,br_squadevents=br_squad,cs_events=cs_result,cs_len=len(cs_result))
    
@app.route('/rules')
def rules():
    return render_template('rules.html')
@app.route('/adminlogin')
def amlog():
    return render_template('adminlogin.html')

@app.route('/adminhome', methods=['POST'])
def adlogverify():
    un = str(request.form['un'])
    pwd = request.form['pwd']
    if un=="ESPGLADMIN":
        if pwd=="ESPGL18":
            return render_template('adminhome.html')
        else:
            return render_template('adminlogin.html',result="Invalid Password")
    else:
        return render_template('adminlogin.html',result="Invalid Username")
@app.route('/verifyaccess')
def acverify():
    return render_template('accessverify.html')
@app.route('/adminhome/newloginaccess')
def logacs():
    return render_template('grantlogacs.html')
@app.route('/adminhome/tourhost')
def host():
    return render_template('tourhost.html')

@app.route("/save_events", methods=["POST"])
def save_events():

    data = request.get_json()
    tournament_type=data["tournament"]
    events = data["events"]

    if tournament_type=='solo':
        table_name='brscrims_solo'
    elif tournament_type=='duo':
        table_name='brscrims_duo'
    elif tournament_type=='squad':
        table_name='brscrims_squad'
    else:
        table_name='csscrims'

    db = get_db()
    cur = db.cursor()
    for e in events:
        d = datetime.strptime(e["date"], "%Y-%m-%d")
        day = d.strftime("%A").upper()
        na=e["event"]
        name=na.upper()
        sql = f"""
        INSERT INTO {table_name}
        (event_date, event_day, event_time, event_name)
        VALUES (%s, %s, %s, %s)
        """

        cur.execute(sql, (
            e["date"],
            day,
            e["time"],
            name
        ))

    db.commit()
    cur.close()
    db.close()

    return "Tournament Hosted Successfully!"

@app.route('/results')
def result():
    return render_template('results.html')
@app.route('/login')
def log():
    return render_template('login.html')

@app.route('/adminhome/currenttournaments')
def cur():
    events=[]
    db=get_db()
    cursor=db.cursor()
    cursor.execute("SELECT DATE_FORMAT(event_date, '%d/%m/%Y'), event_day, TIME_FORMAT(event_time, '%h:%i %p'),event_name FROM brscrims_solo")
    br_solo=cursor.fetchall()
    cursor.execute("SELECT DATE_FORMAT(event_date, '%d/%m/%Y'), event_day, TIME_FORMAT(event_time, '%h:%i %p'),event_name FROM brscrims_duo")
    br_duo=cursor.fetchall()
    cursor.execute("SELECT DATE_FORMAT(event_date, '%d/%m/%Y'), event_day, TIME_FORMAT(event_time, '%h:%i %p'),event_name FROM brscrims_squad")
    br_squad=cursor.fetchall()
    cursor.execute("SELECT DATE_FORMAT(event_date, '%d/%m/%Y'), event_day, TIME_FORMAT(event_time, '%h:%i %p'),event_name FROM csscrims")
    cs_result=cursor.fetchall()
    cursor.close()
    db.close()
    if br_solo!=[]:
        events.append(['SOLO',br_solo[0][0],br_solo[len(br_solo)-1][0]])
    if br_duo!=[]:
        events.append(['DUO',br_duo[0][0],br_duo[len(br_duo)-1][0]])
    if br_squad!=[]:
        events.append(['SQUAD',br_squad[0][0],br_squad[len(br_squad)-1][0]])
    if cs_result!=[]:
        events.append(['CLASH SQAUD',cs_result[0][0],cs_result[len(cs_result)-1][0]])
    return render_template('curtour.html',events=events)

@app.route('/success', methods=['POST'])
def newlogin():
    db=get_db()
    cursor=db.cursor()
    log_cred=[]
    n=str(request.form['nu'])
    u=str(request.form['uid'])
    r=str(request.form['category'])
    un=str(request.form['un'])
    pwd=str(request.form['key'])
    hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
    log_cred.extend([n,u,r,un,hashed.decode()])
    cursor.execute("INSERT INTO member_account (player_name,player_uid,player_role,player_username,player_password) VALUES (%s,%s,%s,%s,%s)",log_cred)
    db.commit()
    db.close()   
    return render_template('grantlogacs.html',key="Successfully Created")

@app.route('/dashboard', methods=['POST'])
def logverify():
    db=get_db()
    cursor=db.cursor()
    un=str(request.form['un'])
    pwd=str(request.form['pwd'])
    cursor.execute("SELECT player_username FROM member_account")
    usernames=cursor.fetchall()
    if (un,) in usernames:
        cursor.execute("SELECT player_password FROM member_account where player_username=%s",(un,))
        stored_hash = cursor.fetchone()[0].encode()
        cursor.close()
        db.close()
        if bcrypt.checkpw(pwd.encode(), stored_hash):
            return render_template('adminhome.html')
        else:
            return render_template('login.html',status="Invalid Password")
    else:
        cursor.close()
        db.close()
        return render_template('login.html',status="Invalid Username") 

@app.route('/tournament/register')
def reg():
    return render_template('register.html')

def sendemail(email, tname, leader, leader_uid, pla2, pla2_uid, pla3, pla3_uid, pla4, pla4_uid):
    sendmail = send_email()

    html_body = render_template(
        'cs_tournament_template.html',
        tname=tname,
        leader=leader,
        leader_uid=leader_uid,
        pla2=pla2,
        pla2_uid=pla2_uid,
        pla3=pla3,
        pla3_uid=pla3_uid,
        pla4=pla4,
        pla4_uid=pla4_uid
    )

    msg = Message(
        subject="Registration Successful",
        recipients=[email],
        html=html_body
    )

    sendmail.send(msg)
    return "success"

@app.route('/regsuccess', methods=['POST'])
def regsub():
    email=str(request.form['email'])
    tname=str(request.form['tname'])
    leader=str(request.form['p1'])
    leader_uid=str(request.form['uid1'])
    pla2=str(request.form['p2'])
    pla2_uid=str(request.form['uid2'])
    pla3=str(request.form['p3'])
    pla3_uid=str(request.form['uid3'])
    pla4=str(request.form['p4'])
    pla4_uid=str(request.form['uid4'])
    db=get_db()
    cursor=db.cursor()
    dtls=(email,tname,leader,leader_uid,pla2,pla2_uid,pla3,pla3_uid,pla4,pla4_uid)
    cursor.execute("SELECT * FROM cs_tour_players")
    pldt=cursor.fetchall()
    for i in pldt:
        if i[1]==tname:
            return render_template('register.html',exist="Team name alreday exist please use someother team name.")
    if dtls not in pldt:
        cursor.execute("INSERT INTO cs_tour_players(email,tname,leader_name,leader_uid,player2_name,player2_uid,player3_name,player3_uid,player4_name,player4_uid) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",dtls)
        db.commit()
    cursor.close()
    db.close()

    sd=sendemail(email,tname,leader,leader_uid,pla2,pla2_uid,pla3,pla3_uid,pla4,pla4_uid)
    return render_template('register.html',status="Your details have been successfully submitted, you will be further notified via email.")

if __name__ == '__main__':
    app.run(debug=True)