"""Independent contract and scope tests, never remote integration evidence."""
import copy
import unittest
from athis_autopilot.n8n_qa import QAContract, validate_blueprint, sdk_code, check_cases, verify_remote, expression


def contract_fixture():
    return QAContract(workflow_name='PELLO-3B-QA-unit-fixture',webhook_path='pello-3b-unit-fixture',
        request_id_prefix='pello-3b-',operation='double',value_min=-1000000,value_max=1000000,
        success_http_status=200,invalid_http_status=400)


def blueprint_fixture():
    expression="={{ typeof $json.body.request_id === 'string' && $json.body.request_id.startsWith('pello-3b-') && $json.body.op === 'double' && typeof $json.body.value === 'number' && Number.isFinite($json.body.value) && $json.body.value >= -1000000 && $json.body.value <= 1000000 ? {request_id:$json.body.request_id,status:'ok',result:$json.body.value*2} : {request_id:typeof $json.body.request_id === 'string' ? $json.body.request_id : null,status:'invalid',error:'invalid_input'} }}"
    return {'nodes':[
        {'name':'QA Webhook','type':'n8n-nodes-base.webhook','version':2.2,
         'parameters':{'httpMethod':'POST','path':'pello-3b-unit-fixture','responseMode':'responseNode','authentication':'none','options':{}}},
        {'name':'QA Result','type':'n8n-nodes-base.set','version':3.5,
         'parameters':{'mode':'raw','jsonOutput':expression,'options':{}}},
        {'name':'QA Response','type':'n8n-nodes-base.respondToWebhook','version':1.5,
         'parameters':{'respondWith':'json','responseBody':'={{ $json }}','options':{'responseCode':"={{ $json.status === 'ok' ? 200 : 400 }}"}}}]}


class QAScopeTests(unittest.TestCase):
    def test_constructor_destructuring_assignments_and_comma_escape_are_rejected_before_evaluation(self):
        for source in ("({'constructor':body}=Number),body('return process')()",
                       '$json.body.value=42','($json.body.value++,42)',
                       "$json.body.request_id['constructor']",'Number.constructor',
                       "({request_id:'x'},$json)"):
            with self.subTest(source=source):
                with self.assertRaises(ValueError): expression('={{ '+source+' }}')

    def test_current_contract_expressions_pass_all_cases(self):
        data=blueprint_fixture(); contract=contract_fixture()
        validate_blueprint(data,contract)
        cases=check_cases(data,contract)
        self.assertGreaterEqual(len(cases),7)
        self.assertTrue(all(c['passed'] for c in cases))
        code=sdk_code(data,contract)
        self.assertIn("@n8n/workflow-sdk",code); self.assertIn('export default workflow(',code)
        self.assertNotIn('newCredential',code)

    def test_wrong_math_is_a_real_deterministic_failure(self):
        data=blueprint_fixture(); data['nodes'][1]['parameters']['jsonOutput']=data['nodes'][1]['parameters']['jsonOutput'].replace('value*2','value*3')
        cases=check_cases(data,contract_fixture())
        self.assertFalse(all(c['passed'] for c in cases))

    def test_unsafe_nodes_credentials_expressions_and_routes_rejected(self):
        mutations=[lambda d:d['nodes'][1].update(type='n8n-nodes-base.httpRequest'),
                   lambda d:d['nodes'][0].update(credentials={'httpBasicAuth':{'id':'foreign'}}),
                   lambda d:d['nodes'][0]['parameters'].update(path='customer-endpoint'),
                   lambda d:d['nodes'][1]['parameters'].update(jsonOutput="={{ process.env }}"),
                   lambda d:d['nodes'][1]['parameters'].update(jsonOutput="={{ $json['constructor'] }}"),
                   lambda d:d['nodes'][2]['parameters'].update(respondWith='redirect')]
        for change in mutations:
            with self.subTest(change=change):
                data=blueprint_fixture(); change(data)
                with self.assertRaises(ValueError): validate_blueprint(data,contract_fixture())

    def test_remote_definition_matches_source_and_has_no_hidden_effects(self):
        source=blueprint_fixture(); contract=contract_fixture()
        remote={'id':'qa-own','name':contract.workflow_name,'versionId':'v1','active':False,
            'nodes':[{'name':n['name'],'type':n['type'],'typeVersion':n['version'],'parameters':n['parameters']} for n in source['nodes']],
            'connections':{'QA Webhook':{'main':[[{'node':'QA Result','type':'main','index':0}]]},
                           'QA Result':{'main':[[{'node':'QA Response','type':'main','index':0}]]}},'settings':{}}
        verify_remote(remote,source,contract)
        remote['nodes'][1]['parameters']={**remote['nodes'][1]['parameters'],'includeOtherFields':True}
        with self.assertRaises(ValueError): verify_remote(remote,source,contract)
        remote['nodes'][1]['parameters'].pop('includeOtherFields')
        remote['nodes'][0]['parameters']={**remote['nodes'][0]['parameters'],'options':{'responseHeaders':{'bad':True}}}
        with self.assertRaises(ValueError): verify_remote(remote,source,contract)
        remote['nodes'][0]['parameters']['options']={}
        remote['nodes'][1]['credentials']={'customer':{'id':'forbidden'}}
        with self.assertRaises(ValueError): verify_remote(remote,source,contract)
