# CI/CD Pipeline Dokumentation
## DEZSYS • Jenkins • Docker • Python Flask

---

| | |
|---|---|
| **Projekt** | DEZSYS_JENKINS_HELLOSPENCER |
| **Schüler** | Jonathan Joestar |
| **Klasse / Fach** | Middleware Engineering |
| **Schule** | HTL Rennweg |
| **Repository** | [github.com/skengzyy/DEZSYS_JENKINS_HELLOSPENCER](https://github.com/skengzyy/DEZSYS_JENKINS_HELLOSPENCER) |
| **Jenkins Build #7** | [customize-denim-whacking.ngrok-free.dev/job/HelloSpencer/7/console](https://customize-denim-whacking.ngrok-free.dev/job/HelloSpencer/7/console) |
| **ngrok Inspector** | [127.0.0.1:4040/inspect/http](http://127.0.0.1:4040/inspect/http) |

---

## 1. Einführung

Diese Dokumentation beschreibt die Implementierung einer vollständigen CI/CD Pipeline für eine Python Flask Applikation im Rahmen des Unterrichtsfaches Middleware Engineering an der HTL Rennweg.

Als CI/CD-Plattform wurde Jenkins eingesetzt, da es sich dabei um eine der meistverbreiteten Open-Source-Lösungen im DevOps-Bereich handelt. Die Pipeline automatisiert den gesamten Softwareentwicklungszyklus von der Quellcodeverwaltung über den Build-Prozess bis hin zum automatisierten Testen und Deployment.

Jenkins ist über ngrok öffentlich erreichbar, was das automatische Triggern der Pipeline bei GitHub Pushes ermöglicht.

---

## 2. Ziele

- Verstehen der Funktionsweise und Einsatzmöglichkeiten von CI/CD Pipelines als DevOps-Werkzeug
- Installation und Konfiguration von Jenkins als CI/CD-Plattform
- Erstellen einer vollständigen Pipeline mit den Stages Source, Build, Test und Deploy
- Integration von Docker als Containerisierungstool in den Build-Prozess
- Automatisches Triggern der Pipeline bei GitHub-Commits via Webhook
- Schreiben und Ausführen von Unit-Tests für eine Flask REST API

---

## 3. Voraussetzungen & Umgebung

### 3.1 Verwendete Technologien

| Komponente | Version / Details |
|---|---|
| Betriebssystem | macOS (Apple Silicon / ARM64) |
| Jenkins | jenkins/jenkins:latest (Docker Container) |
| Docker | Docker Desktop für Mac |
| Python | 3.11 (python:3.11-slim-buster) |
| Framework | Flask 2.3.3 |
| Test Framework | pytest 7.4.2 |
| Tunneling | ngrok (öffentlicher Zugang für Webhook) |
| Versionsverwaltung | Git / GitHub |

### 3.2 Repository Struktur

```
DEZSYS_JENKINS_HELLOSPENCER/
├── src/
│   ├── __init__.py
│   └── hello.py          # Flask Applikation
├── tests/
│   ├── __init__.py
│   ├── test_api.py       # API Integration Tests
│   └── test_hello.py     # Unit Tests
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
└── count.txt
```

---

## 4. Jenkins Installation & Konfiguration

### 4.1 Jenkins Container starten

Jenkins wurde als Docker Container mit gemountem Docker Socket gestartet, damit Jenkins selbst Docker-Befehle ausführen kann:

```bash
docker run -u root -d \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins \
  jenkins/jenkins:latest
```

Das Mounting des Docker Sockets (`/var/run/docker.sock`) ist entscheidend: Damit kann Jenkins innerhalb des Containers Docker-Befehle an den Host-Docker-Daemon delegieren, ohne Docker selbst zu installieren.

### 4.2 Docker CLI im Jenkins Container

Da der Jenkins Container standardmäßig keine Docker CLI enthält, wurde diese manuell nachinstalliert:

```bash
docker exec -it jenkins bash
apt-get update && apt-get install -y docker-ce-cli
```

### 4.3 Installierte Plugins

- Docker Plugin
- CloudBees Docker Build and Publish
- GitHub Integration Plugin (für Webhook-Trigger)

### 4.4 ngrok Tunnel

Da Jenkins lokal auf Port 8080 läuft, wurde ngrok verwendet um einen öffentlich erreichbaren HTTPS-Tunnel zu erstellen. Dieser ist notwendig damit GitHub den Webhook-Aufruf an Jenkins senden kann.

```bash
ngrok http 8080
```

Der ngrok Inspector unter [http://127.0.0.1:4040/inspect/http](http://127.0.0.1:4040/inspect/http) ermöglicht die Echtzeit-Überwachung aller eingehenden HTTP-Anfragen, inklusive der GitHub Webhook Calls.

---

## 5. CI/CD Pipeline

### 5.1 Pipeline Übersicht

| Stage | Status | Beschreibung | Dauer |
|---|---|---|---|
| Source | PASSED | GitHub Repo checkout via SCM | ~2s |
| Build | PASSED | Docker Image hellospencer:latest gebaut | ~18s |
| Test | PASSED | 5/5 Unit Tests erfolgreich | ~0.07s |
| Deploy | PASSED | Container auf Port 5001 deployed | ~3s |

### 5.2 Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Source') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }
        stage('Build') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t hellospencer:latest .'
            }
        }
        stage('Test') {
            steps {
                echo 'Running unit tests...'
                sh 'docker run --rm hellospencer:latest python -m pytest tests/ -v'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
                sh '''
                  docker stop hellospencer-app 2>/dev/null || true
                  docker rm hellospencer-app 2>/dev/null || true
                  docker run -d --name hellospencer-app -p 5001:5000 hellospencer:latest
                '''
            }
        }
    }
    post {
        success { echo 'Pipeline erfolgreich!' }
        failure { echo 'Pipeline fehlgeschlagen!' }
    }
}
```

### 5.3 Dockerfile

```dockerfile
FROM python:3.11-slim-buster
ADD . /python-flask
WORKDIR /python-flask
RUN pip install -r requirements.txt
CMD ["python", "src/hello.py"]
```

### 5.4 GitHub Webhook

Damit die Pipeline automatisch bei jedem Push auf GitHub gestartet wird, wurde ein Webhook konfiguriert:

| Feld | Wert |
|---|---|
| Payload URL | https://customize-denim-whacking.ngrok-free.dev/github-webhook/ |
| Content Type | application/json |
| Trigger Event | Just the push event |
| Status | Active |

Bei jedem `git push origin main` sendet GitHub automatisch eine POST-Anfrage an die Payload URL, Jenkins verarbeitet den Webhook und startet die Pipeline sofort.

---

## 6. Unit Tests

### 6.1 Testergebnisse

Alle 5 Unit Tests wurden erfolgreich ausgeführt (pytest 7.4.2, Python 3.11.4):

| Test Name | Klasse | Beschreibung | Ergebnis |
|---|---|---|---|
| `test_api_response_time` | TestAPIEndpoints | API antwortet < 2 Sekunden | PASSED |
| `test_hello_endpoint_success` | TestAPIEndpoints | GET /api/hello liefert Status 200 | PASSED |
| `test_hello_endpoint_content_type` | TestHelloSpencer | Response Content-Type ist application/json | PASSED |
| `test_hello_endpoint_data` | TestHelloSpencer | Response Body enthält korrekte Daten | PASSED |
| `test_hello_endpoint_status_code` | TestHelloSpencer | HTTP Status Code ist 200 | PASSED |

```
============================== 5 passed in 0.07s ==============================
```

### 6.2 Teststruktur

#### tests/test_hello.py

Unit-Tests die direkt den Flask Test Client verwenden, ohne dass ein laufender Server benötigt wird. Testet Status Code, Content-Type und Response-Daten.

#### tests/test_api.py

Integration-Tests die ebenfalls den Flask Test Client verwenden. Nach einem Import-Fix (`src.hello` statt `localhost:5556`) laufen diese nun korrekt im Docker Container.

```python
# Korrekter Import nach Fix:
from src.hello import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
```

---

## 7. Pipeline Build #7 – Erfolgreicher Durchlauf

| | |
|---|---|
| **Build Nr.** | #7 |
| **Trigger** | GitHub push by skengzyy |
| **Commit** | fix: correct import to src.hello (`a9b77d7`) |
| **Jenkins Log** | [/job/HelloSpencer/7/console](https://customize-denim-whacking.ngrok-free.dev/job/HelloSpencer/7/console) |
| **Gesamtstatus** | SUCCESS |
| **Deployment** | hellospencer-app auf Port 5001 laufend |

### 7.1 Stage-Verlauf

- **Source:** Repository ausgecheckt (Revision `a9b77d7bfd943689a572474f6a8797a39194ea01`)
- **Build:** Docker Image `hellospencer:latest` erfolgreich gebaut (18.8s, alle Dependencies installiert)
- **Test:** 5/5 pytest Tests bestanden in 0.07s
- **Deploy:** Container `hellospencer-app` gestartet auf Port `5001:5000`

### 7.2 Vorherige Fehler & Lösungen

| Build | Fehler | Lösung |
|---|---|---|
| #5 | `test_api.py` versuchte HTTP-Verbindung zu `localhost:5556` – Server nicht gestartet | Umstellung auf Flask Test Client (`app.test_client()`) |
| #6 | `ModuleNotFoundError: No module named 'app'` | Import geändert auf `from src.hello import app` |
| #6 | Port 5000 bereits belegt (macOS AirPlay Receiver) | Port auf 5001 geändert in Jenkinsfile |

---

## 8. Erfüllte Anforderungen

### 8.1 Grundanforderungen 

- [x] Jenkins Installation via Docker Container
- [x] Konfiguration einer einfachen Pipeline (HelloWorld Ausgabe)
- [x] Einbindung des GitHub Repositories via SCM

### 8.2 Erweiterte Anforderungen – Vollständig erfüllt 

- [x] Erstellung von Unit-Tests (5 Tests in `test_api.py` und `test_hello.py`)
- [x] Installation und Konfiguration von Docker, Einbindung in Jenkins
- [x] Konfiguration einer Jenkins Pipeline für die Flask Applikation
- [x] Pipeline wird automatisch bei GitHub Push gestartet (Webhook via ngrok)
- [x] Deployment erfolgt lokal auf dem Notebook (Docker Container Port 5001)

---

## 9. Links & Referenzen

| Ressource | URL |
|---|---|
| GitHub Repository | [github.com/skengzyy/DEZSYS_JENKINS_HELLOSPENCER](https://github.com/skengzyy/DEZSYS_JENKINS_HELLOSPENCER) |
| Jenkins Build #7 Log | [customize-denim-whacking.ngrok-free.dev/job/HelloSpencer/7/console](https://customize-denim-whacking.ngrok-free.dev/job/HelloSpencer/7/console) |
| ngrok HTTP Inspector | [127.0.0.1:4040/inspect/http](http://127.0.0.1:4040/inspect/http) |
| Jenkins Dokumentation | [jenkins.io/doc/book/pipeline](https://www.jenkins.io/doc/book/pipeline/) |
| Docker Hub – Jenkins | [hub.docker.com/r/jenkins/jenkins](https://hub.docker.com/r/jenkins/jenkins) |
