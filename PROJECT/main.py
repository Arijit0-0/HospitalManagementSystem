import os
import tempfile
from datetime import date, datetime

from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
# from flask_mail import Mail
import json



app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hmsprojects')


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# SMTP MAIL SERVER SETTINGS

# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME="add your gmail-id",
#     MAIL_PASSWORD="add your gmail-password"
# )
# mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




database_url = os.environ.get('DATABASE_URL')
use_sqlite = os.environ.get('USE_SQLITE', '').lower() == 'true'
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', '')
db_host = os.environ.get('DB_HOST', '127.0.0.1')
db_name = os.environ.get('DB_NAME', 'hms')

if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
elif use_sqlite:
    sqlite_path = os.environ.get('SQLITE_PATH') or os.path.join(tempfile.gettempdir(), 'careaxis.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    usertype=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(150))
    number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100))
    doctorname=db.Column(db.String(100))
    dept=db.Column(db.String(150))

class Trigr(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timestamp=db.Column(db.String(50))


DEFAULT_DOCTORS = [
    ("haiderup@gmail.com", "Dr Haider Abbas", "Head of Emergency Medicine"),
    ("sunitasharma2381@gmail.com", "Dr Sunita Sharma", "Associate Professor, Musculoskeletal Physiotherapy"),
    ("alokguptaonco@gmail.com", "Dr Alok Gupta", "Senior Director & Head, Medical Oncology"),
    ("rachna_anila@yahoo.co.in", "Dr Anil Agarwal", "HOD, Orthopaedic Surgery"),
    ("drkvchalam99@yahoo.com", "Dr K. Venkata Chalam", "Honorary Secretary General (Dermatology)"),
    ("jbetkerur@gmail.com", "Dr Jayadev Betkerur", "President Elect (Dermatology)"),
    ("dermarao@gmail.com", "Dr P. Narasimha Rao", "Immediate Past President (Dermatology)"),
    ("manjunath576117@yahoo.co.in", "Dr Manjunath Shenoy", "Vice President (Dermatology)"),
    ("drkrishnanikhil@gmail.com", "Dr Krishna Nikhil", "General Medicine"),
    ("anuj_kodnani@yahoo.co.in", "Dr Anuj Harish Kodnani", "Ophthalmology"),
    ("manas.r.mishra.afmc@gmail.com", "Dr Manas Ranjan Mishra", "Paediatrics"),
    ("ninnyjames143@gmail.com", "Dr Nimmy Maria James", "Biochemistry"),
    ("nmanuraj@gmail.com", "Dr Manuraj M. Krishnan", "General Medicine"),
    ("balu16marhta@gmail.com", "Dr Martha Balakrishna", "Orthopaedics"),
    ("dr.pradheep@gmail.com", "Dr Pradeep K.", "Otorhinolaryngology (ENT)"),
    ("dr.priyapulwo@gmail.com", "Dr Priya Darshini S.", "Respiratory Medicine"),
    ("aditibhatia26@gmail.com", "Dr Aditi Bhatia", "General Practitioner"),
    ("hitesh2arora@gmail.com", "Dr Hitesh Arora", "General Practitioner"),
    ("drkaushikvinod@gmail.com", "Dr Kaushik Vinod", "General Practitioner"),
    ("dranupamkumarv@gmail.com", "Dr Anupam Kumar", "General Practitioner"),
]


def admin_required():
    if not current_user.is_authenticated or current_user.usertype != "Admin":
        flash("Admin access is required for that page.", "warning")
        return redirect(url_for('index'))
    return None


def get_appointment_status(booking):
    try:
        booking_date = datetime.strptime(str(booking.date), "%Y-%m-%d").date()
    except ValueError:
        return "Pending Review"

    today = date.today()
    if booking_date < today:
        return "Completed"
    if booking_date == today:
        return "Today"
    return "Upcoming"


def summarize_statuses(bookings):
    summary = {"Completed": 0, "Today": 0, "Upcoming": 0, "Pending Review": 0}
    for booking in bookings:
        summary[get_appointment_status(booking)] += 1
    return summary


def split_specialty_and_designation(label):
    if not label:
        return {"specialty": "", "designation": ""}

    label = str(label).strip()

    if "(" in label and ")" in label:
        specialty = label[label.find("(") + 1:label.find(")")].strip()
        designation = label[:label.find("(")].strip(" ,-")
        return {"specialty": specialty, "designation": designation}

    if "," in label:
        designation, specialty = label.rsplit(",", 1)
        return {"specialty": specialty.strip(), "designation": designation.strip()}

    lowered = label.lower()
    if lowered.startswith("head of "):
        return {"specialty": label[8:].strip(), "designation": "Head"}

    return {"specialty": label, "designation": ""}


def build_doctor_profiles(doctors):
    profiles = []
    for doctor in doctors:
        parts = split_specialty_and_designation(doctor.dept)
        profiles.append({
            "did": doctor.did,
            "doctorname": doctor.doctorname,
            "email": doctor.email,
            "designation": parts["designation"],
            "specialty": parts["specialty"],
            "full_department": doctor.dept,
        })
    return profiles


def ensure_seed_data():
    db.create_all()

    admin_user = User.query.filter_by(email='admin@careaxis.local').first()
    if not admin_user:
        admin_user = User(
            username='System Admin',
            usertype='Admin',
            email='admin@careaxis.local',
            password=generate_password_hash('Admin@123'),
        )
        db.session.add(admin_user)

    if Doctors.query.count() == 0:
        for email, doctorname, dept in DEFAULT_DOCTORS:
            db.session.add(Doctors(email=email, doctorname=doctorname, dept=dept))

    db.session.commit()


with app.app_context():
    ensure_seed_data()


# shared dashboard metrics
def get_dashboard_metrics():
    total_doctors = Doctors.query.count()
    total_patients = Patients.query.count()
    total_users = User.query.count()
    total_activity = Trigr.query.count()
    latest_bookings = Patients.query.order_by(Patients.pid.desc()).limit(5).all()
    all_bookings = Patients.query.all()
    doctors = Doctors.query.order_by(Doctors.doctorname.asc()).all()
    doctor_profiles = build_doctor_profiles(doctors)
    specialty_counts = {}
    for profile in doctor_profiles:
        specialty_counts[profile["specialty"]] = specialty_counts.get(profile["specialty"], 0) + 1
    department_rows = sorted(specialty_counts.items(), key=lambda item: (-item[1], item[0]))

    return {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_users": total_users,
        "total_activity": total_activity,
        "latest_bookings": latest_bookings,
        "doctors": doctor_profiles,
        "department_rows": department_rows,
        "status_summary": summarize_statuses(all_bookings),
    }


# here we will pass endpoints and run the fuction
@app.route('/')
def index():
    metrics = get_dashboard_metrics()
    return render_template('index.html', metrics=metrics, appointment_status=get_appointment_status)
    


@app.route('/doctors',methods=['POST','GET'])
@login_required
def doctors():
    access_redirect = admin_required()
    if access_redirect:
        return access_redirect

    if request.method=="POST":

        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')

        # query=db.engine.execute(f"INSERT INTO `doctors` (`email`,`doctorname`,`dept`) VALUES ('{email}','{doctorname}','{dept}')")
        query=Doctors(email=email,doctorname=doctorname,dept=dept)
        db.session.add(query)
        db.session.commit()
        flash("Information is Stored","primary")

    return render_template('doctor.html')


@app.route('/directory')
def directory():
    doctors_list = Doctors.query.order_by(Doctors.doctorname.asc()).all()
    doctor_profiles = build_doctor_profiles(doctors_list)
    specialty_counts = {}
    for profile in doctor_profiles:
        specialty_counts[profile["specialty"]] = specialty_counts.get(profile["specialty"], 0) + 1
    department_rows = sorted(specialty_counts.items(), key=lambda item: item[0])
    return render_template('directory.html', doctors=doctor_profiles, department_rows=department_rows)



@app.route('/patients',methods=['POST','GET'])
@login_required
def patient():
    # doct=db.engine.execute("SELECT * FROM `doctors`")
    doct=Doctors.query.all()
    doctor_profiles = build_doctor_profiles(doct)
    specialty_options = sorted({profile["specialty"] for profile in doctor_profiles if profile["specialty"]})

    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        # subject="HOSPITAL MANAGEMENT SYSTEM"
        if len(number)<10 or len(number)>10:
            flash("Please give 10 digit number")
            return render_template('patient.html', doct=doctor_profiles, specialty_options=specialty_options)
  

        # query=db.engine.execute(f"INSERT INTO `patients` (`email`,`name`,	`gender`,`slot`,`disease`,`time`,`date`,`dept`,`number`) VALUES ('{email}','{name}','{gender}','{slot}','{disease}','{time}','{date}','{dept}','{number}')")
        query=Patients(email=email,name=name,gender=gender,slot=slot,disease=disease,time=time,date=date,dept=dept,number=number)
        db.session.add(query)
        db.session.commit()
        
        # mail starts from here

        # mail.send_message(subject, sender=params['gmail-user'], recipients=[email],body=f"YOUR bOOKING IS CONFIRMED THANKS FOR CHOOSING US \nYour Entered Details are :\nName: {name}\nSlot: {slot}")



        flash("Booking Confirmed","info")


    return render_template('patient.html', doct=doctor_profiles, specialty_options=specialty_options)


@app.route('/bookings')
@login_required
def bookings(): 
    em=current_user.email
    if current_user.usertype=="Doctor" or current_user.usertype=="Admin":
        # query=db.engine.execute(f"SELECT * FROM `patients`")
        query=Patients.query.all()
        return render_template('booking.html',query=query, appointment_status=get_appointment_status)
    else:
        # query=db.engine.execute(f"SELECT * FROM `patients` WHERE email='{em}'")
        query=Patients.query.filter_by(email=em).all()
        print(query)
        return render_template('booking.html',query=query, appointment_status=get_appointment_status)
    


@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):    
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        # db.engine.execute(f"UPDATE `patients` SET `email` = '{email}', `name` = '{name}', `gender` = '{gender}', `slot` = '{slot}', `disease` = '{disease}', `time` = '{time}', `date` = '{date}', `dept` = '{dept}', `number` = '{number}' WHERE `patients`.`pid` = {pid}")
        post=Patients.query.filter_by(pid=pid).first()
        post.email=email
        post.name=name
        post.gender=gender
        post.slot=slot
        post.disease=disease
        post.time=time
        post.date=date
        post.dept=dept
        post.number=number
        db.session.commit()

        flash("Slot is Updates","success")
        return redirect('/bookings')
        
    posts=Patients.query.filter_by(pid=pid).first()
    return render_template('edit.html',posts=posts)


