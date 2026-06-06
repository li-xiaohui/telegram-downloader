import pytest
from wiki_tool import channel_slug


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Core Value", "core-value"),
        ("YeouidoStory2", "yeouido-story-2"),
        ("bbong_tta", "bbong-tta"),
        ("Brain and Body Research", "brain-and-body-research"),
        ("Ten_level", "ten-level"),
        ("YM Research", "ym-research"),
    ],
)
def test_channel_slug(name, expected):
    assert channel_slug(name) == expected
