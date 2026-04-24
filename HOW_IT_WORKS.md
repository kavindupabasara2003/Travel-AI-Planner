# How We Built It — Step by Step
## AI Travel Planner for Sri Lanka
### A Beginner-Friendly Explanation

---

> This document explains every technical piece of this project in plain English.
> No experience needed. Each section builds on the previous one.

---

# PART 1 — TRAINING THE AI MODEL

---

## What Are We Trying to Do?

We took a general AI model that knows about everything in the world, and we
**taught it specifically about Sri Lanka** — its restaurants, beaches, temples,
cities, and attractions. This process is called **fine-tuning**.

Think of it like this: a fresh university graduate knows general knowledge.
Fine-tuning is like sending them to a Sri Lanka tourism bootcamp so they
become an expert specifically on that topic.

---

## Step 1 — Collect Raw Data

**File:** `data/SriLanka_Travel_Dataset_Final.csv`

We started with a spreadsheet of **971 Sri Lankan locations** — restaurants,
hotels, beaches, temples, and tourist spots. Each row looked like this:

```
Location_Name       | Located_City | Location_Type | AI_Context
--------------------|--------------|---------------|------------------------------------------
Bavarian Barn Resto | Colombo      | Restaurant    | Bavarian Barn is a Restaurant in Colombo...
Sigiriya Rock       | Sigiriya     | Attraction    | Sigiriya is an ancient rock fortress...
```

This is just a plain spreadsheet. The AI cannot learn from a spreadsheet directly
— we need to convert it into a format the AI understands.

---

## Step 2 — Convert Data into AI Training Format (JSONL)

**Script:** `scripts/prepare_training_data.py`

The AI we're fine-tuning (LLaMA 3.2) is a **chat model**. It was designed to
have conversations. So our training data must look like a real conversation —
a question followed by an answer.

The script reads each row from the CSV and creates conversation pairs like this:

```json
{
  "messages": [
    { "role": "system",    "content": "You are a helpful Sri Lanka Travel Assistant." },
    { "role": "user",      "content": "Recommend a Restaurant in Colombo." },
    { "role": "assistant", "content": "You should check out Bavarian Barn Restaurant. It is located in Colombo..." }
  ]
}
```

For every location it creates **two training examples**:
1. A recommendation question ("Any good restaurants in Colombo?")
2. A location question ("Where is Bavarian Barn located?")

With 971 rows × 2 examples = approximately **1,900 training conversations**.

All examples are saved into a file called `data/srilanka_travel_chat.jsonl`
(JSONL = one JSON object per line).

Then the data is split into three files:
- `data/train.jsonl` — **80%** of the data (used to train the model)
- `data/valid.jsonl` — **10%** of the data (used to check if training is working)
- `data/test.jsonl`  — **10%** of the data (used for final evaluation after training)

**Why three splits?**
Think of it like studying for an exam. You use most material to study (train),
some to practice mock exams (valid), and the actual exam tests you on unseen
questions (test).

---

## Step 3 — Fine-Tune the Model with QLoRA

**Script:** `scripts/train_model.py`

### What model did we start from?

We used `mlx-community/Llama-3.2-3B-Instruct-4bit` as our base.

- **LLaMA 3.2** — Meta's open-source AI model
- **3B** — 3 billion internal parameters (its "brain size")
- **Instruct** — a version already trained to follow instructions
- **4bit** — compressed to use less memory (instead of 32 numbers per
  parameter, it uses 4-bit numbers)

### What is LoRA? (The technique we used)

Normally, fine-tuning means updating ALL 3 billion parameters — that requires
a massive computer. **LoRA (Low-Rank Adaptation)** is a clever shortcut.

Instead of changing the original model, LoRA adds small "side notes" to it:

```
Original Model Weights (frozen, never changed)
         +
Small Adapter Matrices A and B (these are trained)
         =
Fine-tuned behaviour
```

