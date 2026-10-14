from cinefactory.artifacts.store import ArtifactStore
from cinefactory.domain.enums import ArtifactKind


def test_artifact_store_deduplicates_content(tmp_path):
    src=tmp_path/'a.txt'; src.write_text('hello')
    store=ArtifactStore(tmp_path/'store')
    a=store.ingest('P',src,ArtifactKind.REPORT)
    b=store.ingest('P',src,ArtifactKind.REPORT)
    assert a.content_hash==b.content_hash
    assert a.relative_path==b.relative_path
