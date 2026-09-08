"""Build gallery Preview rows from a component's declared PreviewVariant.variants().

A component attaches its preview states directly in its own module — no
separate preview.py, no external group= parameter — as a nested
`PreviewVariant` class that inherits from `Kwargs`. Its `variants`
classmethod names its bound parameter `variant` instead of the conventional
`cls`, since inside this one method it always means "construct one variant
of this component's Kwargs":

    class Status(Component):
        @dataclass
        class Kwargs:
            tone: str = "ok"
            message: str = ""

        class PreviewVariant(Kwargs):
            group: ClassVar[str] = "Primitives"

            @classmethod
            def variants(variant: type[Self]):
                return [
                    variant(message="..."),
                    meta(
                        variant(tone="error", message="..."),
                        slug="error",
                        description="Error tone — ping failed.",
                    ),
                ]

`group` needs the explicit `ClassVar[str]` annotation, not just `group =
"Primitives"`. `PreviewVariant` subclasses the dataclass `Kwargs`, and an
unannotated assignment in a dataclass subclass's body is ambiguous to a
static checker the same way it's ambiguous to `dataclasses` itself — for
`previews_from_variants`'s `component_cls: type[PreviewableComponent]`
parameter below to accept a real component, pyrefly needs to confirm
`SomeComponent.PreviewVariant.group` really is a `ClassVar[str]` and not an
instance-scoped field; verified empirically that omitting the annotation
makes every call site (`preview_by_slug(Status, ...)`, `discover_previews()`
itself) fail with "is not a ClassVar" even though nothing about the runtime
behavior changes.

`discover_previews()` (in `citry_preview/discover.py`) finds every component
with a `PreviewVariant` by asking Citry's own registry (`app.components`)
directly, so a component with nothing to preview is just skipped — there is
nothing to register or wire up by hand.

The `variant: type[Self]` parameter annotation is required, not decorative
— and it's the *only* annotation `variants` needs; no return type. Verified
empirically: with no annotation on `variants` at all (not even a return
type), pyrefly silently accepts a typo'd field name — an unannotated
function's body isn't checked strictly. A return-type-only annotation
(`-> list[...]`) also turns checking on, but `variant: type[Self]` is
simpler still: it needs no import of `Variant` into every component file,
and pyrefly still correctly infers the real return type from the body once
checking is on. A wrapping decorator does *not* substitute for this — a
decorator's own declared signature doesn't retroactively make pyrefly
check the wrapped function's body strictly; that's tied to whether the
original `def`, as written, carries its own annotation.

`class PreviewVariant(Kwargs):` — referencing the sibling nested `Kwargs`
class in PreviewVariant's own base-class list — works because a base-class
expression evaluates in the *enclosing* class's body (Status's), where
`Kwargs` was already bound by the time `class PreviewVariant(Kwargs):` runs.
That's different from referencing `Kwargs` bare inside PreviewVariant's own
body (e.g. a plain `variants = [Kwargs(), ...]` list statement there), which
raises NameError: nested class bodies don't close over an enclosing class's
namespace the way nested functions close over an enclosing function's, and
that's true even for a method's body defined inside the nested class, not
just direct class attributes.

`variants` still has to be a classmethod rather than a plain list for the
same reason: only a method's body defers execution until called, by which
point the bound parameter is simply `PreviewVariant` (or whichever
subclass), inheriting `Kwargs`'s fields and dataclass-generated `__init__`
— so calling it is a real, type-checked constructor call with no
per-component annotation needed. `PreviewVariant` genuinely "is a" `Kwargs`
(a variant is a concrete set of Kwargs values), unlike naming the class bare
`Preview`, which would misleadingly suggest an is-a relationship with
something that isn't a kind of Kwargs at all.

No other mechanism was found that keeps a separate nested class, avoids
repeating the component's own name anywhere, and gets real pyrefly
validation, all three at once — every generic indirection tried (a
`**kwargs`-forwarding classmethod — verified empirically not to work even
when defined directly on the real Kwargs class itself, since `**kwargs` is
opaque to static analysis regardless of where it lives — a class decorator
injecting an attribute, a `Generic[TypeVar]` base with `__init_subclass__`
reflection) type-checked as `Any` and silently accepted made-up field names.
The classmethod's bound parameter, tied through Python's own subclassing,
is the one mechanism where the binding is real enough for pyrefly to trace
back to the concrete `Kwargs` class, verified empirically: a typo'd field
name is correctly flagged as an unexpected keyword argument.

Decorate `Kwargs` with `@dataclasses.dataclass` explicitly. Citry keeps an
explicitly-decorated dataclass's authored options as-is instead of
converting it, and a plain `@dataclass` is what lets pyrefly (or any
standard type checker) verify these constructor calls in the first place —
undecorated, Citry's own runtime conversion into a dataclass isn't visible
to static analysis, so every `Kwargs(field=value)` call reads as an invalid
`object.__init__` call.

A bare `variant(...)` entry gets its slug auto-derived from whichever
fields differ from the declared defaults (`f"{component_name}-{field}-{value}..."`),
with a title of `f"{ComponentClassName} / {suffix}"` and an empty
description. Wrap it in `meta(...)` to set an explicit `slug` (the complete
final slug, not a suffix — some existing components' slugs don't follow the
`<component-name>-<suffix>` shape, e.g. `empty_state`'s single state is
`"empty-state"`, not `"empty_state-default"`), `title`, and/or
`description` — needed whenever the auto-derived slug wouldn't read well,
or when a non-identity field (like a fixture message) also happens to
differ from the default and would otherwise leak into the auto-derived
slug.
"""