The adapter matrices are tiny — instead of 3 billion numbers, we only train
about 3 million (1% of the model). This means we can fine-tune on a laptop.

### The training settings we used

```python
MODEL_NAME   = "mlx-community/Llama-3.2-3B-Instruct-4bit"
TRAIN_ITERS  = 600         # How many learning steps
BATCH_SIZE   = 1           # Process 1 conversation at a time
LORA_LAYERS  = 16          # Apply LoRA to 16 layers in the model
LEARNING_RATE = 1e-5       # How fast the model adjusts (very small = careful)
LORA_RANK    = 8           # Size of the adapter matrices
```

### What happens during training?

1. The script shows the model a training conversation (question + answer)
2. The model tries to predict the answer
3. We measure how wrong it was (this is called the **loss**)
4. We nudge the adapter weights slightly to be less wrong next time
5. Repeat 600 times

Every 100 steps, the script saves a checkpoint:
- `adapters/0000100_adapters.safetensors`
- `adapters/0000200_adapters.safetensors`
- ... up to ...
- `adapters/0000600_adapters.safetensors`
- `adapters/adapters.safetensors` (the final best version)

These `.safetensors` files ARE the fine-tuning. They are the "Sri Lanka knowledge"
we added to LLaMA.

---

## Step 4 — Convert to GGUF Format for Ollama

After training, the adapter weights need to be merged with the base model
and converted to **GGUF format** — a compressed format that can run efficiently
on a laptop without a GPU.

This produced the model files in the `models/` folder:
- `models/srilanka-llama-q4.gguf` — 1.9 GB (the one we actually use)
- `models/srilanka-llama.gguf`    — 6.4 GB (full precision backup)

**GGUF** is like a ZIP file for AI models — same intelligence, less storage.
**Q4** means 4-bit quantized — each number in the model is stored in 4 bits
instead of 32 bits, making it ~8× smaller with minimal quality loss.

---

## Step 5 — Create the Modelfile for Ollama

**File:** `Modelfile`

Ollama is the program that actually runs our AI model (like a movie player
plays video files). The `Modelfile` tells Ollama how to set up the model:

```
FROM ./models/srilanka-llama-q4.gguf
SYSTEM "You are a friendly and knowledgeable Sri Lanka Travel Assistant.
        You help users plan cultural, beach, and adventure trips.
        When asked to plan a trip, output JSON.
        When asked general questions, answer naturally."
PARAMETER temperature 0.7
```

**Line by line:**
- `FROM` — which model file to load
- `SYSTEM` — a permanent instruction given to the model before every
  conversation (this is what makes it behave as a travel assistant)
- `temperature 0.7` — controls creativity. 0 = robotic and repetitive,
  1 = very creative but sometimes wrong. 0.7 is a good balance.

**To register this model with Ollama:**
```bash
ollama create srilanka-llama -f Modelfile
```

After this, the model is available as `srilanka-llama` in Ollama, alongside
`llama3.2` (the base model) and `nomic-embed-text` (for embeddings).

---

## Step 6 — How the Model Gets Used in the App

When a user requests an itinerary, the Django backend calls Ollama's HTTP API:

```
User Request
     ↓
Django Backend (llama_service.py)
     ↓
POST http://host.docker.internal:11434/api/chat
     ↓
Ollama (running on your laptop)
     ↓
srilanka-llama model generates the itinerary
     ↓
JSON response sent back to the user
```

`host.docker.internal` is a special address that lets containers reach
services running on the host machine (your laptop).

---

# PART 2 — DOCKER

---

## What is Docker?

**Without Docker:** "It works on my laptop but not on the server" is a very
common problem. Different computers have different operating systems, different
software versions, different file paths.

**With Docker:** You package your app and everything it needs (Python version,
libraries, settings) into a sealed box called a **container**. That box runs
identically everywhere — your laptop, a server, the cloud.

---

## Key Concepts

