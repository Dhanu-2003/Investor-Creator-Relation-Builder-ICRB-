from flask import Flask, render_template, request
import mysql.connector as msc
import smtplib
from email.mime.text import MIMEText


conn = msc.connect(host = '127.0.0.1',port = 3306,user='root',password='Dhanu@2003',database = 'software')

cur = conn.cursor()

app = Flask(__name__)

mail = ""
id = ""
inv = 0


def send_email(subject, body, to_email):
    # Your email credentials
    sender_email = "idea2024hub@gmail.com"
    sender_password = "gbgh kzyi rtdx nrnm"

    # Email content
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email

    # Establish a connection to the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        
        # Login to your email account
        server.login(sender_email, sender_password)
        
        # Send the email
        server.sendmail(sender_email, to_email, message.as_string())





@app.route('/')
def index():
    global mail,id
    mail = ""
    id = ""
    return render_template("login.html")

@app.route('/check', methods=['POST'])
def check():
    global mail,id
    cur.reset()
    cur.execute("select * from login")
    name = request.form.get('username')
    password = request.form.get('password')
    print(name,password)
    for i in cur:
        print(i[0],"->",i[1])
        if i[0]==name and i[1]==password:
            mail = name
         
            return profile()
        
    return "INVALID INPUT"


@app.route("/profile")
def profile():
    global mail,id,inv
    if mail=="":
        return index()
    print()
    cur.reset()
    cur.execute("select * from data where Email_ID = '{}';".format(mail))
    data = [i for i in cur.fetchall()[0]]
    id = str(data[-1])
    inv=0
    return render_template('index.html',data = data)


@app.route('/add_project_data',methods = ['post'])
def add():
    global mail,id,inv
    title = request.form.get('title')
    des = request.form.get('desc')
    if mail=="" or id=="" or inv==1:
        return index()
    cur.reset()
    cur.execute("select ID from projects;")
    
    temp_id = int(cur.fetchall()[-1][-1])+1
    cur.reset()
    cur.execute("insert into projects values('{}','{}','{}','{}','')".format(temp_id,title,des,id))
    conn.commit()
    cur.reset()
    cur.execute("select Project_Working from data where ID = '{}'".format(id))
    pro_wor = cur.fetchall()[0][0]
    cur.reset()
    cur.execute("update data set Project_Working = {} where ID = {}".format(int(pro_wor)+1,id))
    conn.commit()
    cur.reset()
    cur.execute("select name from data where id = '{}'".format(id))
    body = """Dear Sir/Mam,
     
       We Have a New project that has proposed by our user. Try to cross check and i interested then Invest to make changes.
       
       Title : {}
       Description : {}
       
       Proposed by {}""".format(title,des,cur.fetchall()[0][0])
    
    cur.reset()
    cur.execute("select mail from investor_login")
    for i in cur:
        send_email("NEW PROJECT PROPOSAL",body,i[0])
    return cur_pro()

@app.route('/deleting/<id1>',methods = ['get','post'])
def delete(id1):
    global id
    if id=="":
        return index()
    cur.reset()
    cur.execute("select worker from projects where ID = '{}'".format(id1))
    temp_1 = cur.fetchall()[0][0]
    if len(temp_1)==1:
        return "CANNOT DELETE YOUR PROJECT"
    else:
        cur.reset()
        cur.execute("select worker from projects where ID = '{}'".format(id1))
        wor = cur.fetchall()[0][0].split(",")
        wor.remove(str(id))
        cur.reset()
        cur.execute("update projects set worker ='{}' where ID = '{}'".format(",".join(wor),id1))
        conn.commit()
        cur.reset()
        cur.execute("select Project_Working from data where ID = '{}'".format(id))
        pro_wor = cur.fetchall()[0][0]
        cur.reset()
        cur.execute("update data set Project_Working = {} where ID = {}".format(int(pro_wor)-1,id))
        conn.commit()
        cur.execute("select title,des from projects where id = '{}'".format(id1))
        temp_data = cur.fetchall()[0]
        send_email("DELETED SUCCESSFULLY","Title : {} \n Description : {}".format(temp_data[0],temp_data[1]),mail)
    return cur_pro()

#__________________________________________________________________________________________________
@app.route('/investor')
def login_inv():
    return render_template('investor_login.html')

