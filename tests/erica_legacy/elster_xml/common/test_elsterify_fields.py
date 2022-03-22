import datetime

import pytest

from erica.erica_legacy.elster_xml.common.elsterify_fields import elsterify_anrede, elsterify_date, \
    elsterify_grundstuecksart
from erica.erica_legacy.request_processing.erica_input.v2.grundsteuer_input_eigentuemer import Anrede
from erica.erica_legacy.request_processing.erica_input.v2.grundsteuer_input_grundstueck import Grundstuecksart


class TestElsterifyAnrede:
    def test_no_anrede_is_correctly_translated(self):
        result = elsterify_anrede(Anrede.no_anrede)
        assert result == '01'

    def test_herr_is_correctly_translated(self):
        result = elsterify_anrede(Anrede.herr)
        assert result == '02'

    def test_frau_is_correctly_translated(self):
        result = elsterify_anrede(Anrede.frau)
        assert result == '03'

    def test_invalid_value_raises_key_error(self):
        with pytest.raises(KeyError):
            elsterify_anrede("INVALID")


class TestElsterifyGrundstuecksart:
    def test_baureif_is_correctly_translated(self):
        result = elsterify_grundstuecksart(Grundstuecksart.baureif)

        assert result == 1

    def test_abweichende_entwicklung_is_correctly_translated(self):
        result = elsterify_grundstuecksart(Grundstuecksart.abweichendeEntwicklung)

        assert result == 1

    def test_einfamilienhaus_is_correctly_translated(self):
        result = elsterify_grundstuecksart(Grundstuecksart.einfamilienhaus)

        assert result == 2

    def test_zweifamilienhaus_is_correctly_translated(self):
        result = elsterify_grundstuecksart(Grundstuecksart.zweifamilienhaus)

        assert result == 3

    def test_wohnungseigentum_is_correctly_translated(self):
        result = elsterify_grundstuecksart(Grundstuecksart.wohnungseigentum)

        assert result == 5

    def test_invalid_value_raises_key_error(self):
        with pytest.raises(KeyError):
            elsterify_grundstuecksart("INVALID")


class TestElsterifyDate:
    def test_if_valid_date_then_return_correct_format(self):
        result = elsterify_date(datetime.date(1987, 2, 1))
        assert result == "01.02.1987"

    def test_if_none_given_then_return_none(self):
        result = elsterify_date(None)
        assert result is None

    def test_if_invalid_date_then_raise_attribute_error(self):
        with pytest.raises(AttributeError):
            elsterify_date("INVALID")
