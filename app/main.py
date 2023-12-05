
from app.src.f1_plagiarism_calc import app
from app.src.f1_plagiarism_calc import main_percentage
from app.src.f1_plagiarism_calc import main_text_return

from app.src.f2_correspondence_checker import main_correspondence

#@app.route('/', methods=['GET', 'POST'])
def main():

    with app.app_context():
        
        # F1 plagiarism calculator
        result = main_percentage()
        result = main_text_return()

        # F2 correspondence checker
        result = main_correspondence()

        print(result)

    return result


if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000, debug=True)