@app.route('/investor_profile')
def inv_pro():
    global mail,id,inv
    inv = 1
    cur.reset()
    cur.execute("select * from investor where mail = '{}'".format(mail))
    data = cur.fetchall()[0]
    id = data[0]
    return render_template('Investor_profile.html',data = data)
@app.route('/investor_login', methods = ['post'])
def inv_check():
    global mail,id
    name = request.form.get('username')
    password = request.form.get('password')
    cur.reset()
    cur.execute("select * from investor_login")
    for i in cur:
        if i[0]==name and i[1]==password:
            mail = name
            return inv_pro()
    return 'INVALID CREDENTIAL'

@app.route('/my_investment')
def my_inv():
    global mail,id,inv
    if mail=="" or id=="" or inv==0:
        return index()
    cur.reset()
    temp = []
    cur.execute("select * from projects")
    for i in cur:
        print(i)
        if i[-1]!=None and id in i[-1]:
            temp.append(i)
    return render_template('my_investment.html',data = temp)

@app.route('/invest')
def inv():
    global mail,id,inv
    if mail=="" or id=="" or inv==0:
        return index()
    cur.reset()
    temp = []
    cur.execute("select * from projects")
    for i in cur:
        print(i)
        if i[-1]==None or id not in i[-1]:
            temp.append(i)
    return render_template('invest.html',data = temp)


@app.route('/inv_del/<id1>',methods = ['get','post'])
def delete_inv(id1):
    global id,mail,inv
    if id=="" and inv==0:
        return index()
    cur.reset()
    cur.execute("select investor from projects where ID = '{}'".format(id1))
    temp_1 = cur.fetchall()[0][0].split(",")
    if len(temp_1)==1:
        return "CANNOT DELETE YOUR PROJECT"
    cur.reset()
    cur.execute("select investor from projects where ID = '{}'".format(id1))
    wor = cur.fetchall()[0][0].split(",")
    wor.remove(str(id))
    cur.reset()
    cur.execute("update projects set investor ='{}' where ID = '{}'".format(",".join(wor),id1))
    conn.commit()
    cur.reset()
    cur.execute("select projects from investor where ID = '{}'".format(id))
    pro_wor = cur.fetchall()[0][0]
    cur.reset()
    cur.execute("update investor set projects = {} where ID = {}".format(int(pro_wor)-1,id))
    conn.commit()
    cur.execute("select title,des from projects where id = '{}'".format(id1))
    temp_data = cur.fetchall()[0]
    send_email("DELETED SUCCESSFULLY","Title : {} \n Description : {}".format(temp_data[0],temp_data[1]),mail)
    return my_inv()

@app.route('/add_invest/<id1>', methods=['GET', 'POST'])
def add_inv(id1):
    global id,mail,inv
    if inv==0 or id=="" or mail=="":
        return index()
    temp = str(id1)
    cur.reset()
    cur.execute("select investor from projects where id ='{}'".format(temp))
    data = cur.fetchall()[0][0]+","+str(id)
    cur.reset()
    cur.execute("select projects from investor where ID = '{}'".format(id))
    pro_wor = cur.fetchall()[0][0]
    cur.reset()
    cur.execute("update investor set projects = {} where ID = {}".format(int(pro_wor)+1,id))
    cur.reset()
    cur.execute("update projects set investor = '{}' where id = '{}'".format(data,temp))
    conn.commit()
    cur.execute("select title,des from projects where id = '{}'".format(id1))
    temp_data = cur.fetchall()[0]
    send_email("COLLABED SUCCESSFULLY","Title : {} \n Description : {}".format(temp_data[0],temp_data[1]),mail)
    return my_inv()
    


#__________________________________________________________________________________________________
            

@app.route('/add_project')
def add_project():
    global mail,id,inv
    title = request.form.get('title')
    des = request.form.get('desc')
    if mail=="" or id=="" or inv == 1:
        return index()
    
    return render_template('add_project.html')
@app.route('/collab_with_prjects')
def collab():
    global mail,id,inv
    if mail=="" or id=="" or inv == 1:
        return index()
    cur.reset()
    cur.execute("select * from projects;")
    temp = []
    for i in cur:
        if id not in i[3]:
            temp.append(i)
    print(temp)
    return render_template('collab_with_projects.html',data=temp)



