import pytest
from cinefactory.workflows.compiler import WorkflowTemplateCompiler


def test_workflow_tokens_preserve_types():
    t={"1":{"inputs":{"text":"${PROMPT}","seed":"${SEED}","x":"hello ${SHOT_ID}"}}}
    out=WorkflowTemplateCompiler().compile(t,{"PROMPT":"abc","SEED":123,"SHOT_ID":"S01"})
    assert out['1']['inputs']['seed']==123
    assert out['1']['inputs']['x']=='hello S01'


def test_missing_workflow_token_fails():
    with pytest.raises(KeyError):
        WorkflowTemplateCompiler().compile({"x":"${MISSING}"},{})
