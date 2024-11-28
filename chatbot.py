import os
import nltk
from flask import Blueprint, request, jsonify
from models import User, ChatHistory, db
from auth import token_required
from mistralai.client import MistralClient
from datetime import datetime
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import time
from werkzeug.utils import secure_filename

# Configuración del directorio de datos de NLTK
NLTK_DATA_DIR = os.path.join(os.getcwd(), 'nltk_data')
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.append(NLTK_DATA_DIR)

def download_nltk_data():
    """Descarga los datos necesarios de NLTK con manejo de errores."""
    try:
        nltk.download('punkt', download_dir=NLTK_DATA_DIR, quiet=True)
        nltk.download('stopwords', download_dir=NLTK_DATA_DIR, quiet=True)
        nltk.download('averaged_perceptron_tagger', download_dir=NLTK_DATA_DIR, quiet=True)
    except Exception as e:
        print(f"Error descargando datos NLTK: {e}")
        return False
    return True

# Descargar datos de NLTK antes de inicializar el Blueprint
if not download_nltk_data():
    print("Advertencia: Falló la descarga de datos de NLTK. Algunas funciones pueden no funcionar correctamente.")

# Inicialización del Blueprint
chatbot_bp = Blueprint('chatbot', __name__)

# Configuración del cliente de Mistral
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise RuntimeError("Error: La variable de entorno MISTRAL_API_KEY no está configurada.")
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

# -------------------------------
# Funciones Auxiliares
# -------------------------------

def extract_topics(text):
    """Extrae temas principales del texto utilizando NLTK."""
    try:
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('spanish') + stopwords.words('english'))
        tagged = nltk.pos_tag(tokens)
        topics = [
            word for word, tag in tagged
            if word not in stop_words and len(word) > 3 and tag in ['NN', 'NNS', 'NNP', 'NNPS']
        ]
        return list(set(topics))
    except Exception as e:
        print(f"Error en la extracción de temas: {e}")
        return [text.lower()]

def find_similar_questions(current_question, user_id, limit=5):
    """Encuentra preguntas similares previas utilizando TF-IDF y similitud coseno."""
    history = ChatHistory.query.filter_by(user_id=user_id, helpful=True)\
        .order_by(ChatHistory.timestamp.desc()).all()

    if not history:
        return []

    previous_questions = [chat.message for chat in history]

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        all_questions = [current_question] + previous_questions
        tfidf_matrix = vectorizer.fit_transform(all_questions)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

        similar_interactions = []
        for idx in (-similarities).argsort()[:limit]:
            if similarities[idx] > 0.3:  # Umbral de similitud
                similar_interactions.append({
                    'question': history[idx].message,
                    'response': history[idx].response,
                    'similarity': similarities[idx],
                    'understanding': history[idx].user_understanding
                })

        return similar_interactions
    except Exception as e:
        print(f"Error encontrando preguntas similares: {e}")
        return []

def analyze_user_progress(user_id):
    """Analiza el progreso del usuario basado en su historial de interacciones."""
    recent_chats = ChatHistory.query.filter_by(user_id=user_id)\
        .order_by(ChatHistory.timestamp.desc())\
        .limit(20).all()

    if not recent_chats:
        return {
            'avg_complexity': 1,
            'understanding_level': 3,
            'preferred_topics': [],
            'learning_style': 'balanced',
            'learning_pace': 'normal',
            'mastery_scores': {}
        }

    avg_complexity = sum(chat.complexity_level or 1 for chat in recent_chats) / len(recent_chats)
    avg_understanding = sum(chat.user_understanding or 3 for chat in recent_chats) / len(recent_chats)

    topic_interactions = {}
    for chat in recent_chats:
        if chat.topic not in topic_interactions:
            topic_interactions[chat.topic] = []
        topic_interactions[chat.topic].append({
            'understanding': chat.user_understanding or 3,
            'helpful': chat.helpful,
            'timestamp': chat.timestamp
        })

    mastery_scores = {}
    for topic, interactions in topic_interactions.items():
        total_weight = 0
        weighted_score = 0
        for idx, interaction in enumerate(interactions):
            weight = 1 / (idx + 1)
            score = (interaction['understanding'] / 5.0) * (1.5 if interaction['helpful'] else 0.5)
            weighted_score += score * weight
            total_weight += weight
        mastery_scores[topic] = weighted_score / total_weight if total_weight > 0 else 0

    timestamps = [chat.timestamp for chat in recent_chats]
    if len(timestamps) > 1:
        time_diffs = [(t2 - t1).total_seconds() / 3600 for t1, t2 in zip(timestamps[1:], timestamps[:-1])]
        avg_time_between = np.mean(time_diffs)
        learning_pace = (
            'intensive' if avg_time_between < 24 else
            'regular' if avg_time_between < 72 else
            'casual'
        )
    else:
        learning_pace = 'normal'

    if len(recent_chats) > 5:
        understanding_trend = np.polyfit(
            range(len(recent_chats)),
            [chat.user_understanding or 3 for chat in recent_chats],
            1
        )[0]
        learning_style = (
            'advancing' if understanding_trend > 0.1 else
            'stable' if abs(understanding_trend) <= 0.1 else
            'struggling'
        )
    else:
        learning_style = 'balanced'

    topics = []
    for chat in recent_chats:
        if chat.helpful:
            topics.extend(extract_topics(chat.message))

    preferred_topics = [
        topic for topic, count in sorted(
            [(t, topics.count(t)) for t in set(topics)],
            key=lambda x: x[1],
            reverse=True
        )[:5]
    ]

    return {
        'avg_complexity': avg_complexity,
        'understanding_level': avg_understanding,
        'preferred_topics': preferred_topics,
        'learning_style': learning_style,
        'learning_pace': learning_pace,
        'mastery_scores': mastery_scores
    }

