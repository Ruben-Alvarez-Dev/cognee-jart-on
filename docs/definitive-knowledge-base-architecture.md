# Arquitectura Definitiva — Knowledge Base Distribuido con AI

## La pieza clave: SQLite-Sync

**GitHub**: https://github.com/sqliteai/sqlite-sync  
**Tipo**: CRDT-based offline-first sync for SQLite  
**License**: Open source

### Qué hace SQLite-Sync

Convierte cualquier SQLite en una **réplica conflict-free** que sincroniza automáticamente con:
- SQLite Cloud (gestionado)
- PostgreSQL (self-hosted)
- Supabase (self-hosted)

**Una sola llamada de función** para sincronizar. Sin backend que construir.

### Características clave

| Feature | Descripción |
|---------|-------------|
| **CRDT-based** | Conflict-free Replicated Data Types |
| **Block-Level LWW** | Merge a nivel de línea para markdown |
| **Offline-first** | Cola local, sync cuando hay conexión |
| **Multi-platform** | Linux, macOS, Windows, iOS, Android, WASM |
| **Row-Level Security** | Cada cliente solo ve sus filas |
| **Built-in networking** | libcurl integrado, una función para sync |

### Cómo funciona

```sql
-- 1. Cargar extensión
.load ./cloudsync

-- 2. Crear tabla
CREATE TABLE papers (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    tags TEXT
);

-- 3. Habilitar sync CRDT
SELECT cloudsync_init('papers');

-- 4. Usar normalmente
INSERT INTO papers (id, title) VALUES (cloudsync_uuid(), 'Mi paper');

-- 5. Sincronizar
SELECT cloudsync_network_sync();
-- Returns: {"send":{"status":"synced"},"receive":{"rows":0}}
```

### Plataformas soportadas

| Plataforma | Instalación |
|------------|-------------|
| **SQLite CLI / C** | `.load ./cloudsync` |
| **Swift (iOS)** | Swift Package |
| **Android** | `implementation 'ai.sqlite:sync:1.0.0'` |
| **Flutter** | `flutter pub add sqlite_sync` |
| **Expo** | `npm install @sqliteai/sqlite-sync-expo` |
| **React Native** | `npm install @sqliteai/sqlite-sync-react-native` |
| **WASM** | `npm install @sqliteai/sqlite-wasm` |

---

## Arquitectura definitiva: Cognee + SQLite-Sync

### La combinación ganadora

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE DEFINITIVO                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  COGNEE (AI Layer)                                      │   │
│  │  ├── Knowledge Graph (relaciones entre papers)          │   │
│  │  ├── Semantic Search (embeddings + graph)               │   │
│  │  ├── MCP Server (para Pi)                               │   │
│  │  ├── On-device (Rust core para mobile)                  │   │
│  │  └── remember/recall/forget API                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SQLite-Sync (Sync Layer)                               │   │
│  │  ├── CRDT-based conflict-free merge                     │   │
│  │  ├── Block-Level LWW (para markdown)                    │   │
│  │  ├── Offline-first (cola local)                         │   │
│  │  ├── Multi-platform (iOS, Android, Mac, Web)            │   │
│  │  └── Row-Level Security                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SQLite (Storage Layer)                                 │   │
│  │  ├── Papers (metadatos, abstracts, tags)                │   │
│  │  ├── Notes (notas de investigación)                     │   │
│  │  ├── Sources (URLs, referencias)                        │   │
│  │  ├── Embeddings (vectores para búsqueda semántica)      │   │
│  │  └── Graph (relaciones entre entidades)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Arquitectura distribuida

```
Mac Mini (Primary Server)
┌──────────────────────────────────────────┐
│ Cognee (Python full stack)               │
│ ├── Knowledge Graph engine               │
│ ├── Semantic search                      │
│ ├── MCP server                           │
│ └── REST API                             │
│                                          │
│ SQLite-Sync (server side)                │
│ ├── PostgreSQL o Supabase                │
│ └── CloudSync microservice               │
│                                          │
│ SQLite DB                                │
│ ├── papers.db (con sync CRDT)            │
│ └── knowledge.db (Cognee graph)          │
└─────────────────┬────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ iPhone  │ │ iPad    │ │ Mac     │
│         │ │         │ │ Book    │
│ Cognee  │ │ Cognee  │ │ Cognee  │
│ (Rust)  │ │ (Rust)  │ │ (Rust)  │
│         │ │         │ │         │
│ SQLite  │ │ SQLite  │ │ SQLite  │
│ -Sync   │ │ -Sync   │ │ -Sync   │
│ (CRDT)  │ │ (CRDT)  │ │ (CRDT)  │
└─────────┘ └─────────┘ └─────────┘
```

### Flujo de datos

```
1. Usuario añade paper en iPhone
   │
   ▼
2. Cognee-rs procesa (on-device)
   ├── Extrae metadatos
   ├── Crea embeddings
   ├── Actualiza knowledge graph
   └── Guarda en SQLite local
   │
   ▼
3. SQLite-Sync detecta cambios
   ├── CRDT merge (sin conflictos)
   ├── Cola local (offline)
   └── Sync cuando hay conexión
   │
   ▼
4. PostgreSQL/Supabase recibe cambios
   │
   ▼
5. Mac Mini detecta cambios
   ├── SQLite-Sync descarga cambios
   ├── Cognee actualiza knowledge graph
   └── Pi puede consultar via MCP
   │
   ▼
6. iPad detecta cambios
   ├── SQLite-Sync descarga cambios
   └── Cognee-rs actualiza localmente
```

### Implementación concreta

#### Paso 1: SQLite schema con sync

