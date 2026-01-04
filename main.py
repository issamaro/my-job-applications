from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import init_db
from routes import personal_info, work_experiences, education, skills, projects
from routes.resumes import router as resumes_router, profile_router
from routes.job_descriptions import router as job_descriptions_router
from routes.photos import router as photos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="MyCV API", lifespan=lifespan)

# Include routers
app.include_router(personal_info.router)
app.include_router(work_experiences.router)
app.include_router(education.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(resumes_router)
app.include_router(profile_router)
app.include_router(job_descriptions_router)
app.include_router(photos_router)

# Serve static files
app.mount("/", StaticFiles(directory="public", html=True), name="public")
