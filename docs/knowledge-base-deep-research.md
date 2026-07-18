# Deep Research — Knowledge Base Systems (Julio 2026)

## Investigación completa de herramientas disponibles

---

## Tier 1: Soluciones principales (más estrellas, más maduras)

### 1. SiYuan ⭐⭐⭐⭐⭐ (45K stars)

**GitHub**: https://github.com/siyuan-note/siyuan  
**Tipo**: Personal Knowledge Management (PKM)  
**Backend**: SQLite  
**License**: AGPL-3.0

| Característica | Detalle |
|----------------|---------|
| Stars | 45,000+ |
| Backend | SQLite (local) |
| API | REST API completa (`/api/*`) |
| Editor | Markdown WYSIWYG, block-level |
| Referencias | Two-way links, block references |
| OCR | Tesseract integrado |
| Sync | Nativo (nube propia o self-hosted) |
| Multi-plataforma | Desktop, Android, iOS, Docker |
| AI | OpenAI API integrada |
| Export | Markdown, PDF, Word, HTML |
| SQL queries | Nativo (`/api/query/sql`) |

**API Endpoints principales:**
```
POST /api/query/sql          — Ejecutar SQL
GET  /api/block/:id          — Obtener bloque
POST /api/block/update       — Actualizar bloque
GET  /api/file/get           — Obtener archivo
POST /api/file/put           — Subir archivo
GET  /api/search/fullText    — Búsqueda full-text
GET  /api/tag/getTags        — Obtener tags
POST /api/tag/addTag         — Añadir tag
GET  /api/attr/getBlockAttrs — Obtener atributos
POST /api/attr/setBlockAttrs — Establecer atributos
```

**Pros:**
- ✅ SQLite nativo (como nuestra implementación)
- ✅ API REST completa (consultable desde Pi)
- ✅ Block-level references (ideal para papers)
- ✅ OCR integrado (PDFs escaneados)
- ✅ AI writing integrado
- ✅ Self-hosted, privacy-first
- ✅ Knowledge graph visual
- ✅ SQL queries directas
- ✅ Comunidad enorme (45K stars)
- ✅ Multi-plataforma

**Contras:**
- ❌ No es específico para papers académicos
- ❌ No tiene gestión BibTeX nativa
- ❌ Pesado (525MB repo)

**Veredicto**: **Opción más completa**. SQLite nativo + API REST + OCR + AI = todo lo que necesitas.

---

### 2. Cognee ⭐⭐⭐⭐⭐ (28K stars)

**GitHub**: https://github.com/topoteretes/cognee  
**Tipo**: AI Memory Platform for Agents  
**Backend**: SQLite + Knowledge Graph  
**License**: Apache-2.0

| Característica | Detalle |
|----------------|---------|
| Stars | 28,000+ |
| Backend | SQLite + Neo4j/Kuzu |
| API | Python SDK + REST |
| Knowledge Graph | Nativo |
| Multi-modal | Texto, imágenes, audio |
| LLM integration | OpenAI, Anthropic, local |
| MCP server | Integrado |
| Docker | Soportado |

**Operaciones principales:**
```python
import cognee

# Almacenar permanentemente
await cognee.remember("Documento importante...")

# Recuperar
results = await cognee.recall("¿Qué es...?")

# Olvidar
await cognee.forget(dataset="main_dataset")
```

**Pros:**
- ✅ **Knowledge graph nativo** (ideal para relaciones entre papers)
- ✅ **Persistent memory para agentes** (cruza sesiones)
- ✅ **Multi-modal** (texto, imágenes, audio)
- ✅ **MCP server** integrado (Pi puede usarlo directamente)
- ✅ **Multi-tenant** (aislamiento por proyecto)
- ✅ **Ontology grounding** (clasificación automática)
- ✅ CLI + API + Docker

**Contras:**
- ❌ Más complejo que SQLite simple
- ❌ Necesita LLM API key para clasificación
- ❌ Overkill para solo almacenar papers

**Veredicto**: **Mejor para AI agents**. Si quieres que Pi tenga memoria persistente de papers, Cognee es la opción.

---

### 3. Trilium Notes ⭐⭐⭐⭐ (28K stars)

**GitHub**: https://github.com/TriliumNext/Trilium  
**Tipo**: Personal Knowledge Base  
**Backend**: SQLite  
**License**: AGPL-3.0

