import urllib.request
import urllib.error
import urllib.parse
import json
import os

class AuthState:
    AUTHENTICATED = "AUTHENTICATED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    AUTH_FAILED = "AUTH_FAILED"

class AuthError(Exception):
    """Base class for authentication errors."""
    def __init__(self, message="Authentication error", state=AuthState.AUTH_FAILED):
        super().__init__(message)
        self.state = state

class AuthRequiredError(AuthError):
    """Raised when an authenticated request is attempted without an active token."""
    def __init__(self, message="Authentication Required: Please login to Qyntara Nexus Core."):
        super().__init__(message, state=AuthState.AUTH_REQUIRED)

class AuthExpiredError(AuthError):
    """Raised when the API returns a 401 Unauthorized or token is invalid/expired."""
    def __init__(self, message="Session Expired: Please re-authenticate."):
        super().__init__(message, state=AuthState.AUTH_EXPIRED)

class AuthFailedError(AuthError):
    """Raised when authentication credentials fail."""
    def __init__(self, message="Authentication Failed: Invalid API key or credentials."):
        super().__init__(message, state=AuthState.AUTH_FAILED)

class APIConnectionError(Exception):
    """Raised when the API cannot be reached."""
    pass

class NexusAPIClient:
    """
    Centralized HTTP client for Qyntara Nexus.
    Responsible for all network transport, authentication, 
    and error normalization.
    """
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.token = None

    def get_auth_state(self):
        """Returns the explicit AuthState enumeration."""
        if self.token:
            return AuthState.AUTHENTICATED
        return AuthState.AUTH_REQUIRED

    def is_authenticated(self):
        """Returns True if a valid token is present."""
        return bool(self.token)
        
    def _request(self, endpoint, data=None, headers=None, timeout=30, method=None, requires_auth=True):
        """
        Base HTTP request engine.
        Returns a tuple of (response_bytes, status_code).
        """
        if headers is None:
            headers = {}
            
        # Check authentication state if required (endpoints other than /login)
        if endpoint != "/login" and requires_auth and not self.token:
            raise AuthRequiredError("Authentication Required: No active session token. Please log in.")

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}{endpoint}"
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read(), response.status
                
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise AuthExpiredError("Session Expired: Please re-authenticate.")
            # For Phase 1B we propagate other HTTPErrors naturally, or could raise specific exceptions.
            raise e
        except (urllib.error.URLError, ConnectionError) as e:
            raise APIConnectionError(f"Could not connect to QYNTARA Core: {e}")

    def request_json(self, endpoint, headers=None, timeout=30, method="GET", data=None):
        if headers is None:
            headers = {}
        # Ensure we ask for JSON if we are decoding JSON
        if "Accept" not in headers:
            headers["Accept"] = "application/json"
            
        body, status = self._request(endpoint, data=data, headers=headers, timeout=timeout, method=method)
        if body:
            return json.loads(body.decode('utf-8')), status
        return None, status

    def post_json(self, endpoint, payload, headers=None, timeout=30):
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"
        
        data = json.dumps(payload).encode('utf-8')
        return self.request_json(endpoint, headers=headers, timeout=timeout, method="POST", data=data)

    def login(self, api_key):
        """Authenticates with the backend and stores the access token."""
        data_bytes = json.dumps({"api_key": api_key}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        
        body, status = self._request("/login", data=data_bytes, headers=headers, timeout=5, method="POST")
        if status == 200:
            res = json.loads(body.decode('utf-8'))
            self.token = res.get("access_token")
            return True
        return False

    def download_file(self, url_or_path, local_path, fallback_url=None):
        url = url_or_path if url_or_path.startswith("http") else f"{self.base_url}{url_or_path}"
        req = urllib.request.Request(url)
        
        try:
            with urllib.request.urlopen(req) as response:
                with open(local_path, "wb") as f:
                    f.write(response.read())
            return True
        except urllib.error.HTTPError as e:
            if fallback_url:
                fallback_req = urllib.request.Request(fallback_url)
                try:
                    with urllib.request.urlopen(fallback_req) as response:
                        with open(local_path, "wb") as f:
                            f.write(response.read())
                    return True
                except Exception:
                    raise e
            raise e
            
    def upload_multipart(self, endpoint, file_path):
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        data = []
        data.append(f'--{boundary}')
        data.append(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"')
        data.append('Content-Type: application/octet-stream')
        data.append('')
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        body = b'\r\n'.join([x.encode('utf-8') for x in data])
        body += b'\r\n' + file_content + b'\r\n'
        body += f'--{boundary}--\r\n'.encode('utf-8')
        
        headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
        
        resp_body, status = self._request(endpoint, data=body, headers=headers, method="POST")
        if status == 200:
            result = json.loads(resp_body.decode('utf-8'))
            return result.get("path")
        return None

    def predict_risk(self, polycount, has_ngons):
        payload = {
            "polycount": polycount,
            "has_ngons": has_ngons
        }
        data, status = self.post_json("/ai/predict", payload)
        if status == 200 and data:
            return data.get("risk_score", 0.0), data.get("prediction", "Unknown"), data.get("reasons", "")
        return 0.0, "Unknown", ""

    def generate_seam_uv(self, mesh_path):
        payload = {"mesh_path": mesh_path}
        data, status = self.post_json("/ai/seam-gpt", payload)
        if status == 200 and data:
            return data.get("cut_edges", [])
        return []

    def fetch_stats(self, timeout=0.5):
        data, status = self.request_json("/stats", timeout=timeout)
        if status == 200:
            return data
        return None

    def simulate_industry(self, industry_key, payload):
        """Characterization: Uses the correct base_url."""
        url = "/validate/core"
        data, status = self.post_json(url, {"industry": industry_key, "metadata": payload}, timeout=3)
        return data, status
