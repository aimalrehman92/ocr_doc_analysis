
import uvicorn
from fastapi import FastAPI
from app.src import view as ocr_apps
from starlette.middleware.cors import CORSMiddleware

allowed_methods = ["GET", "POST"]

app = FastAPI(
    title="Python OCR applications",
    description="Alivia-OCR based applications",
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


if __name__ == '__main__':
    uvicorn.run(app="main:app", host='0.0.0.0', port=5020, reload=True)


#Please run using the command in terminal:
#uvicorn app.main:app --host 0.0.0.0 --port 5020 --reload
