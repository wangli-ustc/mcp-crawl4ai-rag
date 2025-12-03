# Knowledge Graph Architecture

<cite>
**Referenced Files in This Document**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py)
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py)
- [CODE_FLOW_DIAGRAM.md](file://CODE_FLOW_DIAGRAM.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the knowledge graph system architecture for modeling source code and Simics Device Modeling Language (DML) content. It covers:
- Neo4j schema design for nodes and relationships
- Parsing workflows from source code to graph population
- AI hallucination detection via graph validation and script analysis
- Query interfaces for exploration and domain-specific insights
- Use cases for code validation, dependency analysis, and cross-referencing

## Project Structure
The knowledge graph system is organized around a set of Python modules that:
- Parse and extract structural information from Python and DML sources
- Populate Neo4j with nodes and relationships
- Provide query interfaces for exploration and domain-specific analytics
- Validate AI-generated scripts against the knowledge graph to detect hallucinations

```mermaid
graph TB
subgraph "Parsing"
A["parse_repo_into_neo4j.py"]
B["parse_simics_into_neo4j.py"]
C["simics_dml_parser.py"]
D["simics_test_analyzer.py"]
end
subgraph "Graph Population"
E["Neo4j (via bolt)"]
end
subgraph "Validation"
F["knowledge_graph_validator.py"]
G["ai_script_analyzer.py"]
H["ai_hallucination_detector.py"]
end
subgraph "Query"
I["query_knowledge_graph.py"]
J["query_simics_knowledge_graph.py"]
end
A --> E
B --> E
C --> B
D --> B
G --> F
H --> F
I --> E
J --> E
```

**Diagram sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L1-L120)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L1-L120)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L1-L120)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py#L1-L120)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L1-L120)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py#L1-L120)
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L1-L120)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L1-L120)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L1-L120)

**Section sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L1-L120)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L1-L120)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L1-L120)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py#L1-L120)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L1-L120)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L1-L120)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L1-L120)
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L1-L120)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py#L1-L120)

## Core Components
- Neo4j graph population:
  - Python repository analyzer and extractor
  - Simics-aware extractor for DML, tests, and Python
- Structural parsers:
  - DML parser for devices, interfaces, methods, attributes, registers
  - Simics test analyzer extending Python AST analysis
- Validation and query:
  - Knowledge graph validator for imports, classes, methods, attributes, functions
  - Query interfaces for general and Simics-specific exploration
  - AI hallucination detector orchestrating analyzer and validator

**Section sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L1-L120)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L1-L120)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L1-L120)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py#L1-L120)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L1-L120)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L1-L120)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L1-L120)
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L1-L120)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py#L1-L120)

## Architecture Overview
The system follows a layered architecture:
- Data ingestion layer: parsers and extractors populate Neo4j
- Graph layer: nodes and relationships represent code structure
- Validation layer: graph-backed checks for AI-generated scripts
- Query layer: interactive and domain-specific interfaces

```mermaid
graph TB
subgraph "Ingestion"
P["Python AST Parser<br/>parse_repo_into_neo4j.py"]
S["Simics Extractor<br/>parse_simics_into_neo4j.py"]
D["DML Parser<br/>simics_dml_parser.py"]
T["Test Analyzer<br/>simics_test_analyzer.py"]
end
subgraph "Graph"
N["Neo4j (bolt)"]
end
subgraph "Validation"
V["Knowledge Graph Validator<br/>knowledge_graph_validator.py"]
A["AI Script Analyzer<br/>ai_script_analyzer.py"]
H["Hallucination Detector<br/>ai_hallucination_detector.py"]
end
subgraph "Query"
Q["General Query<br/>query_knowledge_graph.py"]
QS["Simics Query<br/>query_simics_knowledge_graph.py"]
end
P --> N
S --> N
D --> S
T --> S
A --> V
H --> V
V --> N
Q --> N
QS --> N
```

**Diagram sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L1-L120)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L1-L120)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L1-L120)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py#L1-L120)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L1-L120)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py#L1-L120)
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L1-L120)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L1-L120)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L1-L120)

## Detailed Component Analysis

### Neo4j Schema Design
Nodes and relationships are designed to reflect code structure and Simics specifics.

