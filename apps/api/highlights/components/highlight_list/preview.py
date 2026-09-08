from citry_preview.preview import Preview
from highlights.components.highlight_card.preview import QUOTE_ONLY, WITH_COMMENT

HIGHLIGHTS = [QUOTE_ONLY, WITH_COMMENT]

PREVIEWS = [
    Preview(
        slug="highlight-list",
        title="HighlightList",
        description="Stacked cards as a fragment an HTMX swap can replace.",
        component="highlight_list",
        group="Molecules",
        kwargs={"highlights": HIGHLIGHTS},
    ),
]
