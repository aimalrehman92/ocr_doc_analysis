
from fastapi import APIRouter

from app.src.f1_plagiarism_calc import main_percentage
from app.src.f1_plagiarism_calc import main_text_return
from app.src.f2_correspondence_checker import main_correspondence
from app.src.f3_AI_polish_calc import main_AI_polish_calculator



router = APIRouter(
    tags=["Alivia-AI-DS-Service"],
    responses={404: {"description": "Not found"}},
)


@router.post("/plagiarism_calculation")
async def plagiarism_calculator_1(data: dict):
    result = main_percentage(data)
    return result

@router.post("/return_plagiarism_text")
async def plagiarism_calculator_2(data: dict):
    result = main_text_return(data)
    return result


@router.post("/prepay_correspondance_check")
async def correspondence_checker_2(data: dict):
    result = main_correspondence(data)
    return result


@router.post("/ai_polish_calculator")
async def ai_polish_checker(data: dict):
    result = main_AI_polish_calculator(data)
    return result



