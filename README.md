# CallGenius AI - Assistant Vocal de Secrétariat

Ce projet a pour but de remplacer ou d'assister les services de secrétariat téléphonique traditionnels pour les petites entreprises en utilisant une IA vocale automatisée fonctionnant 24h/24.

## 🏗️ Architecture Simplifiée (Les 3 Piliers)

1. **The Listener (L'Auditeur)** : `SpeechRecognition`
   - Écoute active du flux audio (microphone de l'appelant / ligne VoIP).
   - Conversion Audio vers Texte (Speech-to-Text).
   
2. **The Thinker (Le Penseur)** : `Google Gemini API (Free Tier)`
   - Le "Cerveau" de l'opération.
   - Reçoit le texte transcrit de l'appelant.
   - Construit une réponse intelligente, polie et contextualisée grâce à un *System Prompt* (Personnalité, Horaires, Tarifs).

3. **The Speaker (Le Parleur)** : `pyttsx3`
   - Conversion Texte vers Audio (Text-to-Speech).
   - Articulation vocale fluide avec la prononciation locale pour répondre au client humainement.

## 💰 Modèle Économique & Vente

- **Frais d'installation (Setup Fee)** : 
  Facturé pour la configuration initiale, la rédaction du "System Prompt" parfait (le "cerveau" de l'entreprise) et les tests de voix.
- **Abonnement Mensuel (Retainer)** : 
  Pour la maintenance des serveurs (Google Cloud/Hostinger), la mise à jour des prompts (ex: changement d'horaires, de tarifs) et la scalabilité logicielle.
- **Le Pitch de Vente** : 
  "Un secrétariat traditionnel coûte entre 200€ et 400€+/mois et dort la nuit. CallGenius coûte X€, répond instantanément, connaît l'ensemble de vos tarifs sur le bout des doigts, prend des rendez-vous 24h/24 et ne manque *jamais* un appel client."

## 🚀 Scalabilité

Le code Python source (le `main.py`) **ne change jamais**. 
Lorsqu'un nouveau client (dentiste, garagiste, avocat) est signé, seule la configuration (le fichier de "System Prompt") est modifiée ! Rien n'est hardcodé, tout est modulaire.
