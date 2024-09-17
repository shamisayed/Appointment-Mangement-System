from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Date, Time, UniqueConstraint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    appointment_no = Column(Integer, primary_key=True)
    doctor = Column(String(100), nullable=False)
    patient_name = Column(String(100), nullable=False)
    appointment_date = Column(Date, default=date.today)
    appointment_time = Column(Time, default=datetime.now().time)
    __table_args__ = (
        UniqueConstraint('doctor', 'appointment_date', 'appointment_time', name='uq_schedule_doctor_appointment'),
    )

class Doctor(db.Model):
    __tablename__ = 'doctor'
    doctor_id = db.Column(db.Integer, primary_key=True)
    doctorname = db.Column(db.String(100), nullable=False)
    doctor_speciality = db.Column(db.String(100), nullable=False)


# Routes for CRUD operations on Schedule

# GET all schedules route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_appointment', methods=['GET'])
def get_all_schedules():
    doc = Doctor.query.all()
    return render_template('add_appointment.html', doc=doc)

# POST create schedule route
@app.route('/create_schedule', methods=['POST'])
def create_new_schedule():
    data = request.form
    try:
        new_schedule = Schedule(
            doctor=data['doc'],
            patient_name=data['patient_name'],
            appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(data['appointment_time'], '%H:%M').time()
        )
        db.session.add(new_schedule)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Handle uniqueness constraint violation here
        return f"Error: {str(e)}", 400  # You can return a custom message
    return redirect("/view")

# GET view specific schedule route
@app.route('/view', methods=['GET'])
def view_specific_schedule():
    schedule = Schedule.query.all()
    return render_template('display_appointments.html', schedule=schedule)

@app.route("/add_doc",methods=['GET'])
def add_doc():
    return render_template('add_doctor.html')

@app.route('/create_doc', methods=['POST'])
def create_new_doc():
    data = request.form
    new_doctor = Doctor(doctorname=data['doctor_name'],
                            doctor_speciality=data['doctor_speciality'])
    db.session.add(new_doctor)
    db.session.commit()

    return redirect("/display_doctor")
@app.route('/display_doctor',methods=['GET'])
def display_doctor():
    doc = Doctor.query.all()
    return render_template('display_docs.html', doc=doc)
@app.route('/delete_appointment/<int:appointment_no>', methods=['POST'])
def delete_appointment(appointment_no):
    appointment = Schedule.query.get(appointment_no)
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
    return redirect('/view')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
