import pytest
from cinefactory.workflows.safety import WorkflowSafetyValidator


def test_workflow_safety_blocks_cloud_provider_node():
    wf={'1':{'class_type':'KlingVideoAPI','inputs':{'prompt':'hello'}}}
    r=WorkflowSafetyValidator().review(wf)
    assert not r.passed
    assert any('FORBIDDEN_PROVIDER_NODE' in x for x in r.findings)


def test_workflow_safety_blocks_public_url():
    wf={'1':{'class_type':'LocalNode','inputs':{'endpoint':'https://api.example.com/render'}}}
    r=WorkflowSafetyValidator().review(wf)
    assert not r.passed
    assert any('PUBLIC_NETWORK_URL' in x for x in r.findings)


def test_workflow_safety_allows_loopback_url():
    wf={'1':{'class_type':'LocalNode','inputs':{'endpoint':'http://127.0.0.1:8188'}}}
    WorkflowSafetyValidator().require_safe(wf)
