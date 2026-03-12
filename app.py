from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from google import genai
import PyPDF2
from werkzeug.utils import secure_filename

# Forcer le chargement du .env depuis le répertoire de ce script
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

app = Flask(__name__)

# Init Gemini
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

CLIENT_SYSTEM_PROMPT = """
Tu es Sophie, la chargée d'accueil de l'hôtel Madayann.
Tu ne dois JAMAIS dire que tu es une Intelligence Artificielle. Tu es une conseillère humaine professionnelle.
Réponds de manière joviale, enthousiaste et très concise.
Tes réponses seront lues à haute voix, elles doivent donc ressembler à de vraies phrases orales (pas de listes complexes, mais des énumérations fluides).
Adresse de l'hôtel : 3ème entrée Ndamba.
Horaires : ouverts 24h/24 et 7j/7.
Chambres : Double (20 000 F CFA), Simple (15 000 F CFA), Suite (35 000 F CFA).
Restauration (sur réservation) : Petit déjeuner (5000 F CFA), Déjeuner (12000 F CFA), Dîner (12000 F CFA).
Équipements : salle de réunion, parking, wifi gratuit.
Service de buanderie (lavage et repassage) : 3000 F CFA.
Si la personne veut prendre une réservation ou obtenir des infos, réponds à sa demande, puis demande toujours son numéro de téléphone pour lui envoyer un SMS récapitulatif.
"""

# Dictionnaire simple pour garder en mémoire la conversation par utilisateur
sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/setup', methods=['POST'])
def setup():
    activity = request.form.get('activity', 'Entreprise')
    name = request.form.get('name', 'Nom à définir')
    hours = request.form.get('hours', 'Non spécifié')
    tone = request.form.get('tone', 'Professionnel et courtois')
    details = request.form.get('details', '')
    
    pdf_text = ""
    if 'document' in request.files:
        file = request.files['document']
        if file.filename != '':
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text() + "\n"
            except Exception as e:
                print(f"Erreur Lecture PDF: {e}")
                
    # Demande à Gemini de fabriquer le prompt d'instruction parfait
    prompt_builder = f"""
    Crée un 'System Prompt' (instructions de comportement pour un agent vocal IA) basé sur ces informations:
    - Type d'activité: {activity}
    - Nom de l'entreprise: {name}
    - Horaires d'ouverture: {hours}
    - Ton de l'assistant: {tone}
    - Détails supplémentaires fournis par le client: {details}
    - Informations extraites du document PDF (tarifs, services): {pdf_text[:2500]} 
    
    Ton rôle: Rédiger le System Prompt final.
    Ce System Prompt s'adressera DIRECTEMENT à l'agent qui va le lire. Utilise "Tu es...".
    Le prénom de l'agent est Sophie.
    REGLES IMPORTANTES: 
    1. L'agent ne doit JAMAIS dire qu'il est une "intelligence artificielle" ou un "robot". S'il doit se présenter, il utilise un titre élégant comme "Chargée d'accueil" ou "Conseillère".
    2. L'agent doit répondre à l'oral (conversations fluides, concises, d'humain à humain, SANS AUCUNE LISTE NI PUCE).
    3. Avant de raccrocher ou lorsqu'elle valide une information, l'agent DOIT systématiquement demander les coordonnées de l'appelant (Numéro de téléphone) en expliquant que c'est pour lui envoyer un SMS de confirmation/récapitulatif. C'est très rassurant.
    Génère UNIQUEMENT le texte du System Prompt, pas de markdown autour.
    """
    
    try:
        # On génère le prompt personnalisé
        ai_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_builder
        )
        custom_system_prompt = ai_response.text
        
        # On crée une nouvelle session de chat avec ce prompt
        import uuid
        session_id = "session_" + str(uuid.uuid4())
        
        sessions[session_id] = client.chats.create(
            model="gemini-2.5-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction=custom_system_prompt,
                temperature=0.7,
            )
        )
        
        return jsonify({'success': True, 'session_id': session_id, 'prompt': custom_system_prompt})
    except Exception as e:
        print(f"Erreur Setup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_text = data.get('text', '')
    session_id = data.get('session_id', 'default_session')
    
    if not user_text:
        return jsonify({'response': "Je n'ai pas entendu ce que vous avez dit."})
        
    # Initialisation de la session sur la première requête
    if session_id not in sessions:
        sessions[session_id] = client.chats.create(
            model="gemini-2.5-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction=CLIENT_SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
        
    try:
        response = sessions[session_id].send_message(user_text)
        return jsonify({'response': response.text})
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        return jsonify({'response': "Je suis désolée, j'ai une petite perte de connexion. Pouvez-vous répéter ?"})

if __name__ == '__main__':
    print("🚀 Démarrage du serveur Web CallGenius sur http://127.0.0.1:5001")
    app.run(port=5001, debug=True)