### Image
A **Docker Image** is a recipe — a snapshot of an application and all its
dependencies. Think of it like a cake recipe. You can bake the same cake
(container) from the same recipe (image) any number of times.

### Container
A **Container** is a running image. It's the actual cake. You can run
multiple containers from the same image at the same time.

### Dockerfile
A **Dockerfile** is the set of instructions for building an image.
Step by step: start from this base, install these packages, copy these files,
run this command.

---

## Our Backend Dockerfile — `backend/Dockerfile`

```dockerfile
# Step 1: Start from a minimal Python 3.13 environment
FROM python:3.13-slim

# Step 2: Tell Python not to create .pyc files and to show logs immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=travel_ai_backend.settings

# Step 3: Set the working folder inside the container
WORKDIR /app

# Step 4: Install system tools needed by psycopg2 (PostgreSQL driver)
#         gcc = C compiler, libpq-dev = PostgreSQL header files
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Copy the requirements list and install all Python packages
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn

# Step 6: Copy all the Django code into the container
COPY . /app/

# Step 7: Tell Docker that this container uses port 8000
EXPOSE 8000

# Step 8: When the container starts, run the Django app via Gunicorn
#         --timeout 300 = allow 300 seconds for long AI generation requests
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "300",
     "travel_ai_backend.wsgi:application"]
```

**Why Gunicorn?** Django alone can only handle one request at a time.
Gunicorn is a production server that manages multiple workers so many users
can be served simultaneously.

---

## Our Frontend Dockerfile — `frontend/Dockerfile`

This uses a **multi-stage build** — two separate build steps in one file.
This is important because Node.js (used to build the Vue app) is a large
tool, but we don't need it in production. We only need the final HTML/JS/CSS files.

```dockerfile
# ===== STAGE 1: Build the Vue app =====
FROM node:20-alpine AS build-stage

WORKDIR /app

# Install dependencies first (cached if package.json hasn't changed)
COPY package*.json ./
RUN npm ci

# Copy the Vue source code and build it
COPY . .
RUN npm run build
# After this, /app/dist/ contains the final HTML, CSS, JS files

# ===== STAGE 2: Serve with Caddy =====
FROM caddy:alpine as production-stage

# Copy ONLY the built files from Stage 1 (not the whole Node.js environment)
COPY --from=build-stage /app/dist /srv

# Copy our Caddy configuration
COPY Caddyfile /etc/caddy/Caddyfile

EXPOSE 80
EXPOSE 443

# Start the Caddy web server
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
```

**Result:** The final image is only ~85 MB (just Caddy + static files) instead
of 800+ MB (if we included Node.js).

---

## What is Caddy and Why Do We Use It?

Caddy is a modern web server. In our project it does two jobs:

**Job 1: Serve the Vue app (static file server)**
When you visit `http://localhost:5173/`, Caddy serves the HTML/CSS/JS files
that make up the Vue frontend.

**Job 2: Reverse Proxy for the API**
When the Vue app makes an API call to `/api/v1/plan/`, that request needs to
reach the Django backend. Caddy intercepts it and forwards it to Django.

```
Browser Request: GET /api/v1/trips/
         ↓
    Caddy (port 80)
         ↓  [sees /api/* prefix]
    Forwards to: http://travel-ai-backend:8000
         ↓
    Django handles it and sends response back
         ↓
    Caddy returns response to browser
```

**Without a reverse proxy**, the browser would need to know two separate
addresses (port 80 for frontend, port 8000 for backend) and would face
CORS (Cross-Origin) security errors.

**With Caddy**, everything goes through one address — the browser only ever
talks to Caddy.

---

## The Caddyfile — `frontend/Caddyfile`

```caddy
:80 {
    # Rule 1: Any request starting with /api/ goes to Django
    handle /api/* {
        reverse_proxy travel-ai-backend:8000
    }

    # Rule 2: Everything else serves the Vue app
    handle {
        root * /srv
        try_files {path} {path}/ /index.html
        file_server
    }
}
```

