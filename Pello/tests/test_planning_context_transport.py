"""Role-bounded architecture input and lossless planning-context transport."""
import copy,json,unittest
from athis_autopilot.product_planning import ProductPlanningCore
from tests.test_planning_graph import sample,proposal

class PlanningContextTransportTests(unittest.TestCase):
    def payload(self):
        rows=[{'requirement_identifier':f'R{i}','source_reference_identifiers':['S1'],
               'normalized_business_requirement':'Preserve exact source values and business constraints. '*2,
               'authorization_required':False,'verification_expectations':['v'*140],
               'explicit_exclusions':['No external execution'],'unapproved_assumptions':['Local storage is proposed only']}
              for i in range(130)]
        return {'requirements':{'source_segments':[{'source_id':'S1','text':'Original source. '*350}],
                                'requirements':rows},'execution_authorized':False}
    def unpack(self,v):
        if isinstance(v,dict):
            if set(v)=={'pello_table_columns','pello_table_rows'}:
                return [{k:self.unpack(x) for k,x in zip(v['pello_table_columns'],row)} for row in v['pello_table_rows']]
            return {k:self.unpack(x) for k,x in v.items()}
        if isinstance(v,list):return [self.unpack(x) for x in v]
        return v
    def test_large_planning_payload_preserves_every_field_without_mutating_input(self):
        for phase in ['plan-increments','plan-contracts','plan-models']:
            with self.subTest(phase=phase):
                value=self.payload();before=copy.deepcopy(value)
                self.assertGreater(len(json.dumps(value,separators=(',',':'))),55000)
                prompt=ProductPlanningCore._prompt(phase,value);self.assertLessEqual(len(prompt),55000)
                packed=json.loads(prompt.split('DATA JSON:\n',1)[1]);packed.pop('pello_context_encoding')
                self.assertEqual(self.unpack(packed),before);self.assertEqual(value,before)
    def test_small_context_stays_unchanged(self):
        value={'requirements':[{'id':'R1','description':'small'}]}
        self.assertEqual(json.loads(ProductPlanningCore._prompt('plan-increments',value).split('DATA JSON:\n',1)[1]),value)
    def test_unreducible_or_conflicting_transport_markers_fail_closed(self):
        for value in [{'data':'x'*60000},{**self.payload(),'pello_table_rows':[]}]:
            with self.assertRaisesRegex(ValueError,'55,000'):ProductPlanningCore._prompt('plan-increments',value)
    def test_increment_context_keeps_exact_nodes_globals_and_all_source_semantics(self):
        a=sample();architecture=proposal(a);original=copy.deepcopy(architecture)
        core=object.__new__(ProductPlanningCore)
        core.planner_input=lambda _: {'requirements':a.model_dump(mode='json'),'execution_authorized':False}
        core.planning_stage=lambda *_: {'proposal':architecture}
        core.version_row=lambda _: {'version':1}
        captured={}
        class Capture(Exception):pass
        def invoke(*args,**kwargs):captured.update(args[4]);raise Capture()
        core._invoke=invoke
        with self.assertRaises(Capture):core.propose_increments('synthetic')
        self.assertEqual(captured['architecture'],{'nodes':original['nodes'],'global_requirement_ids':original['global_requirement_ids']})
        self.assertEqual(captured['requirements'],a.model_dump(mode='json'));self.assertEqual(architecture,original)
