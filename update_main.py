import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CORS
content = content.replace('allow_origins=["*"]', 'allow_origins=["http://localhost:3000"]')

# 2. Add auth and /login route right after CORS setup (around line 14)
auth_code = '''
from dotenv import load_dotenv
load_dotenv()

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.security import verify_token, create_access_token, Role
from pydantic import BaseModel

ADMIN_KEY = os.getenv("ADMIN_KEY")
if not ADMIN_KEY:
    raise RuntimeError("CRITICAL: ADMIN_KEY environment variable is not set. Refusing to start server.")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

class LoginRequest(BaseModel):
    api_key: str

@app.post("/login")
async def login(request: LoginRequest):
    if request.api_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    token = create_access_token(data={"sub": "admin"}, role=Role.ADMIN, tenant_id="local")
    return {"access_token": token, "token_type": "bearer"}
'''
content = content.replace('app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])', 
                          'app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])\n' + auth_code)

# 3. Add dependencies to all @app.post and @app.get (but not /login)
def add_deps(match):
    full_match = match.group(0)
    if '"/login"' in full_match:
        return full_match
    if 'dependencies=[' in full_match:
        return full_match
    
    # insert dependencies before closing paren of the decorator
    idx = full_match.rfind(')')
    if idx != -1:
        prefix = full_match[:idx]
        if prefix.endswith('('):
            new_full = prefix + 'dependencies=[Depends(get_current_user)])'
        else:
            new_full = prefix + ', dependencies=[Depends(get_current_user)])'
        return new_full
    return full_match

content = re.sub(r'@app\.(post|get)\([^\)]*\)', add_deps, content)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated backend/main.py")
