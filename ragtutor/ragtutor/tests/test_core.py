from ragtutor.core.document_processor import _split_text_with_overlap


def test_split_text_with_overlap_basic():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = _split_text_with_overlap(text, chunk_size=10, overlap=2)
    # Expected windows: [0:10], [8:18], [16:26], [24:26]
    assert chunks[0] == "abcdefghij"
    assert chunks[1].startswith("ijklmnopqr"[:10-2])
    assert len(chunks) >= 3