@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    # db.engine.execute(f"DELETE FROM `patients` WHERE `patients`.`pid`={pid}")
    query=Patients.query.filter_by(pid=pid).first()
    db.session.delete(query)
    db.session.commit()
    flash("Slot Deleted Successful","danger")
    return redirect('/bookings')






@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        usertype=request.form.get('usertype')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')

        encpassword = generate_password_hash(password)
        myquery=User(username=username,usertype=usertype,email=email,password=encpassword)
        db.session.add(myquery)
        db.session.commit()
        flash("Signup Succes Please Login","success")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        valid_password = False
        if user:
            if user.password.startswith("pbkdf2:") or user.password.startswith("scrypt:"):
                valid_password = check_password_hash(user.password, password)
            else:
                valid_password = user.password == password

        if user and valid_password:
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    





    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'
    

@app.route('/details')
@login_required
def details():
    access_redirect = admin_required()
    if access_redirect:
        return access_redirect
    posts=Trigr.query.all()
    # posts=db.engine.execute("SELECT * FROM `trigr`")
    return render_template('trigers.html',posts=posts)


@app.route('/reports')
@login_required
def reports():
    access_redirect = admin_required()
    if access_redirect:
        return access_redirect
    slot_rows = (
        db.session.query(Patients.slot, db.func.count(Patients.pid))
        .group_by(Patients.slot)
        .order_by(db.func.count(Patients.pid).desc())
        .all()
    )
    department_rows = (
        db.session.query(Patients.dept, db.func.count(Patients.pid))
        .group_by(Patients.dept)
        .order_by(db.func.count(Patients.pid).desc())
        .all()
    )
    recent_patients = Patients.query.order_by(Patients.pid.desc()).limit(8).all()

    return render_template(
        'reports.html',
        slot_rows=slot_rows,
        department_rows=department_rows,
        recent_patients=recent_patients,
        appointment_status=get_appointment_status,
        status_summary=summarize_statuses(Patients.query.all()),
    )


