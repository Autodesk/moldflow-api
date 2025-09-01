"""
Unit-tests for SafeCOMProxy (matches project test style).
"""

from unittest.mock import Mock
import pytest
from moldflow.com_proxy import SafeCOMProxy, safe_com, flag_com_method, expose_oleobj


@pytest.mark.unit
class TestUnitComProxy:
    """Test suite for SafeCOMProxy."""

    @pytest.fixture
    def proxy_pair(self):
        """Return (raw_mock, proxy) tuple."""
        raw = Mock(name="RawCOM")
        return raw, safe_com(raw)

    @pytest.mark.parametrize("prop_val, method_ret", [(10, 42), (123, 7)])
    def test_property_and_method_forwarding(self, proxy_pair, prop_val, method_ret):
        """Proxy correctly forwards attribute gets/sets and method calls."""
        raw, proxy = proxy_pair

        raw.Value = prop_val
        assert proxy.Value == prop_val

        proxy.Value = prop_val + 1
        assert raw.Value == prop_val + 1

        raw.add.return_value = method_ret
        assert proxy.add(1, 2) == method_ret

    def test_missing_attribute_raises(self):
        """Accessing or setting an unsupported attribute raises AttributeError."""
        strict_raw = Mock(spec=())  # strict mock raises on unknown attrs
        proxy = safe_com(strict_raw)
        with pytest.raises(AttributeError):
            _ = proxy.DoesNotExist
        with pytest.raises(AttributeError):
            proxy.DoesNotExist = 1

    def test_internal_com_assignment_does_not_validate(self):
        """Assigning to _com should bypass validation path."""
        proxy = SafeCOMProxy(Mock())
        setattr(proxy, "_com", Mock())

    def test_safe_com_returns_same_proxy(self, proxy_pair):
        """safe_com should be idempotent on an existing proxy."""
        _raw, proxy1 = proxy_pair
        proxy2 = safe_com(proxy1)
        assert proxy1 is proxy2

    def test_equality_and_hashing(self):
        """Equality and hashing reflect underlying COM object identity."""
        raw1 = Mock(name="raw1")
        raw2 = Mock(name="raw2")
        p1a = safe_com(raw1)
        p1b = safe_com(raw1)
        p2 = safe_com(raw2)

        assert p1a == p1b
        assert p1a != p2
        assert hash(p1a) == hash(raw1)
        assert {p1a, p1b, p2} == {p1a, p2}

    def test_expose_oleobj_success_and_missing(self):
        """expose_oleobj should copy _oleobj_ when present and skip when missing."""

        class Dummy:  # pylint: disable=C0115
            pass

        # Success case – proxied object has _oleobj_
        proxied = Dummy()
        proxied._oleobj_ = "SENTINEL"  # pylint: disable=W0212,W0201
        wrapper = Dummy()
        wrapper.prox = proxied  # pylint: disable=W0201

        expose_oleobj(wrapper, attr_name="prox")
        assert getattr(wrapper, "_oleobj_", None) == "SENTINEL"

        # Missing attribute path – should not raise
        wrapper2 = Dummy()
        expose_oleobj(wrapper2, attr_name="does_not_exist")

    def test_flag_com_method_proxy_and_exception(self):
        """flag_com_method should delegate to _FlagAsMethod and ignore errors."""

        raw = Mock(name="RawWithFlag")
        proxy = SafeCOMProxy(raw)

        # Success path – _FlagAsMethod exists and is called
        flag_com_method(proxy, "DoThing")
        raw._FlagAsMethod.assert_called_once_with("DoThing")  # pylint: disable=W0212

        # Exception path – underlying object lacks _FlagAsMethod; should not raise
        raw_no_flag = Mock(name="RawNoFlag")
        del raw_no_flag._FlagAsMethod  # pylint: disable=W0212
        flag_com_method(raw_no_flag, "Whatever")
