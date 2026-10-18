import unittest,os,io,json,base64
from unittest.mock import patch
from app import application
class Tests(unittest.TestCase):
 def call(self,path='/',method='GET',body=None,headers=None):
  data=json.dumps(body).encode() if body else b'';r={}
  e={'PATH_INFO':path,'REQUEST_METHOD':method,'CONTENT_LENGTH':str(len(data)),'wsgi.input':io.BytesIO(data),**(headers or {})}
  def start(s,h):r.update(code=int(s.split()[0]),headers=dict(h))
  r['body']=b''.join(application(e,start));return r
 @patch.dict(os.environ,{},clear=True)
 def test_dashboard(self):
  self.assertIn(b'AVI TECHNO tiger logo',self.call()['body'])
  for path in ['/favicon.png','/brand/logo.webp','/brand/background.webp']:self.assertEqual(self.call(path)['code'],200)
  self.assertFalse(json.loads(self.call('/api/status')['body'])['ready'])
  self.assertEqual(self.call('/../../app.py')['code'],404)
 @patch.dict(os.environ,{'STUDIO_USER':'avi','STUDIO_PASSWORD':'test-only'},clear=True)
 def test_access(self):
  self.assertEqual(self.call()['code'],401)
  h={'HTTP_AUTHORIZATION':'Basic '+base64.b64encode(b'avi:test-only').decode()}
  self.assertEqual(self.call(headers=h)['code'],200)
  self.assertEqual(self.call('/api/generate','POST',headers=h)['code'],403)
  h['HTTP_ORIGIN']='http://localhost:8000';self.assertEqual(self.call('/api/generate','POST',headers=h)['code'],503)
 @patch.dict(os.environ,{'STUDIO_USER':'avi','STUDIO_PASSWORD':'test-only','OPENAI_API_KEY':'mock-only','OPENAI_TEXT_MODEL':'mock'},clear=True)
 def test_generation(self):
  h={'HTTP_AUTHORIZATION':'Basic '+base64.b64encode(b'avi:test-only').decode(),'HTTP_ORIGIN':'http://localhost:8000'}
  self.assertEqual(self.call('/api/generate','POST',{'tool':'unknown','prompt':'hi'},h)['code'],400)
  response=io.BytesIO(json.dumps({'output':[{'content':[{'type':'output_text','text':'Mock result'}]}]}).encode())
  with patch('app.urlopen',return_value=response):r=self.call('/api/generate','POST',{'tool':'helpdesk','prompt':'DNS error'},h)
  self.assertEqual(json.loads(r['body']),{'text':'Mock result'})
