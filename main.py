import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging to show INFO level for services
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t%(name)s - %(message)s",
)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import init_db
from routes import users, work_experiences, education, skills, projects, languages
from routes.resumes import router as resumes_router, profile_router
from routes.jobs import router as jobs_router
from routes.photos import router as photos_router
from routes.profile_import import router as profile_import_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="MyCV API", lifespan=lifespan)

# Include routers
app.include_router(users.router)
app.include_router(work_experiences.router)
app.include_router(education.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(languages.router)
app.include_router(resumes_router)
app.include_router(profile_router)
app.include_router(jobs_router)
app.include_router(photos_router)
app.include_router(profile_import_router)

# Serve static files
app.mount("/", StaticFiles(directory="public", html=True), name="public")