```sql
-- papers.sql
CREATE TABLE papers (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    abstract TEXT,
    arxiv_url TEXT,
    github_url TEXT,
    tags TEXT,
    category TEXT,
    relevance_score REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    paper_id TEXT,
    content TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE relations (
    id TEXT PRIMARY KEY,
    source_id TEXT,
    target_id TEXT,
    relation_type TEXT,
    metadata TEXT
);

-- Habilitar CRDT sync
SELECT cloudsync_init('papers');
SELECT cloudsync_init('notes');
SELECT cloudsync_init('relations');
```

#### Paso 2: Cognee integration

```python
# cognee_integration.py
import cognee
import sqlite3

class CogneeKnowledgeBase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    async def add_paper(self, paper: dict):
        """Añadir paper con procesamiento AI"""
        # Guardar en SQLite (sync automático)
        self.conn.execute("""
            INSERT INTO papers (id, title, authors, abstract, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (paper['id'], paper['title'], paper['authors'], 
              paper['abstract'], ','.join(paper.get('tags', []))))
        self.conn.commit()
        
        # Procesar con Cognee (knowledge graph)
        await cognee.remember(f"""
        Paper: {paper['title']}
        Authors: {paper['authors']}
        Abstract: {paper['abstract']}
        Tags: {', '.join(paper.get('tags', []))}
        """)
    
    async def search(self, query: str):
        """Búsqueda semántica + graph"""
        # Búsqueda en SQLite
        cursor = self.conn.execute("""
            SELECT * FROM papers 
            WHERE title LIKE ? OR abstract LIKE ?
        """, (f'%{query}%', f'%{query}%'))
        sql_results = cursor.fetchall()
        
        # Búsqueda semántica con Cognee
        cognee_results = await cognee.recall(query)
        
        return {
            'sql': sql_results,
            'semantic': cognee_results
        }
```

#### Paso 3: Sync configuration

```python
# sync_config.py
import sqlite3

def setup_sync(db_path: str, cloud_id: str, api_key: str):
    """Configurar sync CRDT"""
    conn = sqlite3.connect(db_path)
    
    # Cargar extensión
    conn.enable_load_extension(True)
    conn.load_extension('./cloudsync')
    
    # Conectar a la nube
    conn.execute(f"SELECT cloudsync_network_init('{cloud_id}')")
    conn.execute(f"SELECT cloudsync_network_set_apikey('{api_key}')")
    
    return conn

def sync(conn):
    """Sincronizar cambios"""
    result = conn.execute("SELECT cloudsync_network_sync()").fetchone()
    return json.loads(result[0])
```

#### Paso 4: MCP server para Pi

```python
# mcp_server.py
from mcp import MCPServer, tool

server = MCPServer("knowledge-base")

@tool("add_paper")
async def add_paper(title: str, authors: str, abstract: str, tags: list):
    """Añadir paper a la base de conocimiento"""
    kb = CogneeKnowledgeBase("/Users/ruben/.knowledge/papers.db")
    await kb.add_paper({
        'id': str(uuid.uuid4()),
        'title': title,
        'authors': authors,
        'abstract': abstract,
        'tags': tags
    })
    return {"status": "added", "title": title}

@tool("search_papers")
async def search_papers(query: str):
    """Buscar papers por contenido"""
    kb = CogneeKnowledgeBase("/Users/ruben/.knowledge/papers.db")
    results = await kb.search(query)
    return results

@tool("sync")
async def sync_now():
    """Forzar sincronización"""
    conn = setup_sync("/Users/ruben/.knowledge/papers.db", ...)
    result = sync(conn)
    return result

server.run()
```

---

## Resumen: el sistema definitivo

### Componentes

| Componente | Rol | Fuente |
|------------|-----|--------|
| **Cognee** | AI layer (knowledge graph, semantic search) | github.com/topoteretes/cognee |
| **SQLite-Sync** | Sync layer (CRDT, offline-first) | github.com/sqliteai/sqlite-sync |
| **SQLite** | Storage layer (papers, notes, relations) | Nativo |
| **Pi** | Orchestrator (MCP server) | Tu setup actual |

### Características

| Característica | Implementación |
|----------------|----------------|
| **Distribuido** | ✅ SQLite-Sync (CRDT) |
| **Offline-first** | ✅ Cola local, sync cuando hay conexión |
| **Multi-device** | ✅ iOS, Android, Mac, Windows, Web |
| **AI-powered** | ✅ Cognee (knowledge graph, semantic search) |
| **Conflict-free** | ✅ CRDT (no hay conflictos manuales) |
| **Markdown-aware** | ✅ Block-Level LWW |
| **Self-hosted** | ✅ PostgreSQL o Supabase |
| **API** | ✅ MCP server + REST |
| **Ligero** | ✅ SQLite nativo |

### Pasos para implementar

1. **Instalar SQLite-Sync** (extensión SQLite)
2. **Configurar PostgreSQL/Supabase** (self-hosted)
3. **Instalar Cognee** (pip install cognee)
4. **Crear schema SQLite** con CRDT sync
5. **Implementar CogneeKnowledgeBase** class
6. **Crear MCP server** para Pi
7. **Configurar sync** en cada dispositivo
8. **Probar** multi-device sync

### Timeline

| Fase | Duración | Entregable |
|------|----------|------------|
| SQLite-Sync setup | 1 día | Sync funcionando |
| Cognee integration | 2 días | AI layer funcionando |
| MCP server | 1 día | Pi integration |
| Multi-device | 2 días | iOS/Android apps |
| Testing | 1 día | Validación completa |
| **Total** | **1 semana** | Sistema completo |

---

## Decisión

¿Empezamos a construirlo?

1. **Sí, empecemos** — Implementar SQLite-Sync + Cognee
2. **Primero prototipo** — Solo SQLite-Sync, sin Cognee
3. **Necesito más info** — Quiero ver más detalles antes de decidir
