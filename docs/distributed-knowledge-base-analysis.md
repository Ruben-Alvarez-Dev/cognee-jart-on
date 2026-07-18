# Análisis: Knowledge Base Distribuido con Sincronización Multi-dispositivo

## Requerimientos del usuario

1. **Distribuido**: Satélites/apps en todos los dispositivos
2. **Sincronización**: Todos los dispositivos sincronizados entre sí
3. **Offline-first**: Funciona sin conexión, sincroniza cuando hay red
4. **Central**: Una sola fuente de verdad
5. **Ligero**: No pesado en recursos
6. **Reactivo**: Consultas rápidas

---

## Análisis por sistema

### 1. SiYuan ⭐⭐⭐⭐⭐ (45K stars)

#### Capacidad de sincronización

| Característica | Detalle |
|----------------|---------|
| **Sync nativo** | Sí, integrado |
| **Cloud propia** | SiYuan Cloud (gratis 1GB, pago más) |
| **Self-hosted sync** | Sí, con Docker |
| **S3/WebDAV** | Soportado |
| **Offline-first** | Sí |
| **Multi-device** | Desktop (Win/Mac/Linux), Android, iOS, Web |
| **Conflict resolution** | Automático (última escritura gana) |
| **Encryption** | End-to-end encryption opcional |

#### Arquitectura de sync

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Mac Mini  │     │   iPhone    │     │   iPad      │
│  (Primary)  │     │  (Satellite)│     │  (Satellite)│
│  SiYuan App │     │  SiYuan App │     │  SiYuan App │
│  SQLite DB  │     │  SQLite DB  │     │  SQLite DB  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  SiYuan     │
                    │  Cloud o    │
                    │  Self-hosted│
                    │  Server     │
                    └─────────────┘
```

#### Pros para tu caso
- ✅ **Sync nativo** — no necesitas configurar nada extra
- ✅ **SQLite en cada dispositivo** — como nuestra implementación actual
- ✅ **API REST** — consultable desde Pi en cualquier dispositivo
- ✅ **OCR** — PDFs escaneados se procesan automáticamente
- ✅ **Knowledge graph** — relaciones visuales entre papers
- ✅ **Multi-plataforma** — todos tus dispositivos
- ✅ **Offline-first** — funciona sin conexión

#### Contras
- ❌ Sync puede ser lento con muchos archivos
- ❌ Conflictos resueltos por "última escritura" (no merge inteligente)
- ❌ Cloud propia tiene límites (1GB gratis)

#### Veredicto: **Opción más completa para tu caso**

---

### 2. Cognee ⭐⭐⭐⭐⭐ (28K stars)

#### Capacidad de sincronización

| Característica | Detalle |
|----------------|---------|
| **Sync nativo** | Parcial (en desarrollo) |
| **On-device** | Sí (Rust core) |
| **Multi-device** | Desktop, Mobile (Android/iOS), Edge devices |
| **Offline-first** | Sí (Rust core funciona sin conexión)
| **Distributed** | Sí (multi-tenant, multi-agent)
| **Knowledge graph** | Nativo
| **MCP server** | Integrado

#### Arquitectura distribuida

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Mac Mini  │     │   iPhone    │     │   iPad      │
│  Cognee     │     │  Cognee-rs  │     │  Cognee-rs  │
│  (Python)   │     │  (Rust)     │     │  (Rust)     │
│  Full stack │     │  On-device  │     │  On-device  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Cognee     │
                    │  Cloud o    │
                    │  Self-hosted│
                    │  Server     │
                    └─────────────┘
```

#### On-device (Rust core)

Cognee tiene un core en Rust que corre **directamente en dispositivos**:
- **Samsung Galaxy S24 Ultra**: 139s para procesar "Alice in Wonderland"
- **Búsqueda local**: ~1 segundo
- **Sin servidor necesario**: funciona offline
- **CPU-first**: no necesita GPU

```rust
// cognee-rs en un dispositivo
let memory = CogneeMemory::new();
memory.remember("Paper importante...").await;
let results = memory.recall("¿Qué es...?").await;
```

