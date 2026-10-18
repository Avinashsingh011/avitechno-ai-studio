"""AVI TECHNO AI Studio: Python 3.11+ WSGI application."""
import os, json, base64, hmac, mimetypes
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
from wsgiref.simple_server import make_server
ROOT=Path(__file__).resolve().parent
if (ROOT/'.env').exists():
    for line in (ROOT/'.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1);os.environ.setdefault(k.strip(),v.strip().strip('\"').strip("'"))
TOOLS={t['id']:t for t in json.loads((ROOT/'tools.json').read_text())}
def auth(e):
    u,p=os.getenv('STUDIO_USER',''),os.getenv('STUDIO_PASSWORD','')
    try:
        scheme,token=e.get('HTTP_AUTHORIZATION','').split(' ',1)
        return bool(u and p) and scheme.lower()=='basic' and hmac.compare_digest(base64.b64decode(token,validate=True),(u+':'+p).encode())
    except (ValueError,UnicodeError):return False

def application(e,start):
    def reply(d,code=200,mime='application/json',extra=()):
        data=json.dumps(d).encode() if mime=='application/json' else d
        reason={200:'OK',400:'Bad Request',401:'Unauthorized',403:'Forbidden',404:'Not Found',405:'Method Not Allowed',413:'Content Too Large',502:'Bad Gateway',503:'Service Unavailable'}[code]
        start(f'{code} {reason}',[('Content-Type',mime),('Content-Length',str(len(data))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),('Referrer-Policy','no-referrer'),*extra]);return [data]
    path=e.get('PATH_INFO','/');method=e.get('REQUEST_METHOD','GET')
    if os.getenv('STUDIO_USER') and os.getenv('STUDIO_PASSWORD') and not auth(e):return reply({'error':'Sign in to AI Studio'},401,extra=[('WWW-Authenticate','Basic realm="AVI TECHNO"')])
    if path=='/healthz':return reply({'status':'ok'})
    if path=='/api/status':return reply({'ready':all(os.getenv(k) for k in ['OPENAI_API_KEY','OPENAI_TEXT_MODEL','OPENAI_IMAGE_MODEL','STUDIO_USER','STUDIO_PASSWORD'])})
    if path=='/api/generate':
        if method!='POST':return reply({'error':'Method not allowed'},405)
        if e.get('HTTP_ORIGIN')!=os.getenv('STUDIO_ORIGIN','http://localhost:8000').rstrip('/'):return reply({'error':'Origin mismatch. Set STUDIO_ORIGIN to your exact browser URL.'},403)
        if not auth(e):return reply({'error':'Configure STUDIO_USER and STUDIO_PASSWORD before using AI.'},503)
        if not os.getenv('OPENAI_API_KEY'):return reply({'error':'Set OPENAI_API_KEY in server .env. Prompt building works without a key.'},503)
        try:
            length=int(e.get('CONTENT_LENGTH') or 0)
            if not 0<length<=160000:return reply({'error':'Invalid request size'},413)
            b=json.loads(e['wsgi.input'].read(length));t=TOOLS.get(b.get('tool'));prompt=b.get('prompt')
            if not t or not isinstance(prompt,str) or not prompt.strip() or len(prompt)>60000:raise ValueError()
        except (ValueError,TypeError,AttributeError):return reply({'error':'Invalid tool or brief'},400)
        image=t['kind']=='image';model=os.getenv('OPENAI_IMAGE_MODEL' if image else 'OPENAI_TEXT_MODEL')
        if not model:return reply({'error':'Configure the selected AI model in .env.'},503)
        payload={'model':model,'prompt':t['instruction']+'\n'+prompt,'n':1,'size':'1024x1024'} if image else {'model':model,'instructions':t['instruction'],'input':prompt,'store':False,'max_output_tokens':2200}
        req=Request('https://api.openai.com/v1/'+('images/generations' if image else 'responses'),json.dumps(payload).encode(),headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'],'Content-Type':'application/json'})
        try:
            with urlopen(req,timeout=90) as response:d=json.load(response)
            if image:
                value=d.get('data',[{}])[0].get('b64_json')
                if value:return reply({'image':value})
            else:
                text='\n'.join(c['text'] for item in d.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text')
                if text:return reply({'text':text})
            return reply({'error':'No supported output returned.'},502)
        except (URLError,TimeoutError,ValueError,KeyError,IndexError):return reply({'error':'AI request failed. Check model configuration, API access and account limits.'},502)
    if method not in ('GET','HEAD'):return reply({'error':'Method not allowed'},405)
    target=(ROOT/'web'/('index.html' if path=='/' else path.lstrip('/'))).resolve()
    if not target.is_relative_to((ROOT/'web').resolve()) or not target.is_file():return reply({'error':'Not found'},404)
    return reply(target.read_bytes(),mime=mimetypes.guess_type(target.name)[0] or 'application/octet-stream')
if __name__=='__main__':
    print('AVI TECHNO AI Studio: http://localhost:8000')
    with make_server('127.0.0.1',8000,application) as server:server.serve_forever()
