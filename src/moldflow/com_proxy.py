# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Proxy utilities to add runtime attribute-existence checking for COM objects.

The philosophy:
  • Wrap the raw COM interface once, in the wrapper __init__.
  • Every subsequent attribute access is automatically verified.
  • Keeps wrapper methods clean and consistently safe.
"""

from .logger import process_log
from .common import LogMessage
from .errors import raise_attribute_error

# ------------------------------------------------------------------
# Helper: Verify COM attribute existence
# ------------------------------------------------------------------


def _verify_com_attribute(obj, attribute: str):
    """
    Raise *AttributeError* if *attribute* is not present on *obj*.

    This is kept close to *SafeCOMProxy* because it is only used for COM
    interface safety.

    Args:
        obj: The COM object to verify.
        attribute (str): The attribute to verify.
    """
    process_log(__name__, LogMessage.HELPER_CHECK, locals(), value=obj, name=attribute)
    if not hasattr(obj, attribute):
        raise_attribute_error(attribute)
    process_log(__name__, LogMessage.VALID_INPUT)


class SafeCOMProxy:
    """Lightweight proxy around a COM object that validates attribute access.

    It intercepts *all* attribute look-ups, runs ``verify_com_attribute`` once,
    then returns the attribute from the underlying COM object.
    """

    __slots__ = ("_com",)

    def __init__(self, com_obj):
        """
        Initialize the SafeCOMProxy with a COM object.

        Args:
            com_obj: The COM object to wrap.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="SafeCOMProxy")
        self._com = com_obj

    # ------------------------------------------------------------------
    # Dynamic attribute forwarding with validation
    # ------------------------------------------------------------------
    def __getattr__(self, item):
        """Validate then forward attribute access to the wrapped COM object.

        Special-case ``_oleobj_`` so that the proxy behaves exactly like the
        original ``PyIDispatch`` object when it is passed back into COM API
        calls.  win32com checks for this attribute to obtain the raw COM
        pointer; exposing it here makes ``SafeCOMProxy`` transparently
        acceptable as an argument to other COM methods.

        Args:
            item: The name of the attribute.
        """

        # Allow COM marshaler to unwrap the proxy
        if item == "_oleobj_":
            return getattr(self._com, "_oleobj_", None)

        _verify_com_attribute(self._com, item)
        attr = getattr(self._com, item)
        return attr

    # Forward attribute assignment to wrapped COM object, except for internal _com
    def __setattr__(self, name, value):
        """
        Set an attribute on the wrapped COM object.

        Args:
            name: The name of the attribute.
            value: The value to set.
        """
        if name == "_com":
            object.__setattr__(self, name, value)
        else:
            _verify_com_attribute(self._com, name)
            setattr(self._com, name, value)

    # ------------------------------------------------------------------
    # Equality / hashing so tests comparing against raw mocks still pass
    # ------------------------------------------------------------------

    def __eq__(self, other):
        """
        Check if two SafeCOMProxy objects are equal.

        Args:
            other: The other SafeCOMProxy object to compare with.
        """
        if isinstance(other, SafeCOMProxy):
            return self._com == other._com
        return self._com == other

    def __hash__(self):
        """
        Get the hash of the wrapped COM object.
        """
        return hash(self._com)


def safe_com(obj):
    """
    Return a *SafeCOMProxy* wrapping *obj* if it isn’t already wrapped.

    Args:
        obj: The COM object to wrap.
    """
    return obj if isinstance(obj, SafeCOMProxy) else SafeCOMProxy(obj)


# ------------------------------------------------------------------
# Helper to expose _oleobj_ on wrapper objects
# ------------------------------------------------------------------


def expose_oleobj(container, attr_name="_com"):
    """Attach `_oleobj_` to *container* by copying it from the wrapped COM object.

    The majority of wrapper classes store the underlying COM interface in an
    attribute (commonly `ent_list`, `predicate`, etc.).  Win32com retrieves the
    raw pointer via this sentinel attribute when a Python object is used as an
    argument to another COM call.  By copying `_oleobj_` up to the wrapper we
    make the wrapper directly passable to COM without hand-written hacks.

    Args:
        container: The wrapper instance we are modifying.
        attr_name: Name of the attribute that references the proxied COM
                   object inside *container*.

    Returns:
        None
    """

    try:
        proxied = getattr(container, attr_name)
        ole_ptr = getattr(proxied, "_oleobj_", None)
        setattr(container, "_oleobj_", ole_ptr)
    except AttributeError:
        # Either the attribute does not exist or the proxied object lacks
        # _oleobj_.  In both cases we silently skip — the wrapper simply will
        # not be passable to COM until the attribute appears.
        pass


def flag_com_method(com_object, method_name: str):
    """
    Ensure *method_name* on *com_object* is dispatched as a method.

    When pywin32 accesses a COM attribute with no type information it may
    interpret it as a property-get.  Calling ``_FlagAsMethod`` on the underlying
    ``PyIDispatch`` object forces future accesses to use ``DISPATCH_METHOD``.

    This helper transparently unwraps our :class:`SafeCOMProxy` so callers
    don’t need to reach inside for the ``_com`` attribute.

    Args:
        com_object: The COM object to flag.
        method_name (str): The name of the method to flag.

    Returns:
        None
    """

    raw = (
        com_object._com  # pylint: disable=protected-access
        if isinstance(com_object, SafeCOMProxy)
        else com_object  # pylint: disable=protected-access
    )
    try:
        raw._FlagAsMethod(method_name)  # pylint: disable=protected-access
    except Exception:
        # Either the attribute doesn’t exist or COM rejected it – ignore and
        # let normal dispatch happen (a subsequent call may still work).
        pass