@app.route('/current_investor')
def current_investor():
    global mail,id,inv
    if mail=="" or id=="" or inv==1:
        return index()
    cur.reset()
    cur.execute("select * from projects")
    cu1 = cur.fetchall()
    dup = []
    current_inv = []
    for i in cu1:
        print(i,id)
        if id in i[-2]:
            temp_inv = i[-1].split(',')
            for j in temp_inv:
                if j not in dup:
                    cur.reset()
                    cur.execute("select * from investor where id = '{}'".format(j))
                    current_inv.append(cur.fetchall()[0])
                    dup.append(j)
    return render_template('current_investor.html',data = current_inv)




@app.route('/current_project')
def cur_pro():
    global mail,id,inv
    if mail=="" or id=="" or inv==1:
        return index()
    cur.reset()
    cur.execute('select * from projects')
    temp = [] 
    
    for i in cur:
        print(i)
        if id in i[-2]:
            temp.append(list(i))
    for i in range(len(temp)):
        temp1 = temp[i][3]
        inv_temp = temp[i][4]
        worker = []
        inv_data = []
        print(temp1)
        for j in temp1.split(','):
            cur.reset()
            cur.execute("select name from data where ID = '{}'".format(j))
            worker.append(cur.fetchall()[0][0])
        for j in inv_temp.split(','):
            if j!='0' and j!="":
                print("select name from investor where ID = '{}'".format(j),j)
              
                cur.reset()
                cur.execute("select name from investor where ID = '{}'".format(j))
                x = cur.fetchall()[0][0]
                inv_data.append(x)
            
        temp[i][3] = ",".join(worker)
        temp[i][4] = ",".join(inv_data)
    print(temp)
    return render_template('current_project.html',data=temp)
@app.route('/request_investor')
def req_inv():
    global mail,id,inv
    if mail=="" or id=="" or inv==1:
        return index()
    cur.reset()
    cur.execute("select * from investor")
    return render_template('Request_investor.html',data = cur.fetchall())
@app.route('/req/<id1>', methods=['GET', 'POST'])
def raise_req(id1):
    global id
    if id=="":
        return index()
    cur.reset()
    cur.execute("select mail from investor where id = '{}'".format(id1))
    mail_id = cur.fetchall()[0][0]
    cur.reset()
    cur.execute('select * from projects')
    temp = [] 
    
    for i in cur:
        print(i)
        if id in i[-2]:
            temp.append(list(i))
    cur.reset()
    cur.execute("Select name from data where id = '{}'".format(id))
    sub = "REQUEST from {}".format(cur.fetchall()[0][0])
    body = "Projects: \n"
    cur.reset()
    cur.execute("select * from projects")
    for i in cur:
        if id in i[-2]:
            for j in i:
                body+=j+"\n"
            body+="________________________________________\n"
    body+="\nUser Details:\n\n"
    cur.reset()
    cur.execute("select * from data where id='{}'".format(id))
    for i in cur:
        for j in i:
            body+="\t\t{}\n".format(j)
    
    send_email(sub,body,mail_id)
    print(sub,body,mail_id)
    return "REQUEST RAISED SUCCESSFULLY"
@app.route('/collabing/<id1>', methods=['GET', 'POST'])
def fun(id1):
    global id,mail,inv
    if inv==1 or id=="" or mail=="":
        return index()
    temp = str(id1)
    cur.reset()
    cur.execute("select worker from projects where id ='{}'".format(temp))
    data = cur.fetchall()[0][0]+","+str(id)
    cur.reset()
    cur.execute("select Project_Working from data where ID = '{}'".format(id))
    pro_wor = cur.fetchall()[0][0]
    cur.reset()
    cur.execute("update data set Project_Working = {} where ID = {}".format(int(pro_wor)+1,id))
    cur.reset()
    cur.execute("update projects set worker = '{}' where id = '{}'".format(data,temp))
    conn.commit()
    cur.execute("select title,des from projects where id = '{}'".format(id1))
    temp_data = cur.fetchall()[0]
    send_email("COLLABED SUCCESSFULLY","Title : {} \n Description : {}".format(temp_data[0],temp_data[1]),mail)
    return collab()


if __name__ == '__main__':
    app.run(debug=True)
    