**The `try_files` line is critical for Vue Router.**
Vue is a Single Page Application — there's only one real HTML file (`index.html`).
All page changes (going from `/planner` to `/profile`) happen in JavaScript,
not by loading new pages from the server.

If a user visits `http://localhost/profile` directly (or refreshes the page),
Caddy would normally look for a file called `profile` in `/srv` — which
doesn't exist — and return a 404 error.

`try_files {path} {path}/ /index.html` tells Caddy: "If you can't find
the file, just return `index.html` anyway." Vue Router then reads the URL
and shows the correct page.

---

## Docker Compose — Running All Containers Together

**File:** `docker-compose.yml`

Running three separate containers manually would be tedious. Docker Compose
lets you define all containers in one file and start them all with one command.

```yaml
version: '3.8'

services:

  # Container 1: PostgreSQL database with pgvector
  db:
    image: pgvector/pgvector:pg16     # Use this ready-made image from Docker Hub
    container_name: travel-ai-postgres-prod
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: travel_ai
    ports:
      - "5433:5432"    # host:container — access from laptop on port 5433
    volumes:
      - postgres_data:/var/lib/postgresql/data   # Persist data even if container restarts

  # Container 2: Django backend
  api:
    build: ./backend              # Build image from backend/Dockerfile
    container_name: travel-ai-backend
    command: gunicorn --bind 0.0.0.0:8000 --timeout 300 travel_ai_backend.wsgi:application
    volumes:
      - ./backend:/app            # Mount local code — changes reflect immediately
    ports:
      - "8000:8000"
    depends_on:
      - db                        # Don't start until database is ready
    environment:
      - DB_HOST=db                # "db" = the service name above (Docker DNS)
      - DB_PORT=5432
      - OLLAMA_HOST=http://host.docker.internal:11434

  # Container 3: Vue frontend (Caddy)
  frontend:
    build: ./frontend             # Build image from frontend/Dockerfile
    container_name: travel-ai-frontend
    ports:
      - "5173:80"
    depends_on:
      - api

volumes:
  postgres_data:                  # Named volume — survives container restarts
```

**Container networking:** All three containers share a private Docker network
called `travelai_default`. Inside this network they can find each other by
service name. So when Caddy's config says `reverse_proxy travel-ai-backend:8000`,
Docker DNS resolves `travel-ai-backend` to the correct container IP automatically.

**To start everything:**
```bash
docker compose up -d           # Start all containers in background
docker compose up -d --build   # Rebuild images first, then start
docker compose up -d --force-recreate   # Recreate containers from latest images
docker compose down            # Stop and remove all containers
docker compose logs api        # See backend logs
```

---

# PART 3 — KUBERNETES (K8s)

---

## What is Kubernetes and Why?

Docker Compose runs everything on **one machine**. If that machine crashes,
everything is down. Kubernetes (K8s) manages containers across **multiple
machines** and adds:

- **Self-healing** — if a container crashes, K8s restarts it automatically
- **Scaling** — run 2, 5, or 10 copies of the backend if traffic is high
- **Rolling updates** — deploy new versions with zero downtime
- **Health checks** — stop sending traffic to a pod that isn't ready yet

In our project, we use K8s via **Docker Desktop** which runs a local
single-node cluster on your laptop for development and demonstration.

---

## Key Kubernetes Vocabulary

