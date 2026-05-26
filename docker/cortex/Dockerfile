FROM thehiveproject/cortex:3.1.7

USER root

# ── Dépendances système ───────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    libmagic1 \
    libffi-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Mettre à jour pip ─────────────────────────
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel --break-system-packages 2>/dev/null || \
    python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# ── cortexutils 2.2.1 (dernière version dispo) ──
RUN python3 -m pip install --no-cache-dir \
    "cortexutils==2.2.1" \
    requests \
    future \
    six \
    python-magic \
    --break-system-packages 2>/dev/null || \
    python3 -m pip install --no-cache-dir \
    "cortexutils==2.2.1" \
    requests \
    future \
    six \
    python-magic

# ── Cloner les analyseurs officiels ───────────
WORKDIR /opt
RUN git clone --depth 1 \
    https://github.com/TheHive-Project/Cortex-Analyzers.git \
    || echo "Clone failed"

# ── Installer les dépendances des analyseurs ──
RUN if [ -d /opt/Cortex-Analyzers ]; then \
    find /opt/Cortex-Analyzers/analyzers -name "requirements.txt" \
        -exec python3 -m pip install --no-cache-dir -r {} \
        --break-system-packages 2>/dev/null \; || true; \
fi

# ── Permissions ───────────────────────────────
RUN mkdir -p /tmp/cortex-jobs && chmod 777 /tmp/cortex-jobs

RUN if [ -d /opt/Cortex-Analyzers ]; then \
    chmod -R 755 /opt/Cortex-Analyzers; \
fi

WORKDIR /opt/cortex