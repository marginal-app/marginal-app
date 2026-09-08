from dataclasses import dataclass

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from citry_preview.previews import PREVIEWS, Preview, preview_by_slug
from citry_preview.rendering import render_component


@dataclass(frozen=True)
class RenderedPreview:
    slug: str
    title: str
    description: str
    group: str
    html: str
    is_atom: bool = False


def _render_preview(preview: Preview, request: HttpRequest) -> str:  # noqa: ARG001
    return render_component(preview.component, preview.kwargs)


def _rendered(preview: Preview, request: HttpRequest) -> RenderedPreview:
    return RenderedPreview(
        slug=preview.slug,
        title=preview.title,
        description=preview.description,
        group=preview.group,
        html=_render_preview(preview, request),
        is_atom=preview.group == "Primitives",
    )


@require_http_methods(["GET"])
def gallery_view(request: HttpRequest) -> HttpResponse:
    previews = [_rendered(preview, request) for preview in PREVIEWS]
    return render(request, "citry_preview/gallery.html", {"previews": previews})


@require_http_methods(["GET"])
def silhouette_view(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        preview = preview_by_slug(slug)
    except KeyError as exc:
        raise Http404(f"Unknown preview: {slug}") from exc
    context = {"preview": _rendered(preview, request)}
    return render(request, "citry_preview/silhouette.html", context)