#### Pros para tu caso
- ✅ **On-device** — funciona en iPhone/iPad sin servidor
- ✅ **Knowledge graph nativo** — relaciones entre papers
- ✅ **MCP server** — Pi puede usarlo directamente
- ✅ **Multi-agent** — cada agente puede tener su memoria
- ✅ **Offline-first** — funciona sin conexión
- ✅ **Rust core** — rápido y ligero

#### Contras
- ❌ Sync entre dispositivos aún en desarrollo
- ❌ Más complejo que SiYuan
- ❌ Necesita LLM API para clasificación

#### Veredicto: **Mejor para AI agents, pero sync incompleto**

---

### 3. Trilium Notes ⭐⭐⭐⭐ (28K stars)

#### Capacidad de sincronización

| Característica | Detalle |
|----------------|---------|
| **Sync nativo** | Sí |
| **Arquitectura** | Client-Server |
| **Server** | Node.js (self-hosted)
| **Multi-device** | Desktop (Win/Mac/Linux), Web, Android
| **Offline-first** | Sí
| **Conflict resolution** | Sync automático

#### Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Mac Mini  │     │   iPhone    │     │   Web       │
│  Trilium    │     │  Trilium    │     │  Browser    │
│  Desktop    │     │  Mobile     │     │             │
│  SQLite     │     │  SQLite     │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Trilium    │
                    │  Server     │
                    │  (Node.js)  │
                    └─────────────┘
```

#### Pros para tu caso
- ✅ **Sync nativo** — probado y maduro
- ✅ **SQLite en cada dispositivo**
- ✅ **API REST** — consultable desde Pi
- ✅ **JavaScript scripting** — automatización
- ✅ **Self-hosted** — control total
- ✅ **28K stars** — software maduro

#### Contras
- ❌ No tiene OCR
- ❌ No tiene AI integrado
- ❌ UI menos pulida
- ❌ Mobile app básica

#### Veredicto: **Alternativa sólida, menos features que SiYuan**

---

### 4. Zotero ⭐⭐⭐⭐

#### Capacidad de sincronización

| Característica | Detalle |
|----------------|---------|
| **Sync nativo** | Sí (Zotero Cloud) |
| **Cloud propia** | 300MB gratis, 2GB/$20/año, 6GB/$60/año |
| **Self-hosted** | WebDAV (complejo)
| **Multi-device** | Desktop, iOS, Android, Web
| **Offline-first** | Sí
| **Conflict resolution** | Automático

#### Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Mac       │     │   iPhone    │     │   iPad      │
│  Zotero     │     │  Zotero     │     │  Zotero     │
│  Desktop    │     │  iOS        │     │  iOS        │
│  SQLite     │     │  SQLite     │     │  SQLite     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Zotero     │
                    │  Cloud      │
                    │  (propio)   │
                    └─────────────┘
```

#### Pros para tu caso
- ✅ **Estándar académico** — el mejor para papers
- ✅ **Sync nativo** — funciona bien
- ✅ **BibTeX/LaTeX** — nativo
- ✅ **PDF reader** con anotaciones
- ✅ **Captura automática** desde navegador
- ✅ **Plugins** para Obsidian, Word, LaTeX

#### Contras
- ❌ **No es self-hosted** (usa su nube o WebDAV complejo)
- ❌ **No tiene API REST** nativa (necesita plugin)
- ❌ **No es knowledge base** general
- ❌ **Límites de storage** (300MB gratis)

#### Veredicto: **Mejor para papers académicos, pero no es knowledge base**

---

### 5. Obsidian ⭐⭐⭐

#### Capacidad de sincronización

| Característica | Detalle |
|----------------|---------|
| **Sync nativo** | Sí (pago: $4/mes) |
| **iCloud/Dropbox** | Soportado (gratis)
| **Self-hosted** | No nativo (necesita sync cloud)
| **Multi-device** | Desktop, iOS, Android
| **Offline-first** | Sí
| **Conflict resolution** | Manual

#### Pros
- ✅ **Knowledge graph visual**
- ✅ **Dataview** para queries
- ✅ **Plugins** (Scholar, Zotero)
- ✅ **Markdown** puro

