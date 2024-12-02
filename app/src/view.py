
from fastapi import APIRouter
#import asyncio
from app.src.f1_plagiarism_calc import main_percentage
from app.src.f1_plagiarism_calc import main_text_return
#from app.src.utilities import delete_expired_files

router = APIRouter(
    tags=["Plagiarism Calculator"],
    responses={404: {"Get Request": "Welcome to OCR based intelligent document procrssing units"}},
)

@router.post("/plagiarism_calculation")
async def plagiarism_calculator_1(data: dict):
    result = main_percentage(data)
    return result

@router.post("/return_plagiarism_text")
async def plagiarism_calculator_2(data: dict):
    result = main_text_return(data)
    return result

