import os, tempfile
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["ML_MODE"] = "off"
from fastapi.testclient import TestClient
from app.main import app

DEMO = {"email": "demo@astravault.test", "password": "OrbitReady!2026"}

def client(): return TestClient(app)
def auth(c):
    r=c.post('/api/auth/login',json=DEMO)
    assert r.status_code==200,r.text
    return {"Authorization":f"Bearer {r.json()['access_token']}"}

def test_dataset_import_and_health():
    with client() as c:
        h=c.get('/health').json()
        assert h['status']=='ok' and h['dataset_loaded'] is True
        assert h['dataset_observations']==3600

def test_auth_and_protected_routes():
    with client() as c:
        assert c.get('/api/dataset/dashboard').status_code==401
        headers=auth(c)
        assert c.get('/api/dataset/dashboard',headers=headers).status_code==200

def test_dashboard_reflects_real_dataset():
    with client() as c:
        d=c.get('/api/dataset/dashboard',headers=auth(c)).json()
        assert d['metrics']['crew_count']==20
        assert d['metrics']['total_observations']==3600
        assert d['metrics']['hazard_count']==5 and d['metrics']['risk_count']==17
        assert d['metrics']['dataset_columns']==147
        assert d['dataset']['mission_phases']==['Cruise','Outbound','Return']
        assert d['crew'][0]['crew_code']=='AST001'

def test_astronaut_longitudinal_detail():
    with client() as c:
        detail=c.get('/api/dataset/astronauts/AST001',headers=auth(c)).json()
        assert detail['profile']['observation_count']==180
        assert detail['history'][0]['mission_day']==1
        assert detail['history'][-1]['mission_day']==180
        assert 'radiation_cancer_exposure_category' in detail['latest']
        assert detail['latest']['astronaut_id']=='AST001'

def test_catalogue_has_five_hazards_and_seventeen_risks():
    with client() as c:
        d=c.get('/api/dataset/catalogue',headers=auth(c)).json()
        assert len(d['hazards'])==5 and len(d['risks'])==17
        assert all(x['crew_count']==20 for x in d['hazards'])

def test_unknown_astronaut_and_csv_export():
    with client() as c:
        h=auth(c)
        assert c.get('/api/dataset/astronauts/AST999',headers=h).status_code==404
        r=c.get('/api/dataset/export.csv',headers=h)
        assert r.status_code==200 and 'text/csv' in r.headers['content-type']
        assert 'astronaut_health_integrated.csv' in r.headers.get('content-disposition','') and r.text.startswith('astronaut_id,mission_id')

def test_register_duplicate_and_bad_password():
    with client() as c:
        assert c.post('/api/auth/login',json={**DEMO,'password':'wrong'}).status_code==401
        body={"email":"new.user@example.com","password":"LongEnoughPass1","full_name":"New User"}
        assert c.post('/api/auth/register',json=body).status_code==201
        assert c.post('/api/auth/register',json=body).status_code==409

def test_ml_model_status_template_prediction_and_history():
    with client() as c:
        headers = auth(c)
        status = c.get('/api/ml/status', headers=headers)
        assert status.status_code == 200, status.text
        assert status.json()['available'] is True
        assert status.json()['domains'] == 17
        template = c.get('/api/ml/template/AST001', headers=headers)
        assert template.status_code == 200, template.text
        features = template.json()['features']
        assert len(features) == 82
        assert features['mission_day'] == 180
        prediction = c.post('/api/ml/predict', headers=headers,
                            json={'crew_code':'AST001','features':features})
        assert prediction.status_code == 201, prediction.text
        result = prediction.json()
        assert result['prediction_id'] > 0
        assert result['triage_status'] in ('GREEN','AMBER','RED')
        assert len(result['domain_predictions']) == 17
        for domain in result['domain_predictions'].values():
            assert domain['label'] in ('LOW','MODERATE','HIGH')
            assert abs(domain['prob_low'] + domain['prob_moderate'] + domain['prob_high'] - 1) < 1e-5
        history = c.get('/api/ml/history/AST001', headers=headers)
        assert history.status_code == 200 and len(history.json()) == 1
        assert history.json()[0]['id'] == result['prediction_id']


def test_ml_rejects_missing_features():
    with client() as c:
        headers = auth(c)
        r = c.post('/api/ml/predict', headers=headers, json={'crew_code':'AST001','features':{'mission_day':1,'mission_phase':'Cruise'}})
        assert r.status_code == 422