#### Contras
- ❌ **Sync de pago** ($4/mes) o usar iCloud/Dropbox
- ❌ **No tiene API** nativa
- ❌ **No tiene OCR**

#### Veredicto: **Buen complemento, no base principal**

---

## Comparativa de sincronización

| Sistema | Sync nativo | Self-hosted | Offline-first | Multi-device | API REST |
|---------|-------------|-------------|---------------|--------------|----------|
| **SiYuan** | ✅ | ✅ | ✅ | ✅ (5 plataformas) | ✅ |
| **Cognee** | Parcial | ✅ | ✅ (Rust) | ✅ (on-device) | ✅ |
| **Trilium** | ✅ | ✅ | ✅ | ✅ (4 plataformas) | ✅ |
| **Zotero** | ✅ | WebDAV | ✅ | ✅ (4 plataformas) | Plugin |
| **Obsidian** | $4/mes | ❌ | ✅ | ✅ (3 plataformas) | Plugin |

---

## Recomendación final para sistema distribuido

### Opción 1: **SiYuan** (recomendada)

**Por qué:**
- ✅ Sync nativo integrado (cloud propia o self-hosted)
- ✅ SQLite en cada dispositivo
- ✅ API REST para Pi
- ✅ OCR, Knowledge graph, AI
- ✅ 5 plataformas (Mac, Windows, Linux, Android, iOS)
- ✅ Offline-first
- ✅ 45K stars, software maduro

**Arquitectura:**
```
Mac Mini (primario)          iPhone              iPad
┌──────────────────┐    ┌──────────────┐    ┌──────────────┐
│ SiYuan Server    │    │ SiYuan App   │    │ SiYuan App   │
│ (Docker)         │    │ (satellite)  │    │ (satellite)  │
│ SQLite DB        │◄──►│ SQLite DB    │◄──►│ SQLite DB    │
│ API REST         │    │ Offline-first│    │ Offline-first│
│ OCR              │    │              │    │              │
└────────┬─────────┘    └──────────────┘    └──────────────┘
         │
         ▼
   Pi Integration
   (MCP server o API)
```

### Opción 2: **Cognee** (si quieres AI agents)

**Por qué:**
- ✅ On-device (Rust core) — funciona en iPhone/iPad
- ✅ Knowledge graph nativo
- ✅ MCP server para Pi
- ✅ Multi-agent memory
- ⚠️ Sync entre dispositivos aún en desarrollo

**Arquitectura:**
```
Mac Mini (primario)          iPhone              iPad
┌──────────────────┐    ┌──────────────┐    ┌──────────────┐
│ Cognee (Python)  │    │ Cognee-rs    │    │ Cognee-rs    │
│ Full stack       │    │ (Rust)       │    │ (Rust)       │
│ Knowledge graph  │◄──►│ On-device    │◄──►│ On-device    │
│ MCP server       │    │ Offline      │    │ Offline      │
└────────┬─────────┘    └──────────────┘    └──────────────┘
         │
         ▼
   Pi Integration
   (MCP server)
```

### Opción 3: **Zotero + SiYuan** (híbrido)

**Por qué:**
- Zotero para gestión académica (BibTeX, PDFs, sync)
- SiYuan para knowledge base (notas, relaciones, API)
- Sync entre ambos via plugin/script

**Arquitectura:**
```
Zotero (papers académicos)
├── BibTeX nativo
├── PDFs con anotaciones
└── Sync cloud

SiYuan (knowledge base)
├── Notas de investigación
├── Knowledge graph
├── API REST
└── Sync self-hosted

Bridge (sync Zotero → SiYuan)
├── Exporta metadatos Zotero
├── Importa en SiYuan
└── Sincronización bidireccional
```

---

## Decisión

¿Cuál prefieres?

1. **SiYuan** — Lo más completo para sistema distribuido
2. **Cognee** — Mejor para AI agents, pero sync incompleto
3. **Zotero + SiYuan** — Lo mejor de ambos mundos
4. **Trilium** — Alternativa sólida, menos features
