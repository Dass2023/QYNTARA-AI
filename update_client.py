import re

with open('maya/qyntara_client.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove ACCESS_CODE
content = content.replace('ACCESS_CODE = "QYNTARA-X-777"\n', '')

# 2. Insert helper methods and replace login()
login_old = '''    def login(self):
        code = self.auth_input.text()
        if code == ACCESS_CODE:
            try:
                with urllib.request.urlopen(f"{API_URL}/stats", timeout=30) as response:
                    if response.status == 200:
                        self.token = "VALID"
                        self.set_status("NEURAL LINK ESTABLISHED", "success")
                        self.auth_group.hide()
                        self.controls_group.show()
                    else:
                        self.set_status("SERVER ERROR", "error")
            except Exception as e:
                self.set_status("CONNECTION FAILED", "error")
                self.show_message("Connection Failed", f"Could not connect to QYNTARA Core.\\nError: {e}\\nEnsure backend is running on port 8000.", "error")
        else:
            self.set_status("ACCESS DENIED", "error")'''

login_new = '''    def _handle_session_expired(self):
        self.controls_group.hide()
        self.auth_group.show()
        self.set_status("SESSION EXPIRED. PLEASE RE-LOGIN.", "error")
        self.token = None

    def _authed_request(self, url, data=None, headers=None, timeout=30):
        if headers is None: headers = {}
        if hasattr(self, 'token') and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read(), response.status
        except urllib.error.HTTPError as e:
            if e.code == 401:
                self._handle_session_expired()
            raise e

    def login(self):
        api_key = self.auth_input.text()
        try:
            import json
            data_bytes = json.dumps({"api_key": api_key}).encode("utf-8")
            resp_body, status = self._authed_request(f"{API_URL}/login", data=data_bytes, headers={"Content-Type": "application/json"}, timeout=5)
            if status == 200:
                data = json.loads(resp_body.decode())
                self.token = data.get("access_token")
                self.set_status("NEURAL LINK ESTABLISHED", "success")
                self.auth_group.hide()
                self.controls_group.show()
        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.set_status("ACCESS DENIED", "error")
            else:
                self.set_status("SERVER ERROR", "error")
        except Exception as e:
            self.set_status("CONNECTION FAILED", "error")
            self.show_message("Connection Failed", f"Could not connect to QYNTARA Core.\\nError: {e}\\nEnsure backend is running on port 8000.", "error")'''

if login_old in content:
    content = content.replace(login_old, login_new)
else:
    print("Could not find login_old")

# 3. Replace seam-gpt
old_seam = '''                req = urllib.request.Request(f"{API_URL}/ai/seam-gpt")
                req.add_header("Content-Type", "application/json")
                with urllib.request.urlopen(req, data=data) as response:
                    res_data = json.loads(response.read().decode())'''
new_seam = '''                resp_body, status = self._authed_request(f"{API_URL}/ai/seam-gpt", data=data, headers={"Content-Type": "application/json"})
                res_data = json.loads(resp_body.decode())'''
content = content.replace(old_seam, new_seam)

# 4. Replace execute
old_exec = '''            req = urllib.request.Request(f"{API_URL}/execute")
            req.add_header("Content-Type", "application/json")
            
            # Use a longer timeout for pipeline jobs
            with urllib.request.urlopen(req, jsondata, timeout=300) as response:
                result = json.loads(response.read().decode())'''
new_exec = '''            resp_body, status = self._authed_request(f"{API_URL}/execute", data=jsondata, headers={"Content-Type": "application/json"}, timeout=300)
            result = json.loads(resp_body.decode())'''
content = content.replace(old_exec, new_exec)

# 5. Replace upload
old_up = '''            req = urllib.request.Request(url, data=body)
            req.add_header('Content-type', f'multipart/form-data; boundary={boundary}')
            
            with urllib.request.urlopen(req) as response:
                resp_data = json.loads(response.read().decode())'''
new_up = '''            resp_body, status = self._authed_request(url, data=body, headers={'Content-type': f'multipart/form-data; boundary={boundary}'})
            resp_data = json.loads(resp_body.decode())'''
content = content.replace(old_up, new_up)

# 6. Replace ai/predict
old_pred = '''            req = urllib.request.Request(f"{API_URL}/ai/predict")
            req.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(req, data=data_bytes) as response:
                result = json.loads(response.read().decode())'''
new_pred = '''            resp_body, status = self._authed_request(f"{API_URL}/ai/predict", data=data_bytes, headers={"Content-Type": "application/json"})
            result = json.loads(resp_body.decode())'''
content = content.replace(old_pred, new_pred)

# 7. Replace stats 1 (open_stats)
old_stats1 = '''            with urllib.request.urlopen(f"{API_URL}/stats", timeout=2) as response:
                data = json.loads(response.read().decode())'''
new_stats1 = '''            resp_body, status = self._authed_request(f"{API_URL}/stats", timeout=2)
            data = json.loads(resp_body.decode())'''
content = content.replace(old_stats1, new_stats1)

# 8. Replace stats 2 (check_connection)
old_stats2 = '''            with urllib.request.urlopen(f"{API_URL}/stats", timeout=0.5) as response:
                if response.status == 200:'''
new_stats2 = '''            resp_body, status = self._authed_request(f"{API_URL}/stats", timeout=0.5)
            if status == 200:'''
content = content.replace(old_stats2, new_stats2)

# 9. Replace library
old_lib = '''            with urllib.request.urlopen(f"{API_URL}/library") as response:
                data = json.loads(response.read().decode())'''
new_lib = '''            resp_body, status = self._authed_request(f"{API_URL}/library")
            data = json.loads(resp_body.decode())'''
content = content.replace(old_lib, new_lib)


with open('maya/qyntara_client.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated maya/qyntara_client.py")