```mermaid
erDiagram
REPOSITORY {
string name PK
datetime created_at
}
FILE {
string path PK
string name
string module_name
int line_count
string file_type
}
CLASS {
string full_name PK
string name
datetime created_at
}
METHOD {
string method_id PK
string name
string full_name
list args
list params_list
list params_detailed
string return_type
datetime created_at
}
ATTRIBUTE {
string attr_id PK
string name
string full_name
string type
datetime created_at
}
FUNCTION {
string func_id PK
string name
string full_name
list args
list params_list
list params_detailed
string return_type
datetime created_at
}
IMPORT {
string source_path
string target_path
}
REPOSITORY ||--o{ FILE : "CONTAINS"
FILE ||--o{ CLASS : "DEFINES"
FILE ||--o{ FUNCTION : "DEFINES"
CLASS ||--o{ METHOD : "HAS_METHOD"
CLASS ||--o{ ATTRIBUTE : "HAS_ATTRIBUTE"
FILE ||--o{ IMPORT : "IMPORTS"
```

Notes:
- Unique constraints and indexes are created for performance and integrity.
- Python-specific nodes include File, Class, Method, Attribute, Function.
- Simics-specific additions include DMLFile, DMLDevice, DMLInterface, DMLMethod, DMLAttribute, DMLRegister, TestFile, TestFunction, TestFixture, SimicsAPI, DeviceUnderTest, and relationships like INHERITS_FROM, DEFINES, IMPLEMENTS, HAS_METHOD, HAS_ATTRIBUTE, HAS_REGISTER, TESTS, USES_API.

**Diagram sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L420-L470)
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L612-L783)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L182-L224)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L311-L468)

**Section sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L420-L470)
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L612-L783)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L182-L224)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L311-L468)

### Parsing Workflow: Python Repository
The repository analyzer performs:
- Cloning and scanning for Python files
- First pass to discover project modules
- Second pass to analyze files via AST
- Graph creation with MERGE semantics to avoid duplicates
- Import relationship creation based on module matching

```mermaid
sequenceDiagram
participant Repo as "Repository"
participant Extractor as "DirectNeo4jExtractor"
participant Analyzer as "Neo4jCodeAnalyzer"
participant DB as "Neo4j"
Repo->>Extractor : analyze_repository(repo_url)
Extractor->>Extractor : clear_repository_data(repo_name)
Extractor->>Extractor : clone_repo(repo_url, temp_dir)
Extractor->>Extractor : get_python_files(repo_path)
Extractor->>Analyzer : analyze_python_file(file, repo_root, project_modules)
Analyzer-->>Extractor : analysis result
Extractor->>DB : create Repository node
loop for each module_data
Extractor->>DB : create File node
Extractor->>DB : create Class nodes and MERGE relationships
Extractor->>DB : create Method nodes and MERGE relationships
Extractor->>DB : create Attribute nodes and MERGE relationships
Extractor->>DB : create Function nodes and MERGE relationships
Extractor->>DB : create Import relationships
end
Extractor-->>Repo : summary and completion
```

**Diagram sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L529-L611)
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L612-L783)

**Section sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L529-L611)
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L612-L783)

### Parsing Workflow: Simics DML and Tests
The Simics extractor:
- Discovers DML, test, and Python files locally
- Sets up Simics-specific constraints and indexes
- Parses DML and test files, then creates nodes and relationships
- Links tests to DML devices and other Simics constructs

```mermaid
sequenceDiagram
participant Dir as "Local Directory"
participant Ext as "SimicsNeo4jExtractor"
participant DML as "DMLParser"
participant TA as "SimicsTestAnalyzer"
participant DB as "Neo4j"
Dir->>Ext : analyze_local_directory(path, filters)
Ext->>Ext : _discover_simics_files(...)
Ext->>DB : _setup_simics_schema()
alt DML-only
Ext->>DML : parse_dml_file(file, base_path)
DML-->>Ext : analysis
Ext->>DB : _create_dml_nodes(analysis)
else Tests-only
Ext->>TA : analyze_test_file(file, base_path, project_modules)
TA-->>Ext : analysis
Ext->>DB : _create_test_nodes(analysis)
else Python-only
Ext->>Ext : _analyze_python_files(...)
Ext->>DB : _create_python_nodes(analysis)
end
Ext->>DB : _create_simics_relationships(...)
```

**Diagram sources**
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L54-L121)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L182-L224)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L225-L310)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L311-L468)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L469-L563)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L120-L179)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py#L90-L159)

**Section sources**
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L54-L121)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L182-L224)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L225-L310)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L311-L468)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L469-L563)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L120-L179)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py#L90-L159)

### DML Parsing Model
DML parsing extracts devices, interfaces, methods, attributes, registers, and links them to devices.