| Característica | Detalle |
|----------------|---------|
| Stars | 28,000+ |
| Backend | SQLite |
| API | REST API (`/api/*`) |
| Editor | WYSIWYG + Markdown |
| Referencias | Two-way links |
| Scripting | JavaScript integrado |
| Sync | Nativo |
| Multi-plataforma | Desktop, Web, Mobile |

**API Endpoints:**
```
GET  /api/notes/:noteId         — Obtener nota
POST /api/notes/:noteId/content — Actualizar contenido
PUT  /api/notes/:noteId         — Actualizar nota
POST /api/notes                 — Crear nota
DELETE /api/notes/:noteId       — Eliminar nota
GET  /api/search                — Buscar
```

**Pros:**
- ✅ SQLite nativo
- ✅ API REST completa
- ✅ JavaScript scripting (automatización)
- ✅ Self-hosted
- ✅ Knowledge graph

**Contras:**
- ❌ No tiene OCR
- ❌ No tiene AI integrado
- ❌ UI menos pulida que SiYuan

**Veredicto**: **Alternativa sólida a SiYuan**. Más ligero, menos features.

---

### 4. Paperless-ngx ⭐⭐⭐⭐⭐ (43K stars)

**GitHub**: https://github.com/paperless-ngx/paperless-ngx  
**Tipo**: Document Management System  
**Backend**: Django + SQLite/PostgreSQL  
**License**: GPL-3.0

| Característica | Detalle |
|----------------|---------|
| Stars | 43,000+ |
| Backend | Django + SQLite/PostgreSQL |
| API | REST API completa |
| OCR | Tesseract integrado |
| Tags | Nativo |
| Correspondentes | Nativo |
| Tipos documento | Nativo |
| Multi-usuario | Sí |
| Email consume | Integrado |

**Pros:**
- ✅ **OCR automático** (PDFs escaneados)
- ✅ **API REST completa**
- ✅ **Tags, correspondentes, tipos**
- ✅ **Búsqueda full-text**
- ✅ **Multi-usuario**
- ✅ **Email consume** (recibe documentos por email)
- ✅ **43K stars** (comunidad enorme)

**Contras:**
- ❌ Docker obligatorio
- ❌ No es para papers académicos
- ❌ No tiene BibTeX
- ❌ Overkill para solo papers

**Veredicto**: **Mejor para gestión de TODOS los documentos** (facturas, contratos, papers, etc.). Demasiado para solo papers académicos.

---

## Tier 2: Soluciones especializadas

### 5. Zotero ⭐⭐⭐⭐

**Web**: https://www.zotero.org  
**GitHub**: https://github.com/zotero  
**Stars**: ~10K (varios repos)

| Característica | Detalle |
|----------------|---------|
| Tipo | Reference Manager |
| Backend | SQLite |
| API | Plugin (Better BibTeX) |
| BibTeX | Nativo |
| PDFs | Reader integrado |
| Sync | Zotero cloud (300MB free) |
| Plugins | 1000+ |

**Pros:**
- ✅ **Estándar académico**
- ✅ **BibTeX/LaTeX nativo**
- ✅ **Captura automática** desde navegador
- ✅ **PDF reader** con anotaciones
- ✅ **Plugins** para todo (Obsidian, Word, LaTeX)
- ✅ **Sync en la nube**

**Contras:**
- ❌ No es self-hosted (usa su nube o WebDAV)
- ❌ No tiene API REST nativa
- ❌ No es knowledge base general

**Veredicto**: **Mejor para papers académicos**. Se puede combinar con SQLite sync.

---

### 6. Obsidian ⭐⭐⭐⭐

**Web**: https://obsidian.md  
**Tipo**: Knowledge Base (Markdown)  
**Storage**: Archivos Markdown locales  
**License**: Propietario (gratis para uso personal)

| Característica | Detalle |
|----------------|---------|
| Storage | Markdown local |
| Knowledge Graph | Nativo |
| Plugins | 1000+ |
| Search | Full-text, graph-based |
| API | Plugin Local REST API |
| Sync | Nativo (pago) o iCloud/Dropbox |

**Pros:**
- ✅ **Local-first, Markdown**
- ✅ **Knowledge graph visual**
- ✅ **Plugins** (Scholar, Zotero, Dataview)
- ✅ **Dataview** para queries SQL-like
- ✅ **Comunidad enorme**

