# DARKWIN-AATK: Memory Map

## System Overview
DARKWIN is a modular automation toolkit designed for offensive security reconnaissance and vulnerability scanning. It orchestrates a collection of third-party security tools into a unified pipeline.

## Architectural Map

```mermaid
graph TD
    User([User]) --> CLI[core/darkwin.py]
    CLI --> Config[core/config_loader.py]
    CLI --> Logger[core/logger.py]
    CLI --> Pipeline[core/pipeline.py]
    
    subgraph Core Logic
        Pipeline --> Engine[core/engine.py]
        Engine --> ToolLoader[core/tool_loader.py]
    end
    
    subgraph Module Layers
        Engine --> OSINT[modules/osint]
        Engine --> RECON[modules/recon]
        Engine --> CLOUD[modules/cloud]
        Engine --> WEB[modules/web]
        Engine --> VULN[modules/vulnerabilities]
    end
    
    Module Layers --> ThirdParty[External Binary Execution]
    ThirdParty --> Results[reports/TARGET/SESSION/*.txt]
```

## Component Breakdown

### 1. The Entry Point (`core/darkwin.py`)
- Uses `click` for the command-line interface.
- Commands: `run`, `doctor`, `update`.
- Handles session initialization and banner display.

### 2. Configuration (`core/config_loader.py` & `config.yaml`)
- Manages the environment.
- Stores API keys for services like GitHub, VirusTotal, and HIBP.
- Defines tool paths and logging directories.

### 3. Orchestration Engine (`core/engine.py`)
- The "Brain" of the system.
- Wraps `subprocess` calls to external tools.
- Handles output redirection and error logging.

### 4. Pipeline Controller (`core/pipeline.py`)
- Defines the logical sequence of operations for different modes:
    - **Recon**: DNS, Subdomains, ASN, Cloud discovery.
    - **Scan**: Port scanning, Service discovery, Web fuzzing.
    - **Bounty**: All the above + vulnerability specific modules.

### 5. Dependency Validator (`core/tool_loader.py`)
- Checks if tools like `nmap`, `subfinder`, `amass`, etc., are in the system `$PATH`.

## Data Flow
1. **Input**: User provides target domain and mode.
2. **Init**: Logger starts a new session; Config is loaded.
3. **Execution**: Pipeline triggers specific modules.
4. **Processing**: Engine executes external binaries and captures output.
5. **Storage**: Reports are saved in a structured format under `reports/`.