```mermaid
classDiagram
class DMLDevice {
+string name
+string parent
+string file_path
+int line_number
+string[] interfaces
+string[] methods
+string[] attributes
+string[] registers
}
class DMLInterface {
+string name
+string[] methods
+string file_path
+int line_number
}
class DMLMethod {
+string name
+string device
+string[] parameters
+string return_type
+string file_path
+int line_number
}
class DMLAttribute {
+string name
+string device
+string type_name
+string file_path
+int line_number
}
class DMLRegister {
+string name
+string device
+string address
+string size
+string file_path
+int line_number
}
class DMLParser {
+parse_dml_file(file_path, base_path) Dict
-_extract_devices(content, file_path) DMLDevice[]
-_extract_interfaces(content, file_path) DMLInterface[]
-_extract_methods(content, file_path) DMLMethod[]
-_extract_attributes(content, file_path) DMLAttribute[]
-_extract_registers(content, file_path) DMLRegister[]
-_link_elements_to_devices(devices, methods, attributes, registers, content) void
}
DMLParser --> DMLDevice : "creates"
DMLParser --> DMLInterface : "creates"
DMLParser --> DMLMethod : "creates"
DMLParser --> DMLAttribute : "creates"
DMLParser --> DMLRegister : "creates"
```

**Diagram sources**
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L19-L86)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L87-L179)

**Section sources**
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L19-L86)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L87-L179)

### AI Hallucination Detection Process
The detector orchestrates AST analysis, graph validation, and reporting.

```mermaid
sequenceDiagram
participant User as "User"
participant Detector as "AIHallucinationDetector"
participant Analyzer as "AIScriptAnalyzer"
participant Validator as "KnowledgeGraphValidator"
participant Reporter as "HallucinationReporter"
participant DB as "Neo4j"
User->>Detector : detect_hallucinations(script_path)
Detector->>Analyzer : analyze_script(script_path)
Analyzer-->>Detector : AnalysisResult
Detector->>Validator : validate_script(AnalysisResult)
Validator->>DB : query graph (modules, classes, methods, functions)
DB-->>Validator : results
Validator-->>Detector : ScriptValidationResult
Detector->>Reporter : generate_comprehensive_report(ScriptValidationResult)
Reporter-->>User : JSON/Markdown reports
```

**Diagram sources**
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L48-L126)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py#L93-L133)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L129-L164)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L642-L804)

**Section sources**
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L48-L126)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py#L93-L133)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L129-L164)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L642-L804)

### Query Interfaces
- General query tool explores repositories, classes, methods, and runs custom Cypher.
- Simics query tool provides domain-specific queries for device hierarchy, test coverage, API usage, fixtures, and statistics.

```mermaid
flowchart TD
Start(["Start"]) --> Choose["Choose Query Mode"]
Choose --> |General| Gen["query_knowledge_graph.py"]
Choose --> |Simics| Sims["query_simics_knowledge_graph.py"]
Gen --> ListRepos["List Repositories"]
Gen --> ExploreRepo["Explore Repository"]
Gen --> ListClasses["List Classes"]
Gen --> ExploreClass["Explore Class"]
Gen --> SearchMethod["Search Method"]
Gen --> Custom["Run Custom Cypher"]
Sims --> Predefs["Predefined Queries"]
Predefs --> DH["Device Hierarchy"]
Predefs --> DI["Device Interfaces"]
Predefs --> DM["Device Methods"]
Predefs --> DR["Device Registers"]
Predefs --> TC["Test Coverage"]
Predefs --> UT["Untested Devices"]
Predefs --> AU["API Usage"]
Predefs --> TP["Test Patterns"]
Predefs --> DD["Device Dependencies"]
Predefs --> CL["Cross-Language Links"]
Predefs --> SD["Similar Devices"]
Predefs --> TF["Test Fixtures"]
Predefs --> ST["Stats"]
DH --> End(["End"])
DI --> End
DM --> End
DR --> End
TC --> End
UT --> End
AU --> End
TP --> End
DD --> End
CL --> End
SD --> End
TF --> End
ST --> End
```

**Diagram sources**
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L39-L211)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L212-L294)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L30-L113)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L114-L245)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L246-L450)

**Section sources**
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L39-L211)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L212-L294)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L30-L113)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L114-L245)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L246-L450)