| Word | What it means |
|------|---------------|
| **Pod** | The smallest unit. Usually one running container. |
| **Deployment** | Manages a set of identical Pods. Ensures the right number are always running. |
| **Service** | A stable network address for a set of Pods (Pods have changing IPs, Services don't). |
| **ConfigMap** | Stores non-secret configuration (environment variables). |
| **Secret** | Stores sensitive data like passwords (base64 encoded). |
| **PersistentVolumeClaim** | Requests storage that survives Pod restarts (for the database). |
| **Ingress** | An HTTP router — routes incoming web traffic to the right Service. |
| **Namespace** | A virtual cluster inside the cluster. We use `travel-ai` namespace. |

---

## What is Helm?

Writing raw Kubernetes YAML files for every environment (dev/staging/prod)
means duplicating lots of code. **Helm** is Kubernetes' package manager —
like npm for Node.js or pip for Python.

A **Helm Chart** is a folder of template YAML files where values are replaced
with variables. You define the variables in `values.yaml` and Helm fills them in.

**Our chart is at:** `k8s/travel-ai-chart/`

```
k8s/travel-ai-chart/
├── Chart.yaml         ← Chart metadata (name, version)
├── values.yaml        ← Default variable values
└── templates/
    ├── backend.yaml   ← Django Deployment + Service
    ├── frontend.yaml  ← Caddy Deployment + Service
    ├── postgres.yaml  ← PostgreSQL PVC + Deployment + Service
    ├── secrets.yaml   ← Database passwords + Django secret key
    ├── configmap.yaml ← Non-secret environment variables
    └── ingress.yaml   ← HTTP routing rules
```

---

## values.yaml — The Control Panel

```yaml
# How many copies of each service to run
replicaCount:
  frontend: 2     # 2 frontend pods = if one crashes, the other keeps serving
  backend: 2      # 2 backend pods = handles more concurrent AI requests
  postgres: 1     # 1 database pod (only ever one to avoid data conflicts)

# Which Docker images to use
image:
  frontend:
    repository: travel-ai-frontend
    tag: "latest"
    pullPolicy: IfNotPresent    # Use local image, don't try to download
  backend:
    repository: travel-ai-backend
    tag: "latest"
    pullPolicy: IfNotPresent
  postgres:
    repository: pgvector/pgvector
    tag: "pg16"

# Database credentials (stored as base64 in Secrets)
postgresql:
  database: "travel_ai_db"
  username: "traveldb_user"
  base64user:     "dHJhdmVsZGJfdXNlcg=="       # base64("traveldb_user")
  base64password: "c2VjdXJlcGFzc3dvcmQxMjM="   # base64("securepassword123")
  base64db:       "dHJhdmVsX2FpX2Ri"            # base64("travel_ai_db")

# Django settings
django:
  base64secretkey: "ZGphbmdvLWluc2VjdXJlLXN1cGVyc2VjcmV0a2V5"
  debug: "True"
  allowed_hosts: "*"
  ollama_host: "http://host.docker.internal:11434"   # Reach Ollama on host machine

# The domain name for the Ingress
ingress:
  host: "travelai.local"
```

---

## Template 1 — secrets.yaml

Kubernetes Secrets store sensitive values. They are base64 encoded (not
encrypted — just obscured). For real production, you'd use a secrets manager
like HashiCorp Vault.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Release.Name }}-secrets    # e.g., "travel-ai-secrets"
type: Opaque
data:
  POSTGRES_USER:     {{ .Values.postgresql.base64user | quote }}
  POSTGRES_PASSWORD: {{ .Values.postgresql.base64password | quote }}
  POSTGRES_DB:       {{ .Values.postgresql.base64db | quote }}
  SECRET_KEY:        {{ .Values.django.base64secretkey | quote }}
```

`{{ .Release.Name }}` is a Helm template variable — it gets replaced with
the release name (`travel-ai`) when you run `helm install`.

---

## Template 2 — configmap.yaml

ConfigMaps store non-sensitive configuration as plain text key-value pairs.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  POSTGRES_HOST: "{{ .Release.Name }}-postgres-service"   # Internal DNS name
  POSTGRES_PORT: "5432"
  DEBUG:         {{ .Values.django.debug | quote }}
  ALLOWED_HOSTS: {{ .Values.django.allowed_hosts | quote }}
  OLLAMA_HOST:   {{ .Values.django.ollama_host | quote }}
```

