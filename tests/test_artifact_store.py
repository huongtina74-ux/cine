from cinefactory.domain.enums import ArtifactKind
from cinefactory.storage.artifacts import ContentAddressedArtifactStore


def test_content_addressed_store_deduplicates(tmp_path):
    source = tmp_path / "frame.bin"
    source.write_bytes(b"same-content")
    store = ContentAddressedArtifactStore(tmp_path / "artifacts")
    a = store.ingest(source, project_id="P1", kind=ArtifactKind.IMAGE)
    b = store.ingest(source, project_id="P1", kind=ArtifactKind.IMAGE)
    assert a.content_hash == b.content_hash
    assert a.relative_path == b.relative_path
    assert store.resolve(a).exists()