**Contras:**
- ❌ No tiene API nativa (necesita plugin)
- ❌ No es multi-usuario
- ❌ No tiene OCR integrado

**Veredicto**: **Excelente como knowledge base personal**. Se puede combinar con Zotero + SQLite.

---

## Tier 3: Soluciones emergentes

### 7. linXiv ⭐⭐⭐

**GitHub**: https://github.com/fzhiy/noria  
**Tipo**: Academic paper manager  
**Backend**: SQLite  
**Features**: arXiv integration, AI tagging, Obsidian vault

**Pros:**
- ✅ Específico para papers académicos
- ✅ SQLite nativo
- ✅ arXiv integration
- ✅ AI-powered tagging
- ✅ Obsidian integration

**Contras:**
- ❌ Nuevo, menos maduro
- ❌ Comunidad pequeña

---

### 8. Cognee MCP Server ⭐⭐⭐⭐

**GitHub**: https://github.com/topoteretes/cognee  
**Tipo**: MCP server for AI agents  
**Features**: Knowledge graph, persistent memory, multi-modal

**Pros:**
- ✅ **MCP server nativo** (Pi puede usarlo directamente)
- ✅ Knowledge graph
- ✅ Persistent memory across sessions
- ✅ Multi-modal

**Contras:**
- ❌ Más complejo
- ❌ Necesita LLM API key

---

## Comparativa final

| Sistema | Stars | SQLite | API | OCR | Knowledge Graph | BibTeX | MCP | Self-hosted |
|---------|-------|--------|-----|-----|-----------------|--------|-----|-------------|
| **SiYuan** | 45K | ✅ | REST | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Cognee** | 28K | ✅ | REST+MCP | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Trilium** | 28K | ✅ | REST | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Paperless** | 43K | ✅ | REST | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Zotero** | 10K | ✅ | Plugin | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Obsidian** | — | ❌ | Plugin | ❌ | ✅ | Plugin | ❌ | ✅ |
| **SQLite custom** | — | ✅ | Python | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Recomendación final

### Para tu caso específico: **SiYuan + SQLite sync**

**Por qué:**
1. **SQLite nativo** — como nuestra implementación actual, pero con UI
2. **API REST completa** — consultable desde Pi/código
3. **OCR integrado** — PDFs escaneados
4. **Knowledge graph** — relaciones entre papers
5. **Self-hosted** — privacy-first
6. **45K stars** — comunidad activa, software maduro
7. **Multi-plataforma** — desktop, mobile, Docker

### Arquitectura propuesta

```
SiYuan (knowledge base central)
├── Papers académicos (PDFs + metadatos)
├── Notas de investigación
├── Knowledge graph
├── API REST (/api/query/sql)
└── OCR automático

SQLite sync (para proyectos)
├── /Users/ruben/.knowledge/papers.db
├── Replica de metadatos SiYuan
├── Consultable desde Pi
└── Integración con adversarial-verifier

Pi Integration
├── MCP server para SiYuan API
├── Consultas SQL directas
└── Sync automático
```

### Pasos inmediatos

1. **Instalar SiYuan** (Docker o app nativa)
2. **Importar papers existentes** (PDFs + markdown)
3. **Configurar sync SiYuan → SQLite**
4. **Crear MCP server** para Pi
5. **Integrar con adversarial-verifier**

### Alternativa rápida: SQLite central (sin SiYuan)

Si no quieres instalar SiYuan ahora:
```
/Users/ruben/.knowledge/
├── papers.db              # SQLite central
├── papers/                # PDFs + markdown
└── scripts/
    ├── add_paper.py
    ├── search.py
    └── export.py
```

**Ventajas:**
- Sin dependencias externas
- Ya implementado
- Consultable desde cualquier proyecto

**Desventajas:**
- Sin UI
- Sin OCR
- Sin knowledge graph

---

## Decisión

¿Cuál prefieres?

1. **SiYuan** — Lo más completo (UI + API + OCR + Knowledge Graph)
2. **Cognee** — Mejor para AI agents (MCP + persistent memory)
3. **SQLite central** — Lo más simple (ya implementado)
4. **Zotero + SQLite** — Mejor para papers académicos
5. **Paperless-ngx** — Mejor para gestión de documentos