## Dependency Analysis
Key dependencies and relationships:
- parse_simics_into_neo4j.py imports and extends DirectNeo4jExtractor and Neo4jCodeAnalyzer from parse_repo_into_neo4j.py
- SimicsNeo4jExtractor composes DMLParser and SimicsTestAnalyzer
- KnowledgeGraphValidator depends on Neo4j for graph queries
- AIHallucinationDetector composes AIScriptAnalyzer, KnowledgeGraphValidator, and HallucinationReporter
- Query interfaces depend on KnowledgeGraphQuerier

```mermaid
graph TB
PRN["parse_repo_into_neo4j.py"]
PSN["parse_simics_into_neo4j.py"]
SDM["simics_dml_parser.py"]
STA["simics_test_analyzer.py"]
KGV["knowledge_graph_validator.py"]
ASA["ai_script_analyzer.py"]
AHD["ai_hallucination_detector.py"]
QKG["query_knowledge_graph.py"]
QSK["query_simics_knowledge_graph.py"]
PSN --> PRN
PSN --> SDM
PSN --> STA
KGV --> PRN
AHD --> ASA
AHD --> KGV
QSK --> QKG
```

**Diagram sources**
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L33-L53)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L1-L20)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py#L12-L21)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L1-L21)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py#L1-L20)
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L16-L30)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L1-L20)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L21-L33)

**Section sources**
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L33-L53)
- [simics_dml_parser.py](file://knowledge_graphs/simics_dml_parser.py#L1-L20)
- [simics_test_analyzer.py](file://knowledge_graphs/simics_test_analyzer.py#L12-L21)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L1-L21)
- [ai_script_analyzer.py](file://knowledge_graphs/ai_script_analyzer.py#L1-L20)
- [ai_hallucination_detector.py](file://knowledge_graphs/ai_hallucination_detector.py#L16-L30)
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L1-L20)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L21-L33)

## Performance Considerations
- Constraints and indexes:
  - Unique constraints for File.path and DML nodes
  - Indexes on File.name, Class.name, Method.name for efficient lookups
- MERGE semantics:
  - Used to avoid duplicate nodes and relationships during ingestion
- Caching:
  - KnowledgeGraphValidator caches module and class lookups to reduce repeated queries
- Filtering:
  - Excludes test files and large files to keep ingestion fast
- Asynchronous Neo4j driver:
  - Uses AsyncGraphDatabase for concurrent operations

**Section sources**
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L420-L470)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L182-L224)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L100-L115)

## Troubleshooting Guide
Common issues and resolutions:
- Neo4j connectivity:
  - Ensure NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD are configured
  - Verify Neo4j service is running and reachable
- Duplicate nodes:
  - MERGE is used to prevent duplicates; if duplicates appear, check uniqueness constraints and indexes
- Large files:
  - Files larger than a threshold are skipped; adjust thresholds if needed
- Import resolution:
  - External modules are treated as uncertain; confirm module names and repository matching logic
- Query timeouts:
  - Use LIMIT clauses and targeted queries; leverage indexes on frequently queried properties

**Section sources**
- [query_knowledge_graph.py](file://knowledge_graphs/query_knowledge_graph.py#L350-L399)
- [parse_repo_into_neo4j.py](file://knowledge_graphs/parse_repo_into_neo4j.py#L508-L528)
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L642-L804)

## Conclusion
The knowledge graph system provides a robust foundation for code and Simics DML analysis:
- Structured schema enables rich relationships between files, classes, methods, attributes, functions, and Simics constructs
- Automated ingestion pipelines populate the graph efficiently with constraints and indexes
- Validation against the graph detects AI hallucinations by checking imports, classes, methods, attributes, and functions
- Query interfaces offer both general exploration and Simics-specific insights for dependency analysis and cross-referencing

## Appendices

### Use Cases
- Code validation:
  - Validate imports, class instantiations, method calls, attribute accesses, and function calls against the graph
- Dependency analysis:
  - Analyze device inheritance, interface implementations, and relationships between DML devices and tests
- Cross-referencing:
  - Link Python tests to DML devices and Simics APIs to understand usage patterns

**Section sources**
- [knowledge_graph_validator.py](file://knowledge_graphs/knowledge_graph_validator.py#L129-L164)
- [query_simics_knowledge_graph.py](file://knowledge_graphs/query_simics_knowledge_graph.py#L70-L167)
- [parse_simics_into_neo4j.py](file://knowledge_graphs/parse_simics_into_neo4j.py#L564-L618)

### System-wide Flow Reference
For broader context on summarization and chunking flows in the repository, refer to the provided diagram.

**Section sources**
- [CODE_FLOW_DIAGRAM.md](file://CODE_FLOW_DIAGRAM.md#L1-L254)