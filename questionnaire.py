from flask import Blueprint, request, jsonify
from models import User, QuestionnaireResponse, db
from auth import token_required

questionnaire_bp = Blueprint('questionnaire', __name__)

def classify_user(responses):
    scores = {
        'estructurado': 0,
        'explorador': 0,
        'intensivo': 0
    }
    
    # Análisis temporal (20 puntos)
    if responses['study_time'] == 'A':
        scores['estructurado'] += 10
    elif responses['study_time'] == 'C':
        scores['intensivo'] += 10
    else:
        scores['explorador'] += 10
    
    if responses['session_duration'] == 'B':
        scores['estructurado'] += 5
    elif responses['session_duration'] == 'C':
        scores['intensivo'] += 5
    else:
        scores['explorador'] += 5
    
    if responses['learning_pace'] == 'A':
        scores['estructurado'] += 5
    elif responses['learning_pace'] == 'C':
        scores['intensivo'] += 5
    else:
        scores['explorador'] += 5
    
    # Análisis metodológico (30 puntos)
    if responses['learning_style'] == 'A':
        scores['estructurado'] += 10
    elif responses['learning_style'] == 'B':
        scores['explorador'] += 10
    else:
        scores['intensivo'] += 10
    
    if responses['content_format'] == 'A':
        scores['estructurado'] += 5
    elif responses['content_format'] == 'B':
        scores['explorador'] += 5
    else:
        scores['intensivo'] += 5
    
    if responses['feedback_preference'] == 'A':
        scores['estructurado'] += 5
    elif responses['feedback_preference'] == 'B':
        scores['explorador'] += 5
    else:
        scores['intensivo'] += 5
    
    # Análisis motivacional (25 puntos)
    if responses['learning_goals'] == 'A':
        scores['estructurado'] += 5
    elif responses['learning_goals'] == 'B':
        scores['explorador'] += 5
    else:
        scores['intensivo'] += 5
    
    if responses['motivators'] == 'A':
        scores['estructurado'] += 5
    elif responses['motivators'] == 'B':
        scores['explorador'] += 5
    else:
        scores['intensivo'] += 5
    
    if responses['challenges'] == 'A':
        scores['estructurado'] += 5
    elif responses['challenges'] == 'B':
        scores['explorador'] += 5
    else:
        scores['intensivo'] += 5
    
    # Análisis de contenido (25 puntos)
    if responses['interest_areas'] == 'A':
        scores['estructurado'] += 5
    elif responses['interest_areas'] == 'B':
        scores['explorador'] += 5
    else:
        scores['intensivo'] += 5
    
    if responses['experience_level'] == 'B':
        scores['estructurado'] += 5
    elif responses['experience_level'] == 'C':
        scores['intensivo'] += 5
    else:
        scores['explorador'] += 5
    
    if responses['learning_tools'] == 'A':
        scores['estructurado'] += 5
    elif responses['learning_tools'] == 'B':
        scores['explorador'] += 5
    else:
        scores['intensivo'] += 5

    # Map profile types to user types for chatbot interaction
    profile_type = max(scores.items(), key=lambda x: x[1])[0]
    user_type_mapping = {
        'estructurado': 'ESTRUCTURADO',
        'explorador': 'EXPLORADOR',
        'intensivo': 'INTENSIVO'
    }
    
    return user_type_mapping[profile_type]

@questionnaire_bp.route('/submit_questionnaire', methods=['POST'])
@token_required
def submit_questionnaire(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = [
            'study_time', 'session_duration', 'learning_pace',
            'learning_style', 'content_format', 'feedback_preference',
            'learning_goals', 'motivators', 'challenges',
            'interest_areas', 'experience_level', 'learning_tools'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Create new questionnaire response
        new_response = QuestionnaireResponse(
            user_id=current_user.id,
            study_time=data['study_time'],
            session_duration=data['session_duration'],
            learning_pace=data['learning_pace'],
            learning_style=data['learning_style'],
            content_format=data['content_format'],
            feedback_preference=data['feedback_preference'],
            learning_goals=data['learning_goals'],
            motivators=data['motivators'],
            challenges=data['challenges'],
            interest_areas=data['interest_areas'],
            experience_level=data['experience_level'],
            learning_tools=data['learning_tools']
        )
        
        db.session.add(new_response)
        
        # Determine user type based on responses
        user_type = classify_user(data)
        current_user.user_type = user_type
        current_user.questionnaire_completed = True
        
        db.session.commit()
        return jsonify({
            'message': 'Questionnaire submitted successfully',
            'user_type': user_type
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error saving questionnaire: {str(e)}'}), 500

@questionnaire_bp.route('/get_user_profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    if not current_user.questionnaire_completed:
        return jsonify({'message': 'Questionnaire not completed'}), 400

    questionnaire = QuestionnaireResponse.query.filter_by(user_id=current_user.id).first()
    
    if not questionnaire:
        return jsonify({'message': 'Questionnaire data not found'}), 404
    
    profile = {
        'email': current_user.email,
        'user_type': current_user.user_type,
        'questionnaire_responses': {
            'study_time': questionnaire.study_time,
            'session_duration': questionnaire.session_duration,
            'learning_pace': questionnaire.learning_pace,
            'learning_style': questionnaire.learning_style,
            'content_format': questionnaire.content_format,
            'feedback_preference': questionnaire.feedback_preference,
            'learning_goals': questionnaire.learning_goals,
            'motivators': questionnaire.motivators,
            'challenges': questionnaire.challenges,
            'interest_areas': questionnaire.interest_areas,
            'experience_level': questionnaire.experience_level,
            'learning_tools': questionnaire.learning_tools
        }
    }
    
    return jsonify(profile), 200
