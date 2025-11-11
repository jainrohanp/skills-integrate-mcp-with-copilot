"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# Persistent database setup
from src.db import get_session, init_db
from src.models import Member, Activity, Signup
from sqlmodel import select

# Initialize DB and seed sample activities if needed
init_db()

def seed_activities():
    session = get_session()
    if session.exec(select(Activity)).first() is None:
        sample_activities = [
            Activity(name="Chess Club", description="Learn strategies and compete in chess tournaments", schedule="Fridays, 3:30 PM - 5:00 PM", max_participants=12),
            Activity(name="Programming Class", description="Learn programming fundamentals and build software projects", schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM", max_participants=20),
            Activity(name="Gym Class", description="Physical education and sports activities", schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", max_participants=30),
            Activity(name="Soccer Team", description="Join the school soccer team and compete in matches", schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM", max_participants=22),
            Activity(name="Basketball Team", description="Practice and play basketball with the school team", schedule="Wednesdays and Fridays, 3:30 PM - 5:00 PM", max_participants=15),
            Activity(name="Art Club", description="Explore your creativity through painting and drawing", schedule="Thursdays, 3:30 PM - 5:00 PM", max_participants=15),
            Activity(name="Drama Club", description="Act, direct, and produce plays and performances", schedule="Mondays and Wednesdays, 4:00 PM - 5:30 PM", max_participants=20),
            Activity(name="Math Club", description="Solve challenging problems and participate in math competitions", schedule="Tuesdays, 3:30 PM - 4:30 PM", max_participants=10),
            Activity(name="Debate Team", description="Develop public speaking and argumentation skills", schedule="Fridays, 4:00 PM - 5:30 PM", max_participants=12),
        ]
        session.add_all(sample_activities)
        session.commit()
    session.close()

seed_activities()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")



@app.get("/activities")
def get_activities():
    session = get_session()
    activities = session.exec(select(Activity)).all()
    result = {}
    for activity in activities:
        participants = session.exec(select(Member.email).join(Signup, Signup.member_id == Member.id).where(Signup.activity_id == activity.id)).all()
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": participants
        }
    session.close()
    return result



@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    session = get_session()
    activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
    if not activity:
        session.close()
        raise HTTPException(status_code=404, detail="Activity not found")

    member = session.exec(select(Member).where(Member.email == email)).first()
    if not member:
        member = Member(name=email.split('@')[0].capitalize(), email=email)
        session.add(member)
        session.commit()
        session.refresh(member)

    existing_signup = session.exec(select(Signup).where(Signup.activity_id == activity.id, Signup.member_id == member.id)).first()
    if existing_signup:
        session.close()
        raise HTTPException(status_code=400, detail="Student is already signed up")

    signup = Signup(member_id=member.id, activity_id=activity.id)
    session.add(signup)
    session.commit()
    session.close()
    return {"message": f"Signed up {email} for {activity_name}"}



@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    session = get_session()
    activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
    if not activity:
        session.close()
        raise HTTPException(status_code=404, detail="Activity not found")

    member = session.exec(select(Member).where(Member.email == email)).first()
    if not member:
        session.close()
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    signup = session.exec(select(Signup).where(Signup.activity_id == activity.id, Signup.member_id == member.id)).first()
    if not signup:
        session.close()
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    session.delete(signup)
    session.commit()
    session.close()
    return {"message": f"Unregistered {email} from {activity_name}"}