@app.route('/admin')
@login_required
def admin_dashboard():
    access_redirect = admin_required()
    if access_redirect:
        return access_redirect

    metrics = get_dashboard_metrics()
    recent_users = User.query.order_by(User.id.desc()).limit(8).all()
    recent_activity = Trigr.query.order_by(Trigr.tid.desc()).limit(8).all()
    return render_template(
        'admin.html',
        metrics=metrics,
        recent_users=recent_users,
        recent_activity=recent_activity,
        appointment_status=get_appointment_status,
    )


@app.route('/search',methods=['POST','GET'])
@login_required
def search():
    if request.method=="POST":
        query=request.form.get('search')
        doctors_list = Doctors.query.order_by(Doctors.doctorname.asc()).all()
        doctor_profiles = build_doctor_profiles(doctors_list)
        query_lower = query.strip().lower()
        name = next((profile for profile in doctor_profiles if query_lower in profile["doctorname"].lower()), None)
        dept = next((profile for profile in doctor_profiles if query_lower in profile["specialty"].lower() or query_lower in profile["designation"].lower()), None)
        if name or dept:

            flash("Doctor is Available","info")
        else:

            flash("Doctor is Not Available","danger")
    metrics = get_dashboard_metrics()
    return render_template('index.html', metrics=metrics, appointment_status=get_appointment_status)






if __name__ == "__main__":
    app.run(debug=True)
