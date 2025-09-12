from __future__ import annotations
from collections.abc import Mapping, Sequence, Set
from dataclasses import is_dataclass, fields, MISSING
from typing import Any, get_args, get_origin, Union, Optional

import mathinteractive

try:
    from typing import TypedDict  # 3.11+
except ImportError:
    try:
        from typing_extensions import TypedDict  # type: ignore
    except Exception:
        TypedDict = None  # type: ignore


def shape(x: Any, *, max_depth: int = 5, tuple_limit: int = 6, type_hint: Any = None) -> str:
    """
    Terse 'shape' descriptions for Python values with dataclass/TypedDict support.

    Examples:
        shape(User(name="A", tags=["x"]))              -> 'User{name: str, tags: list[str] (1)}'
        shape(data, type_hint=MyTypedDict)             -> '{id: int, name?: str, tags?: list[str]}'
        shape([{"id":1},{"id":2}], type_hint=list[dict[str,int]])
                                                       -> 'list[dict[str, int]] (2)'

    Notes:
      - If a dataclass, shows fields using annotations when available; falls back to value shapes.
      - If given a TypedDict *class* via `type_hint`, prints its schema with required `key:` and optional `key?:`.
      - For plain dict/list/tuple, you can pass `type_hint` like dict[str,int] or list[User].
      - Cycles and deep nesting are elided with '…'.
    """
    seen = set()

    def is_typeddict_cls(tp: Any) -> bool:
        if TypedDict is None:
            return False
        # Heuristic: TypedDict classes are `dict`-like with __annotations__ and special keys sets
        return isinstance(tp, type) and issubclass(tp, dict) and hasattr(tp, "__annotations__")

    def render_typeddict_schema(tp: Any) -> str:
        # Works on a TypedDict *class*
        ann = getattr(tp, "__annotations__", {})
        req = set(getattr(tp, "__required_keys__", set()))
        opt = set(getattr(tp, "__optional_keys__", set()))
        parts = []
        for k, t in ann.items():
            key = f"{k}?" if (k in opt and k not in req) else k
            parts.append(f"{key}: {ann_to_str(t)}")
        return "{%s}" % (", ".join(parts))

    def ann_to_str(tp: Any) -> str:
        """Pretty string for typing annotations (PEP 585/604 aware)."""
        if tp is Any:
            return "Any"
        origin = get_origin(tp)
        args = get_args(tp)

        # Union / Optional (PEP 604 | or typing.Union)
        if origin is Union:
            alts = [ann_to_str(a) for a in args]
            # Optional[T] becomes 'T | None'
            return " | ".join(sorted(set(alts)))

        # Annotated[T, ...]
        if str(origin).endswith("Annotated"):
            return ann_to_str(args[0])

        # Literal[...] (render as the literals)
        if (getattr(origin, "__name__", "") or str(origin)).endswith("Literal"):
            return " | ".join(repr(a) for a in args)

        # Parametrized containers
        if origin in (list, tuple, set, frozenset):
            if not args:
                return origin.__name__
            if origin is tuple:
                if len(args) == 2 and args[1] is ...:
                    return f"tuple[{ann_to_str(args[0])}, ...]"
                else:
                    return "tuple[" + ", ".join(ann_to_str(a) for a in args) + "]"
            return f"{origin.__name__}[{ann_to_str(args[0])}]"

        if origin in (dict, Mapping):
            if len(args) == 2:
                return f"dict[{ann_to_str(args[0])}, {ann_to_str(args[1])}]"
            return "dict"

        # Builtins or classes
        if isinstance(tp, type):
            return tp.__name__

        # PEP 695 type parameters or special forms
        return str(tp).replace("typing.", "")

    def apply_type_hint_to_container(o: Any, hint: Any) -> str | None:
        """If hint is a container/TypedDict, use it to format the container type tersely."""
        if hint is None:
            return None
        origin = get_origin(hint)
        args = get_args(hint)

        # TypedDict schema (class) — render schema only
        if is_typeddict_cls(hint):
            return render_typeddict_schema(hint)

        # dict/Mapping[K, V]
        if isinstance(o, Mapping) and (origin in (dict, Mapping) or hint is dict):
            if len(args) == 2:
                return f"dict[{ann_to_str(args[0])}, {ann_to_str(args[1])}] ({len(o)})"
            return f"dict ({len(o)})"

        # list[T] / set[T] / tuple[...] hints
        if isinstance(o, Sequence) and not isinstance(o, (str, bytes, bytearray)):
            if origin in (list, tuple) or hint in (list, tuple):
                inner = ann_to_str(args[0]) if args else "Any"
                n = len(o)
                if (origin or hint) is tuple and args and len(args) > 1 and args[-1] is not ...:
                    inner = ", ".join(ann_to_str(a) for a in args)
                    return f"tuple[{inner}]"
                return f"{(origin or hint).__name__}[{inner}] ({n})"

        if isinstance(o, Set) and (origin in (set, frozenset) or hint in (set, frozenset)):
            inner = ann_to_str(args[0]) if args else "Any"
            return f"{(origin or hint).__name__}[{inner}] ({len(o)})"

        return None

    def _shape(o: Any, depth: int, hint: Any = None) -> str:
        oid = id(o)
        if oid in seen:
            return "…"
        if depth <= 0:
            return "…"

        # If a type_hint can drive container printing, try that first.
        hinted = apply_type_hint_to_container(o, hint)
        if hinted is not None:
            return hinted

        # Scalars
        if o is None:
            return "None"
        t = type(o)
        tn = t.__name__

        # NumPy-ish
        if hasattr(o, "shape") and hasattr(o, "dtype"):
            try:
                shp = "×".join(map(str, o.shape))
            except Exception:
                shp = "?"
            try:
                dt = str(o.dtype)
            except Exception:
                dt = "?"
            base = getattr(t, "__name__", "ndarray")
            return f"{base}[{dt}] ({shp})"

        # Pandas (basic)
        mod = getattr(t, "__module__", "")
        if mod.startswith("pandas."):
            if tn == "DataFrame" and hasattr(o, "dtypes"):
                try:
                    dtypes = ", ".join(f"{c}:{str(dt)}" for c, dt in o.dtypes.items())
                except Exception:
                    dtypes = "…"
                r, c = getattr(o, "shape", ("?", "?"))
                return f"DataFrame[{dtypes}] ({r}×{c})"
            if tn == "Series" and hasattr(o, "dtype"):
                n = getattr(o, "shape", (None,))[0]
                return f"Series[{str(o.dtype)}] ({n})"
            return tn

        # Dataclass (instance)
        if is_dataclass(o):
            seen.add(oid)
            try:
                parts = []
                for f in fields(o):
                    ann = f.type if f.type is not None else Any
                    val_present = True
                    try:
                        v = getattr(o, f.name)
                    except Exception:
                        val_present = False
                        v = None
                    # Prefer annotation as the primary description; append value-counts where helpful
                    if val_present:
                        # For container fields, show value-aware shapes (counts), guided by annotation
                        parts.append(f"{f.name}: {_shape(v, depth-1, ann)}")
                    else:
                        parts.append(f"{f.name}: {ann_to_str(ann)}")
                return f"{tn}" + "{" + ", ".join(parts) + "}"
            finally:
                seen.discard(oid)

        # TypedDict *classes* passed directly
        if is_typeddict_cls(o):
            return render_typeddict_schema(o)

        # Mappings
        if isinstance(o, Mapping):
            seen.add(oid)
            try:
                ktypes = _union(list(o.keys()), depth-1)
                vtypes = _union(list(o.values()), depth-1)
            finally:
                seen.discard(oid)
            return f"dict[{ktypes}, {vtypes}] ({len(o)})"

        # Bytes/str
        if isinstance(o, (str, bytes, bytearray)):
            base = "str" if isinstance(o, str) else ("bytes" if isinstance(o, bytes) else "bytearray")
            return f"{base} ({len(o)})"

        # Tuples
        if isinstance(o, tuple):
            seen.add(oid)
            try:
                if len(o) <= tuple_limit:
                    inner = ", ".join(_shape(e, depth-1) for e in o)
                    return f"tuple[{inner}]"
                else:
                    inner = _union(o, depth-1)
                    return f"tuple[{inner}] ({len(o)})"
            finally:
                seen.discard(oid)

        # Lists / general Sequences (but not str/bytes handled above)
        if isinstance(o, Sequence):
            seen.add(oid)
            try:
                inner = _union(o, depth-1)
            finally:
                seen.discard(oid)
            return f"list[{inner}] ({len(o)})"

        # Sets
        if isinstance(o, Set):
            seen.add(oid)
            try:
                inner = _union(o, depth-1)
            finally:
                seen.discard(oid)
            return f"set[{inner}] ({len(o)})"

        # Fallback
        if hasattr(o, "__dict__") or hasattr(o, "__slots__"):
            return tn
        return tn

    def _union(iterable, depth):
        if not iterable:
            return "Any"
        parts = {_shape(e, depth) for e in iterable}
        if len(parts) == 1:
            return next(iter(parts))
        return " | ".join(sorted(parts))

    return _shape(x, max_depth, type_hint)

__all__ = ["shape","mathinteractive"]
