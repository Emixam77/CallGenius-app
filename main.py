import speech_recognition as sr
from gtts import gTTS
import pygame
import time
import os
from dotenv import load_dotenv
from google import genai

# Forcer le chargement du .env depuis le répertoire de ce script
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

class VoiceAgent:
    def __init__(self, system_prompt):
        # 1. Init Speaker (pygame pour lire l'audio généré par gTTS)
        pygame.mixer.init()
        
        # 2. Init Listener (SpeechRecognition)
        self.recognizer = sr.Recognizer()
        
        # 3. Init Thinker (Gemini)
        # Assurez-vous d'avoir GEMINI_API_KEY dans votre fichier .env
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.system_prompt = system_prompt
        self.chat_session = self.client.chats.create(
            model="gemini-2.5-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=0.7,
            )
        )

    def speak(self, text):
        """ The Speaker : Google Text-to-Speech """
        print(f"🤖 IA: {text}")
        try:
            tts = gTTS(text=text, lang="fr", slow=False)
            filename = "temp_voice.mp3"
            tts.save(filename)
            
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Attendre la fin de la lecture
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Libérer le fichier pour pouvoir l'écraser au coup suivant
            pygame.mixer.music.unload()
            if os.path.exists(filename):
                os.remove(filename)
                
        except Exception as e:
            print(f"Erreur Audio: {e}")

    def listen(self):
        """ The Listener : Speech-to-Text """
        with sr.Microphone() as source:
            print("🎤 En écoute (parlez maintenant)...")
            # Ajustement pour le bruit ambiant (utile pour la clarté)
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                # Utilisation de la reconnaissance par défaut Google (gratuite en illimité pr le dev)
                text = self.recognizer.recognize_google(audio, language="fr-FR")
                print(f"👤 Appelant : {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return "Je n'ai pas bien compris, pouvez-vous répéter ?"
            except sr.RequestError as e:
                print(f"Erreur du service de reconnaissance vocale; {e}")
                return None

    def think_and_respond(self, user_text):
        """ The Thinker : Gènere la réponse avec Gemini """
        if not user_text or user_text == "Je n'ai pas bien compris, pouvez-vous répéter ?":
            return "Je suis désolé, je n'ai pas bien entendu. Pourriez-vous répéter ?"
            
        try:
            response = self.chat_session.send_message(user_text)
            return response.text
        except Exception as e:
            print(f"Erreur Gemini: {e}")
            return "Désolé, je rencontre un problème de réseau. Veuillez patienter."

    def run(self):
        """ Boucle principale de l'agent """
        self.speak("Bonjour, vous êtes bien sur la messagerie intelligente. Comment puis-je vous aider ?")
        
        while True:
            # Étape 1 : Écouter l'appelant
            user_input = self.listen()
            
            if user_input is None:
                continue
                
            # Condition de sortie pour fermer le programme (utile pour le test)
            if "au revoir" in user_input.lower() or "raccrocher" in user_input.lower():
                self.speak("Au revoir et merci de votre appel. À bientôt !")
                break
                
            # Étape 2 : Analyser et penser avec Gemini
            ai_response = self.think_and_respond(user_input)
            
            # Étape 3 : Répondre à voix haute
            self.speak(ai_response)

if __name__ == "__main__":
    # Ce système prompt sera la SEULE chose à changer pour chaque nouveau client.
    # On pourrait charger ça depuis un fichier texte externe par exemple.
    CLIENT_SYSTEM_PROMPT = """
    Tu es l'assistante vocale virtuelle du cabinet dentaire du Dr. Dupont.
    Ton prénom est Sophie.
    Réponds de manière cordiale, concise et professionnelle.
    Les appels que tu gères se font à l'oral, tes phrases doivent donc être fluides, sans puces ni formatting compliqué.
    L'adresse du cabinet est 12 rue de la Paix, 75000 Paris.
    Les horaires: 9h à 18h en semaine.
    Si quelqu'un demande le prix d'un blanchiment, c'est 400€.
    Si quelqu'un veut prendre rendez-vous, demande ses disponibilités puis dis que tu transmets la demande au docteur.
    """
    
    agent = VoiceAgent(system_prompt=CLIENT_SYSTEM_PROMPT)
    agent.run()