import dataclasses
from typing import TYPE_CHECKING, ClassVar, Protocol

from citry_preview.preview import Preview

if TYPE_CHECKING:
    from collections.abc import Sequence

    from _typeshed import DataclassInstance


@dataclasses.dataclass(frozen=True)
class Variant[K]:
    kwargs: K
    slug: str | None = None
    title: str | None = None
    description: str = ""


def meta[K](
    kwargs: K,
    *,
    slug: str | None = None,
    title: str | None = None,
    description: str = "",
) -> Variant[K]:
    return Variant(kwargs=kwargs, slug=slug, title=title, description=description)


class _PreviewVariantLike(Protocol):
    group: ClassVar[str]

    @classmethod
    def variants(cls) -> "Sequence[object]": ...


class PreviewableComponent(Protocol):
    """What `previews_from_variants` needs from a component — nothing more.

    A structural type, not a specific component: it doesn't (and can't) know
    any component's actual Kwargs fields, only that a `PreviewVariant` with
    this shape exists. That's the real boundary of what this generic,
    reflection-based code can know — same reasoning as Citry's own
    `Component.template_data(self, kwargs: Any, slots: Any)`, just expressed
    as a Protocol here instead of `Any` because there's an actual known
    contract (name, Kwargs, PreviewVariant) that's worth stating precisely.
    """

    name: ClassVar[str | None]
    Kwargs: ClassVar[type["DataclassInstance"]]
    PreviewVariant: ClassVar[type[_PreviewVariantLike]]


def previews_from_variants(component_cls: type[PreviewableComponent]) -> list[Preview]:
    name = component_cls.name
    if name is None:
        msg = f"{component_cls.__name__}: a registered component always has a name"
        raise AssertionError(msg)
    title_base = component_cls.__name__
    preview_variant = component_cls.PreviewVariant
    group = preview_variant.group
    field_names = [f.name for f in dataclasses.fields(component_cls.Kwargs)]
    try:
        defaults = component_cls.Kwargs()
    except TypeError:
        # Kwargs has required fields (no defaults for every field), so there is
        # no meaningful "default" to diff a variant against for slug/title
        # auto-derivation. Every variant of a component like this must pass an
        # explicit slug to meta(...).
        defaults = None

    previews: list[Preview] = []
    for entry in preview_variant.variants():
        row = entry if isinstance(entry, Variant) else Variant(kwargs=entry)
        auto_suffix = None
        if defaults is not None:
            diff = {
                field: getattr(row.kwargs, field)
                for field in field_names
                if getattr(row.kwargs, field) != getattr(defaults, field)
            }
            auto_suffix = "-".join(f"{field}-{value}" for field, value in diff.items()) or "default"
        if row.slug is None and auto_suffix is None:
            msg = (
                f"{name}: PreviewVariant entry needs an explicit meta(..., slug=...) — "
                "Kwargs has required fields, so a slug can't be auto-derived from defaults."
            )
            raise ValueError(msg)
        slug = row.slug or f"{name}-{auto_suffix}"
        previews.append(
            Preview(
                slug=slug,
                title=row.title or f"{title_base} / {row.slug or auto_suffix}",
                description=row.description,
                component=name,
                group=group,
                kwargs={field: getattr(row.kwargs, field) for field in field_names},
            )
        )
    return previews


def merge_previews(*groups: list[Preview]) -> list[Preview]:
    merged: list[Preview] = []
    slugs: set[str] = set()
    for group in groups:
        for preview in group:
            if preview.slug in slugs:
                raise ValueError(f"Duplicate preview slug: {preview.slug}")
            slugs.add(preview.slug)
            merged.append(preview)
    return merged
