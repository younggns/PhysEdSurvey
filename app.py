import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime # Add this import

# Initialize Flask App and Database
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'survey.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///survey.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---

class Participant(db.Model):
    """Represents a survey participant."""
    id = db.Column(db.String(80), primary_key=True)
    quiz_question = relationship("QuizQuestion", uselist=False, back_populates="participant")
    essay = relationship("Essay", uselist=False, back_populates="participant")
    survey_question = relationship("SurveyQuestion", uselist=False, back_populates="participant")
    responses = relationship("Response", back_populates="participant")

class QuizQuestion(db.Model):
    """Stores the question for each participant."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    participant_id = db.Column(db.String(80), ForeignKey('participant.id'), unique=True)
    participant = relationship("Participant", back_populates="quiz_question")

class Essay(db.Model):
    """Stores the essay for each participant."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    participant_id = db.Column(db.String(80), ForeignKey('participant.id'), unique=True)
    participant = relationship("Participant", back_populates="essay")

class Feedback(db.Model):
    """Stores individual feedback paragraphs."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

class SurveyQuestion(db.Model):
    """Defines which feedback options a participant sees."""
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(80), ForeignKey('participant.id'), unique=True)
    
    feedback_a_id = db.Column(db.Integer, ForeignKey('feedback.id'))
    feedback_b_id = db.Column(db.Integer, ForeignKey('feedback.id'))
    feedback_c_id = db.Column(db.Integer, ForeignKey('feedback.id'), nullable=True) # Optional 3rd feedback

    feedback_a = relationship("Feedback", foreign_keys=[feedback_a_id])
    feedback_b = relationship("Feedback", foreign_keys=[feedback_b_id])
    feedback_c = relationship("Feedback", foreign_keys=[feedback_c_id])
    
    participant = relationship("Participant", back_populates="survey_question")
    response = relationship("Response", uselist=False, back_populates="survey_question")


class Response(db.Model):
    """Stores the participant's submitted answers."""
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(80), ForeignKey('participant.id'))
    survey_question_id = db.Column(db.Integer, ForeignKey('survey_question.id'))
    ranking = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # Add this line

    participant = relationship("Participant", back_populates="responses")
    survey_question = relationship("SurveyQuestion", back_populates="response")


# --- Web Routes ---

@app.route('/survey/<participant_id>')
def survey(participant_id):
    """Displays the survey page for a specific participant."""
    participant = Participant.query.get(participant_id)
    if not participant:
        return "Participant not found.", 404

    # Fetch the specific question and associated data for this participant
    quiz_question = participant.quiz_question
    question = participant.survey_question
    essay = participant.essay

    if not question or not essay:
        return "Survey content not found for this participant.", 404
        
    return render_template('index.html', quiz_question=quiz_question, participant=participant, essay=essay, question=question)

@app.route('/submit', methods=['POST'])
def submit():
    """Handles survey submissions."""
    data = request.get_json()
    
    participant_id = data.get('participant_id')
    question_id = data.get('question_id')
    ranking = data.get('ranking')
    reason = data.get('reason')

    # Basic validation
    if not all([participant_id, question_id, ranking]):
        return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

    # Create and save the response
    new_response = Response(
        participant_id=participant_id,
        survey_question_id=question_id,
        ranking=ranking,
        reason=reason
        # The timestamp will be added automatically due to the 'default'
    )
    db.session.add(new_response)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Thank you! Your response has been recorded.'})


if __name__ == '__main__':
    # Create the database if it doesn't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)