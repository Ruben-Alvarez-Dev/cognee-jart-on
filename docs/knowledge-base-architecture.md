# Knowledge Base Architecture Analysis

## Requerimientos

1. **Central**: Una sola base para todo (papers, proyectos, investigación)
2. **Categorización**: Tags, categorías, clasificación automática
3. **Queryable**: Búsqueda rápida por texto, tags, categoría
4. **Persistente**: Sobrevive sesiones, reinicios
5. **Ligero**: Mínimo overhead
6. **Actualizable**: CRUD completo
7. **Exportable**: Markdown, JSON, BibTeX
8. **Integrable**: Consultable desde cualquier proyecto

## Opciones encontradas en GitHub

### 1. Paperless-ngx ⭐⭐⭐⭐⭐

**GitHub**: https://github.com/paperless-ngx/paperless-ngx  
**Stars**: 42,892  
**License**: GPL-3.0

| Característica | Valor |
|----------------|-------|
| Tipo | Document management system |
| Backend | Django + SQLite/PostgreSQL |
| Frontend | Angular |
| OCR | Tesseract |
| Deployment | Docker |
| API | REST API completa |

**Pros:**
- ✅ Gestión completa de documentos (PDF, imágenes, etc.)
- ✅ OCR integrado (extrae texto de PDFs escaneados)
- ✅ Tags, correspondentes, tipos de documento
- ✅ Búsqueda full-text
- ✅ API REST completa
- ✅ Comunidad enorme (42K stars)
- ✅ Multi-usuario
- ✅ Consumo de email integrado

**Contras:**
- ❌ Pesado (necesita Docker, Redis, DB)
- ❌ No es específico para papers académicos
- ❌ No tiene gestión de referencias BibTeX
- ❌ Overkill para solo papers

**Veredicto**: Ideal si quieres gestión de TODOS los documentos (facturas, contratos, papers, etc.). Demasiado para solo papers académicos.

---

### 2. Zotero ⭐⭐⭐⭐

**Web**: https://www.zotero.org  
**GitHub**: https://github.com/zotero  
**Stars**: ~10K (varios repos)  
**License**: AGPL-3.0

| Característica | Valor |
|----------------|-------|
| Tipo | Reference manager |
| Backend | SQLite |
| Sync | Zotero cloud (300MB free) |
| Plugins | 1000+ plugins |
| BibTeX | Nativo |

**Pros:**
- ✅ Estándar de facto para investigación académica
- ✅ Gestión de referencias BibTeX/LaTeX
- ✅ Plugins para todo (Obsidian, Word, LaTeX)
- ✅ Sync en la nube
- ✅ Captura automática desde navegador
- ✅ Organización por colecciones y tags
- ✅ PDF reader integrado con anotaciones

**Contras:**
- ❌ No es self-hosted (usa su nube o WebDAV)
- ❌ No tiene API REST nativa (necesita plugin)
- ❌ No es un "knowledge base" general

**Veredicto**: Mejor opción para papers académicos. Combina perfectamente con Obsidian.

---

### 3. JabRef ⭐⭐⭐

**GitHub**: https://github.com/JabRef/jabref  
**Stars**: 4,340  
**License**: MIT

| Característica | Valor |
|----------------|-------|
| Tipo | BibTeX editor |
| Backend | Archivos .bib |
| Language | Java |
| Search | PubMed, arXiv, Google Scholar |

**Pros:**
- ✅ Nativo para BibTeX/LaTeX
- ✅ Búsqueda en múltiples fuentes académicas
- ✅ Importación automática de metadatos
- ✅ Open source, ligero
- ✅ Funciona sin servidor

**Contras:**
- ❌ Java (pesado)
- ❌ No tiene API
- ❌ No es un knowledge base

**Veredicto**: Bueno si usas LaTeX. No es lo que necesitamos.

---

### 4. Obsidian + Plugins ⭐⭐⭐⭐

**Web**: https://obsidian.md  
**Plugin Scholar**: https://github.com/lolipopshock/obsidian-scholar

| Característica | Valor |
|----------------|-------|
| Tipo | Knowledge base (Markdown) |
| Storage | Archivos Markdown locales |
| Graph | Knowledge graph |
| Plugins | 1000+ |
| Search | Full-text, graph-based |

**Pros:**
- ✅ Local-first, Markdown
- ✅ Knowledge graph visual
- ✅ Plugins para papers (Scholar, Zotero integration)
- ✅ Dataview para queries
- ✅ Comunidad enorme
- ✅ Funciona offline

**Contras:**
- ❌ No tiene API (necesita plugin Local REST API)
- ❌ No es multi-usuario
- ❌ No tiene gestión de PDFs integrada

**Veredicto**: Excelente como knowledge base personal. Se puede combinar con Zotero.

---

### 5. SQLite + Custom (nuestra implementación) ⭐⭐⭐⭐

**Ya implementado en**: `/Users/ruben/Code/adversarial-verifier/papers/db/papers.db`

| Característica | Valor |
|----------------|-------|
| Tipo | Custom knowledge base |
| Backend | SQLite |
| API | Python class |
| Search | SQL queries |

