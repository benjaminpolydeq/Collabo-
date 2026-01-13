# 🚀 Guide de Démarrage Rapide - Collabo

Ce guide vous permet de démarrer avec Collabo en moins de 5 minutes !

## ⚡ Installation Express (3 commandes)

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/collabo.git && cd collabo

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run app/main.py
```

✅ **C'est tout !** L'application s'ouvre automatiquement dans votre navigateur.

---

## 📦 Méthodes d'Installation

### Option 1 : Installation Standard (Recommandé)

```bash
# Cloner le repository
git clone https://github.com/votre-username/collabo.git
cd collabo

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer
streamlit run app/main.py
```

### Option 2 : Installation Légère (Sans audio)

```bash
# Même processus mais avec requirements minimal
pip install -r requirements-minimal.txt
streamlit run app/main.py
```

### Option 3 : Avec Make (Linux/Mac)

```bash
# Installation et lancement en une commande
make init
make run
```

### Option 4 : Docker 🐳

```bash
# Avec Docker Compose (Recommandé)
docker-compose up -d

# Ou avec Docker directement
docker build -t collabo-app .
docker run -p 8501:8501 -v $(pwd)/data:/app/data collabo-app
```

Accédez à : `http://localhost:8501`

---

## 🔧 Configuration (Optionnelle)

### Activer l'IA complète

1. Créez un fichier `.env` :
```bash
cp .env.example .env
```

2. Ajoutez votre clé API Anthropic :
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

3. Relancez l'application

> **Note :** L'application fonctionne sans API avec des analyses simulées.

---

## 📖 Premier Pas

### 1. Ajouter votre premier contact

1. Cliquez sur **"👥 Contacts"**
2. Allez dans l'onglet **"➕ Ajouter un Contact"**
3. Remplissez les informations :
   - Nom : `Jean Dupont`
   - Email : `jean@example.com`
   - Domaine : `Technologie`
   - Occasion : `Conférence Tech 2025`
   - Sujets : `AI, Startups, Innovation`
   - Priorité : `Haute`

4. Cliquez sur **"✅ Enregistrer"**

### 2. Démarrer une conversation

1. Retournez à **"👥 Contacts"**
2. Cliquez sur votre contact
3. Cliquez sur **"💬 Chat"**
4. Envoyez votre premier message !

### 3. Voir les statistiques

1. Allez dans **"📊 Analytics"**
2. Consultez vos métriques de networking

---

## 🎯 Fonctionnalités Clés

| Fonctionnalité | Description | Raccourci |
|---------------|-------------|-----------|
| 🏠 Dashboard | Vue d'ensemble de votre réseau | Page d'accueil |
| 👥 Contacts | Gestion complète des contacts | Sidebar → Contacts |
| 💬 Chat | Messagerie sécurisée | Cliquer sur contact |
| 📊 Analytics | Statistiques du réseau | Sidebar → Analytics |
| ⚙️ Paramètres | Configuration | Sidebar → Paramètres |

---

## 🔒 Sécurité

✅ **Chiffrement automatique** - Toutes vos données sont chiffrées
✅ **Stockage local uniquement** - Rien n'est envoyé en ligne
✅ **Aucun serveur externe** - 100% privé

Vos données sont dans : `./data/`

---

## 🆘 Aide Rapide

### L'application ne démarre pas ?

```bash
# Vérifier Python
python --version  # Doit être 3.8+

# Réinstaller les dépendances
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Relancer
streamlit run app/main.py
```

### Erreur de port occupé ?

```bash
# Utiliser un autre port
streamlit run app/main.py --server.port 8502
```

### Données corrompues ?

```bash
# Sauvegarder d'abord
cp -r data/ data_backup/

# Réinitialiser
rm -rf data/
mkdir data
```

---

## 📚 Ressources

- **Documentation complète** : [README.md](README.md)
- **Configuration avancée** : [config.yaml](config.yaml)
- **Variables d'environnement** : [.env.example](.env.example)
- **Support** : [GitHub Issues](https://github.com/votre-username/collabo/issues)

---

## 🎉 C'est parti !

Vous êtes maintenant prêt à utiliser Collabo. Quelques commandes utiles :

```bash
# Voir toutes les commandes Make
make help

# Lancer l'application
make run

# Exécuter les tests
make test

# Créer une sauvegarde
make backup

# Nettoyer les fichiers temporaires
make clean
```

---

## 💡 Astuces Pro

1. **Raccourcis clavier dans Streamlit** :
   - `R` : Recharger l'app
   - `C` : Effacer le cache
   - `?` : Aide

2. **Export de données** :
   - Paramètres → Exporter → Télécharger JSON

3. **Priorités intelligentes** :
   - Haute : Contacts stratégiques
   - Moyenne : Contacts réguliers
   - Basse : Contacts occasionnels

4. **Recherche rapide** :
   - Utilisez la barre de recherche dans Contacts
   - Filtrez par domaine ou priorité

---

<div align="center">
  <p><strong>Besoin d'aide ?</strong></p>
  <p>📧 support@collabo-app.com | 💬 GitHub Discussions</p>
  <br>
  <p>⭐ Si vous aimez Collabo, donnez-nous une étoile sur GitHub !</p>
</div>