def preprocess_text(text):
    """Preprocesa el texto de entrada eliminando errores comunes y normalizando."""
    if not text:
        return ""
    text = ' '.join(text.split()).lower()
    common_typos = {
        'q ': 'que ',
        'xq': 'porque',
        'k ': 'que ',
        'tb ': 'también ',
    }
    for typo, correction in common_typos.items():
        text = text.replace(typo, correction)
    return text

# -------------------------------
# Rutas del Blueprint
# -------------------------------

@chatbot_bp.route('/chat', methods=['POST'])
@token_required
def chat(current_user):
    """Maneja la interacción del usuario con el chatbot."""
    start_time = time.time()
    message = request.form.get('message', '')
    file = request.files.get('file')

    if not message and not file:
        return jsonify({'error': 'No se proporcionó ningún mensaje o archivo'}), 400

    file_info = ""
    if file and file.filename:
        filename = secure_filename(file.filename)
        file_info = f"\nArchivo adjunto: {filename}"

    processed_message = preprocess_text(message + file_info if file_info else message)
    user_progress = analyze_user_progress(current_user.id)
    similar_interactions = find_similar_questions(processed_message, current_user.id)
    user_type = current_user.user_type

    messages = get_tailored_prompt(user_type, processed_message, user_progress, similar_interactions)

    try:
        chat_response = mistral_client.chat(
            model="mistral-tiny",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        ai_response = chat_response.choices[0].message.content

        topics = extract_topics(processed_message)
        main_topic = topics[0] if topics else "general"
        response_time = time.time() - start_time

        chat_entry = ChatHistory(
            user_id=current_user.id,
            message=message + file_info if file_info else message,
            response=ai_response,
            complexity_level=user_progress['avg_complexity'],
            topic=main_topic,
            response_time=response_time,
            preferred_pace=user_progress['learning_pace']
        )
        db.session.add(chat_entry)
        db.session.commit()

        return jsonify({
            'response': ai_response,
            'chat_id': chat_entry.id,
            'complexity_level': user_progress['avg_complexity']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/chat_feedback', methods=['POST'])
@token_required
def submit_feedback(current_user):
    """Permite al usuario proporcionar retroalimentación sobre una interacción previa."""
    data = request.json
    chat_id = data.get('chat_id')
    helpful = data.get('helpful')
    understanding = data.get('understanding')

    if not chat_id:
        return jsonify({'error': 'Chat ID is required'}), 400

    try:
        chat = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first()
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404

        chat.helpful = helpful if helpful is not None else chat.helpful
        if understanding:
            chat.user_understanding = understanding

        if helpful is not None and understanding:
            chat.interaction_quality = (helpful + (understanding / 5)) / 2

        if chat.timestamp:
            session_duration = (datetime.utcnow() - chat.timestamp).total_seconds()
            chat.session_duration = int(session_duration)

        db.session.commit()
        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/learning_report', methods=['GET'])
@token_required
def get_learning_report(current_user):
    """Genera un reporte del progreso del aprendizaje del usuario."""
    user_progress = analyze_user_progress(current_user.id)
    if not user_progress:
        return jsonify({'error': 'Could not generate learning report'}), 404
    return jsonify(user_progress), 200