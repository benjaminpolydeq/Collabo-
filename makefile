# Makefile pour Collabo Application

.PHONY: help install install-minimal install-dev run test clean format lint docker-build docker-run

# Variables
PYTHON := python3
PIP := pip3
STREAMLIT := streamlit

help: ## Affiche ce message d'aide
	@echo "Collabo - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installation complète avec toutes les dépendances
	$(PIP) install -r requirements.txt
	@echo "✅ Installation complète terminée!"

install-minimal: ## Installation minimale (version légère)
	$(PIP) install -r requirements-minimal.txt
	@echo "✅ Installation minimale terminée!"

install-dev: ## Installation avec dépendances de développement
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"
	@echo "✅ Installation dev terminée!"

run: ## Lance l'application
	$(STREAMLIT) run app/main.py

test: ## Execute les tests
	pytest tests/ -v --cov=app

test-coverage: ## Execute les tests avec rapport de couverture
	pytest tests/ -v --cov=app --cov-report=html
	@echo "📊 Rapport disponible dans htmlcov/index.html"

clean: ## Nettoie les fichiers temporaires
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "🧹 Nettoyage terminé!"

format: ## Formate le code avec Black
	black app/ tests/
	@echo "✨ Code formaté!"

lint: ## Vérifie la qualité du code
	flake8 app/ tests/ --max-line-length=100
	mypy app/ --ignore-missing-imports
	@echo "✅ Lint terminé!"

setup: ## Configuration initiale du projet
	mkdir -p data
	mkdir -p assets/css
	mkdir -p assets/images
	touch data/.gitkeep
	@echo "📁 Structure créée!"

backup: ## Sauvegarde les données
	@echo "💾 Création d'une sauvegarde..."
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz data/
	@echo "✅ Sauvegarde créée!"

venv: ## Crée un environnement virtuel
	$(PYTHON) -m venv venv
	@echo "🐍 Environnement virtuel créé!"
	@echo "Activez-le avec: source venv/bin/activate (Linux/Mac) ou venv\\Scripts\\activate (Windows)"

requirements-update: ## Met à jour requirements.txt
	$(PIP) freeze > requirements.txt
	@echo "📝 Requirements mis à jour!"

security-check: ## Vérifie les vulnérabilités de sécurité
	$(PIP) install safety
	safety check
	@echo "🔒 Vérification de sécurité terminée!"

docs: ## Génère la documentation
	mkdocs build
	@echo "📚 Documentation générée dans site/"

docs-serve: ## Lance le serveur de documentation
	mkdocs serve

docker-build: ## Construit l'image Docker
	docker build -t network-app:latest .
	@echo "🐳 Image Docker construite!"

docker-run: ## Lance l'application dans Docker
	docker run -p 8501:8501 -v $(PWD)/data:/app/data network-app:latest

init: venv install setup ## Installation complète pour nouveau projet
	@echo "🎉 Projet initialisé avec succès!"
	@echo "Lancez 'make run' pour démarrer l'application"

update: ## Met à jour toutes les dépendances
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	@echo "⬆️ Dépendances mises à jour!"

info: ## Affiche les informations du système
	@echo "🔍 Informations système:"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Streamlit: $(shell $(STREAMLIT) --version)"
	@echo "Répertoire: $(PWD)"