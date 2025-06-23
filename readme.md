
## Local Setup
### Create & Activate Virtual Environment

#### 1. Create a virtual environment:

```bash
python3 -m venv venv
```

This will create a folder named `venv/` containing the virtual environment.

#### 2. Activate the virtual environment:

* On **macOS/Linux**:

  ```bash
  source venv/bin/activate
  ```

* On **Windows (CMD)**:

  ```cmd
  venv\Scripts\activate.bat
  ```

* On **Windows (PowerShell)**:

  ```powershell
  venv\Scripts\Activate.ps1
  ```

#### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Create ELK Cluster
```shell
python main.py
```
## Destroy Cluster
```shell
terrafrom destroy
```