Notice `POSTGRES_HOST` is set to `travel-ai-postgres-service` — that's the
Kubernetes Service name for the database. K8s DNS automatically resolves this
to the database Pod's IP, just like Docker Compose's internal network.

---

## Template 3 — postgres.yaml

This has three parts: storage request, the database container, and its network address.

```yaml
# PART A: Ask Kubernetes for 5GB of persistent storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ .Release.Name }}-postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce         # Only one pod can write at a time (correct for DB)
  resources:
    requests:
      storage: 5Gi
---
# PART B: The PostgreSQL container
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-postgres-deployment
spec:
  replicas: {{ .Values.replicaCount.postgres }}   # Always 1
  selector:
    matchLabels:
      app: {{ .Release.Name }}-postgres
  template:
    spec:
      containers:
        - name: postgres
          image: "pgvector/pgvector:pg16"         # PostgreSQL with vector support
          env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:                     # Pull from the Secret (not hardcoded)
                  name: {{ .Release.Name }}-secrets
                  key: POSTGRES_USER
            # ... POSTGRES_PASSWORD and POSTGRES_DB same pattern
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data  # Where PostgreSQL stores files
      volumes:
        - name: postgres-data
          persistentVolumeClaim:
            claimName: {{ .Release.Name }}-postgres-pvc   # Use the PVC from PART A
---
# PART C: A stable network address for the database
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-postgres-service
spec:
  selector:
    app: {{ .Release.Name }}-postgres    # Route traffic to pods with this label
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
```

**Why PersistentVolumeClaim?** Without it, if the PostgreSQL pod crashes and
restarts, all data would be lost. The PVC ensures the data is stored on the
host machine's disk and re-attached to the new pod.

---

## Template 4 — backend.yaml (Django)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-backend-deployment
spec:
  replicas: {{ .Values.replicaCount.backend }}   # 2 pods = redundancy
  selector:
    matchLabels:
      app: {{ .Release.Name }}-backend
  template:
    spec:
      containers:
        - name: backend
          image: "travel-ai-backend:latest"
          imagePullPolicy: IfNotPresent           # Use locally built image
          ports:
            - containerPort: 8000
          env:
            - name: DJANGO_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ .Release.Name }}-secrets
                  key: SECRET_KEY
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: {{ .Release.Name }}-config
                  key: POSTGRES_HOST
            - name: OLLAMA_HOST
              valueFrom:
                configMapKeyRef:
                  name: {{ .Release.Name }}-config
                  key: OLLAMA_HOST
            # ... other env vars from ConfigMap/Secret
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-backend-service
spec:
  type: ClusterIP          # Internal only — not reachable from outside the cluster
  selector:
    app: {{ .Release.Name }}-backend
  ports:
    - port: 8000
      targetPort: 8000
```

`ClusterIP` means this Service is only accessible from inside the cluster.
The frontend Caddy pod can reach it, but your browser cannot directly.

---

## Template 5 — frontend.yaml (Caddy)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-frontend-deployment
spec:
  replicas: {{ .Values.replicaCount.frontend }}   # 2 pods
  template:
    spec:
      containers:
        - name: frontend
          image: "travel-ai-frontend:latest"
          ports:
            - containerPort: 80
            - containerPort: 443
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-frontend-service
spec:
  type: LoadBalancer       # Externally reachable — this is the entry point
  selector:
    app: {{ .Release.Name }}-frontend
  ports:
    - name: http
      port: 80
      targetPort: 80
    - name: https
      port: 443
      targetPort: 443
```

`LoadBalancer` means Docker Desktop assigns `localhost` as the external IP,
so `http://localhost` reaches this Service from your browser.

The Caddyfile inside the frontend container still routes `/api/*` to
`travel-ai-backend:8000` — K8s DNS resolves `travel-ai-backend` to the
backend Service, which then load-balances across the 2 backend pods.