**Pros:**
- ✅ Ya implementado
- ✅ Ultra ligero
- ✅ SQL queries
- ✅ Persistente
- ✅ Sin dependencias

**Contras:**
- ❌ No tiene UI
- ❌ No tiene OCR
- ❌ No tiene sync
- ❌ Hay que mantenerlo

---

## Arquitecturas posibles

### Opción A: SQLite Central (recomendada para empezar)

```
/Users/ruben/.knowledge/
├── papers.db          # SQLite central
├── papers/            # PDFs y markdown
├── projects/          # Referencias por proyecto
└── exports/           # Exportaciones
```

**Ventajas:**
- Ligero, sin Docker
- Un solo archivo .db
- Consultable desde cualquier proyecto
- Python nativo

**Desventajas:**
- Sin UI web
- Sin OCR
- Sin sync

### Opción B: Paperless-ngx + SQLite

```
Docker (Paperless-ngx)
├── Documentos escaneados (PDF, imágenes)
├── OCR automático
├── Tags y categorías
└── API REST

Proyectos
├── adversarial-verifier → consulta via API
└── otros proyectos → consulta via API
```

**Ventajas:**
- OCR para PDFs escaneados
- UI web completa
- Gestión de TODOS los documentos

**Desventajas:**
- Docker obligatorio
- Más pesado
- No es específico para papers

### Opción C: Zotero + Obsidian + SQLite

```
Zotero (gestión de referencias)
├── Papers con metadatos BibTeX
├── PDFs con anotaciones
└── Sync en la nube

Obsidian (knowledge base)
├── Notas de investigación
├── Dataview queries
└── Graph view

SQLite (API para proyectos)
├── Copia de metadatos Zotero
├── Consultable desde Pi
└── Integración con adversarial-verifier
```

**Ventajas:**
- Lo mejor de los tres mundos
- Zotero para papers académicos
- Obsidian para notas y relaciones
- SQLite para integración con código

**Desventajas:**
- Más complejo
- Triple mantenimiento

### Opción D: Zotero como fuente de verdad

```
Zotero (central)
├── Todos los papers
├── BibTeX nativo
├── PDFs con anotaciones
└── API via plugin

Plugin Zotero → SQLite sync
├── Replica local en SQLite
├── Consultable desde Pi
└── Sincronización automática

Proyectos
├── adversarial-verifier → consulta SQLite
└── otros → consulta SQLite
```

**Ventajas:**
- Zotero es el estándar académico
- SQLite es ligero y consultable
- Sync automático via plugin

**Desventajas:**
- Necesita Zotero instalado
- Plugin de sync puede fallar

---

## Recomendación

### Para tu caso: **Opción D (Zotero + SQLite sync)**

**Razones:**
1. **Zotero** es el estándar para investigación académica
2. **SQLite** es ligero y consultable desde Pi/código
3. **Sync automático** entre Zotero y SQLite
4. **BibTeX nativo** para LaTeX
5. **PDFs con anotaciones** en Zotero
6. **Knowledge base** en Obsidian (opcional)

### Implementación propuesta

```
/Users/ruben/.knowledge/
├── zotero/                # Zotero data (manages itself)
├── papers.db              # SQLite central (synced from Zotero)
├── exports/               # Exportaciones Markdown
└── obsidian/              # Vault de Obsidian (opcional)

Zotero Plugin: "Better BibTeX" → auto-export .bib
Zotero Plugin: "Zotero SQLite Sync" → sync to papers.db

Pi Integration:
├── src/knowledge/database.py  # Ya implementado
├── MCP server                 # Consultar desde Pi
└── CLI                        # Consultar desde terminal
```

### Pasos inmediatos

1. **Instalar Zotero** (si no está)
2. **Instalar plugin Better BibTeX**
3. **Configurar sync Zotero → SQLite**
4. **Migrar papers existentes a Zotero**
5. **Configurar Pi para consultar SQLite**

---

## Alternativa rápida: SQLite central (sin Zotero)

Si no quieres instalar Zotero ahora, podemos usar SQLite central:

```
/Users/ruben/.knowledge/
├── papers.db              # SQLite central
├── papers/
│   ├── adversarial-verifier/  # Papers de este proyecto
│   ├── autoagent/             # Papers de AutoAgent
│   └── general/               # Papers generales
└── scripts/
    ├── add_paper.py           # Añadir paper
    ├── search.py              # Buscar
    └── export.py              # Exportar
```

**Ventajas:**
- Sin dependencias externas
- Ya implementado (migrar a central)
- Consultable desde cualquier proyecto
- Un solo archivo .db

**Desventajas:**
- Sin UI
- Sin OCR
- Sin sync automático
- Hay que añadir papers manualmente

---

## Decisión

¿Cuál prefieres?

1. **Zotero + SQLite sync** (más completo, requiere Zotero)
2. **SQLite central** (más simple, sin dependencias)
3. **Paperless-ngx** (más potente, requiere Docker)
4. **Obsidian + SQLite** (knowledge base + API)
