from cinefactory.core.dependency_graph import DependencyGraph


def test_selective_invalidation():
    g = DependencyGraph()
    g.add_edge("CHAR_C01_V3", "KF_SH12")
    g.add_edge("KF_SH12", "VIDEO_SH12")
    g.add_edge("CHAR_C01_V3", "KF_SH18")
    assert g.invalidate_from("CHAR_C01_V3") == {"KF_SH12", "VIDEO_SH12", "KF_SH18"}
