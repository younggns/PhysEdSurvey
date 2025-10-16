import csv
import os
from app import app, db, Participant, Essay, QuizQuestion, Feedback, SurveyQuestion

def init_db_from_csv(csv_filepath=f'{os.getcwd()}/static/data/feedback.csv'):
    """
    Initializes the database by reading participant data from a CSV file.
    
    The CSV file must have the following columns:
    'ID', 'essay', 'feedback-original', 'feedback-level1', 'feedback-level2'
    """
    if not os.path.exists(csv_filepath):
        print(f"Error: The file '{csv_filepath}' was not found.")
        print("Please create it and add your survey data.")
        return

    with app.app_context():
        # Drop all tables to start fresh
        db.drop_all()
        # Create all tables based on models
        db.create_all()

        # Open and read the CSV file
        with open(csv_filepath, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                # --- Create DB Objects for each row ---
                
                # 1. Create the Participant
                participant = Participant(id=row['ID'])
                
                # 2. Create the Essay and link it to the participant
                quiz_question = QuizQuestion(participant=participant, content=row['quiz_question'])
                essay = Essay(participant=participant, content=row['essay'])

                # 3. Create the three unique Feedback objects
                # feedback_orig = Feedback(content=row['feedback-original'])
                feedback_lvl1 = Feedback(content=row['feedback-level1'])
                feedback_lvl2 = Feedback(content=row['feedback-level2'])

                # 4. Create the SurveyQuestion, linking the participant to their specific feedback
                survey_question = SurveyQuestion(
                    participant=participant,
                    # feedback_a=feedback_orig,
                    feedback_b=feedback_lvl1,
                    feedback_c=feedback_lvl2
                )
                
                # Add all the new objects for this participant to the session
                # SQLAlchemy will handle the relationships and foreign keys
                db.session.add_all([
                    participant, 
                    quiz_question,
                    essay, 
                    # feedback_orig, 
                    feedback_lvl1, 
                    feedback_lvl2, 
                    survey_question
                ])

        # Commit all the changes to the database
        db.session.commit()

        print(f"Database initialized and seeded from '{csv_filepath}'.")
        print("You can now run 'python app.py' to start the web server.")
        print("Each participant can now access their survey directly via their unique URL, for example:")
        print("http://127.0.0.1:5000/survey/participant_id")


if __name__ == '__main__':
    # The script will look for 'survey_data.csv' in the same directory
    init_db_from_csv()