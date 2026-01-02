Readme file:

✔ Prerequisites
✔ Installation
✔ Folder structure
✔ How to configure
✔ How to run
✔ Logging details
✔ Troubleshooting
✔ Optional enhancements

---

# 📘 **Tomcat Log Analyzer

A Linux CLI-based Tomcat log analyzer that:

* Extracts errors from `catalina.out`
* Streams analysis from a **remote Ollama AI server**
* Logs errors + timings
* Stores performance metrics separately
* Uses a clean YAML-based configuration

This project is built for DevOps, SRE, and Platform Engineering teams who need a fast, automated root-cause analysis (RCA) workflow.

---

# 🧩 **1. Prerequisites**

## ✔ 1.1 Python Requirements (on VM-1)

Install:

* Python 3.8+
* pip

Verify Python:
python3 --version


Install required libraries:
pip install requests pyyaml

---

## ✔ 1.2 Remote Ollama Setup (VM-2)

On your **Ollama VM**:

1. Install Ollama:

   
   curl -fsSL https://ollama.com/install.sh | sh
   

2. Start Ollama server with remote access enabled:


3. Pull your model:

   
   ollama pull mistral
   

   *(or any model you want)*

4. Verify API:

   
   curl http://<OLLAMA_VM_IP>:11434/api/tags
   

You should get a JSON response with model names.

#By default ollama server is accessible from 127.0.0.1(localhost). To make it accessible from anywhere make following changes.
Replace following line 
	Environment="PATH=/home/aunsh/.local/bin:/home/aunsh/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin"
with 
	Environment="OLLAMA_HOST=0.0.0.0:11434"	
	
# Apply the changes
	sudo systemctl daemon-reload
	sudo systemctl restart ollama

---

## ✔ 1.3 Ensure VM-1 Can Reach VM-2

From VM-1:


curl http://<OLLAMA_VM_IP>:11434/api/tags


If no response:

* Check firewall
* Check security groups
* Check IP reachability

---

# 📁 **2. Folder Structure**


tomcat-analyzer/
│
├── main.py
├── ai_analyzer.py
├── log_parser.py
├── config.yaml
│
└── logs/
    ├── analyzer.log
    └── performance.log


You must create this directory structure on **VM-1**.

---

# ⚙️ **3. Installation Steps**

### Step 1 — Create project directory


mkdir tomcat-analyzer
cd tomcat-analyzer


### Step 2 — Copy project files

Place:

* `main.py`
* `ai_analyzer.py`
* `log_parser.py`
* `config.yaml`

Create logs directory:


mkdir logs


### Step 3 — Make main.py executable (optional)


chmod +x main.py


Project is now ready.

---

# 📘 **4. Configuration — config.yaml**

Example:

yaml
ollama_host: "http://<ollama_host>:11434"
model: "mistral"

log_dir: "./logs"
log_file: "analyzer.log"
log_level: "INFO"

max_error_lines: 300


### Change the following:

| Field             | Meaning                                  |
| ----------------- | ---------------------------------------- |
| `ollama_host`     | IP + port of your remote Ollama server   |
| `model`           | Model to use (`mistral`, `llama3`, etc.) |
| `log_dir`         | Where logs are stored                    |
| `max_error_lines` | Max lines to capture per error block     |

---

# 🚀 **5. How to Run the Analyzer**

Basic usage:


python3 main.py /path/to/catalina.out


Specify custom config:


python3 main.py /var/log/tomcat/catalina.out -c config.yaml


### What happens when you run it:

1. Log file is loaded
2. Error blocks are extracted
3. Remote Ollama connection is established
4. AI output is streamed live into terminal
5. All timings go to `performance.log`
6. All operational logs go to `analyzer.log`

---

# 📄 **6. Output Example**

Terminal output:


🔍 Extracted Error Log Preview:

SEVERE: Servlet exception...
java.lang.NullPointerException
...

🤖 Analyzing with remote Ollama (streaming)...

Analyzing Tomcat logs...
Root cause appears to be a DB connection leak...

⏱️ Total analysis time: 3.42 seconds
✅ Streaming complete.


🧠 Final Summary:
The issue is caused by...


---

# 📊 **7. Logging Details**

## ✔ analyzer.log (main logs)

Contains:

* Errors during API calls
* Info messages
* Parsing issues
* Stack traces

Location:


logs/analyzer.log


## ✔ performance.log (timing metrics)

Contains:

* Time to load log file
* Time to parse log
* Time to connect to Ollama
* Time to stream response
* Total analysis time

Location:


logs/performance.log


Example:


2025-11-20 13:10:22 - Time to load log file: 0.0043 sec
2025-11-20 13:10:22 - Time to parse log: 0.0321 sec
2025-11-20 13:10:23 - Time to connect to Ollama: 0.4122 sec
2025-11-20 13:10:27 - Time to stream response: 3.8519 sec
2025-11-20 13:10:27 - Total analysis time: 4.2641 sec


---

# 🛠 **8. Troubleshooting**

### ❌ **Ollama API error**

Check:


curl http://<OLLAMA_VM_IP>:11434/api/tags


### ❌ "Connection timed out"

Fix:

* Firewall on VM2
* Ollama not running
* Wrong IP in config.yaml

### ❌ "No relevant errors found"

Your log does not contain:

* SEVERE
* Exception
* ERROR
* Caused by

Modify regex in `log_parser.py` if needed.

---

