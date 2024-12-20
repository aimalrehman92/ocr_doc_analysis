

# This is the main file for services built upon OCR technology.
# We create FASTAPI based api here and include the API routes from the "View" script inside the "src" folder.
# You can choose to run it on any port by discussing with DevOps.


import uvicorn
from fastapi import FastAPI
from app.src import view as ocr_apps
from starlette.middleware.cors import CORSMiddleware
from app.src.utilities import delete_expired_files
import asyncio


allowed_methods = ["GET", "POST"]

app = FastAPI(
    title="Python OCR applications for Document Analysis",
    description="Python OCR based Plagiarism Calculator",
    version="0.1.0",
    docs_url="/",
    redoc_url=None,
)

app.include_router(ocr_apps.router)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=allowed_methods,
                   allow_headers=['*'])


# Create a startup function to start the background task
async def startup():
    asyncio.create_task(delete_expired_files())

app.add_event_handler("startup", startup)


if __name__ == '__main__':
    uvicorn.run(app="main:app", host='0.0.0.0', port=5020, reload=True)


#Please run using the command in terminal:
#uvicorn app.main:app --host 0.0.0.0 --port 5020 --reload