---

## Template 6 — ingress.yaml

The Ingress is an HTTP router that sits in front of everything.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ .Release.Name }}-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$1
spec:
  rules:
    - host: travelai.local               # Only respond to this domain name
      http:
        paths:
          - path: /?(.*)
            pathType: Prefix
            backend:
              service:
                name: {{ .Release.Name }}-frontend-service
                port:
                  number: 80
```

This routes all traffic for `travelai.local` to the frontend Service.
To use this from a browser you'd add `127.0.0.1 travelai.local` to your
`/etc/hosts` file. Currently the app is accessible at `http://localhost`
directly via the LoadBalancer Service (no Ingress needed for local dev).

---

## How to Deploy to Kubernetes

```bash
# Step 1: Build Docker images
docker compose build

# Step 2: Tag them with the names the Helm chart expects
docker tag travelai-api:latest      travel-ai-backend:latest
docker tag travelai-frontend:latest travel-ai-frontend:latest

# Step 3: Deploy with Helm (installs or upgrades)
helm upgrade --install travel-ai k8s/travel-ai-chart/ \
  --namespace travel-ai \
  --create-namespace

# Step 4: Run Django migrations inside the pod
kubectl exec -n travel-ai \
  $(kubectl get pod -n travel-ai -l app=travel-ai-backend -o jsonpath='{.items[0].metadata.name}') \
  -- python manage.py migrate

# Step 5: Check everything is running
kubectl get all -n travel-ai
```

**To update after code changes:**
```bash
docker compose build                          # Rebuild images
docker tag travelai-api:latest travel-ai-backend:latest
docker tag travelai-frontend:latest travel-ai-frontend:latest
kubectl rollout restart deployment/travel-ai-backend-deployment -n travel-ai
kubectl rollout restart deployment/travel-ai-frontend-deployment -n travel-ai
kubectl rollout status  deployment/travel-ai-backend-deployment -n travel-ai
```

---

## Full Architecture — How Everything Connects

```
YOUR BROWSER
     |
     | http://localhost (K8s) or http://localhost:5173 (Docker Compose)
     ↓
CADDY (frontend container)
     |
     |── /api/* requests ──→ DJANGO (backend container, port 8000)
     |                              |
     |                              |── reads/writes ──→ POSTGRESQL (db container)
     |                              |
     |                              |── AI requests ──→ OLLAMA (on your laptop, port 11434)
     |                                                        |
     |                                                        └── srilanka-llama model
     |                                                        └── nomic-embed-text model
     |                                                        └── llama3.2 model
     |
     └── /* requests ─────→ Vue App files in /srv (index.html, app.js, style.css)
```

---

## Summary of All Commands

```bash
# ===== DOCKER COMPOSE =====
docker compose build                    # Build images
docker compose up -d                    # Start all containers
docker compose up -d --force-recreate  # Recreate with new images (after code change)
docker compose down                     # Stop and remove containers
docker compose logs -f api              # Watch backend logs live
docker compose ps                       # Show container status

# ===== KUBERNETES =====
kubectl get pods -n travel-ai           # List all pods
kubectl get all -n travel-ai            # List everything
kubectl logs -n travel-ai <pod-name>    # See pod logs
kubectl describe pod -n travel-ai <pod> # Detailed pod info
kubectl rollout restart deployment/travel-ai-backend-deployment -n travel-ai

# ===== HELM =====
helm list -n travel-ai                  # List installed releases
helm upgrade --install travel-ai k8s/travel-ai-chart/ -n travel-ai --create-namespace
helm uninstall travel-ai -n travel-ai   # Remove everything

# ===== OLLAMA =====
ollama list                             # Show loaded models
ollama serve                            # Start Ollama server
ollama create srilanka-llama -f Modelfile   # Register our custom model
```

---

*End of document.*
