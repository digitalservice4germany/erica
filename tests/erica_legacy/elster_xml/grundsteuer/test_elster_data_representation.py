from xml.etree import ElementTree

import pytest

from erica.erica_legacy.elster_xml.common.basic_xml_data_representation import EXml
from erica.erica_legacy.elster_xml.common.xml_conversion import convert_object_to_xml
from erica.erica_legacy.elster_xml.grundsteuer.elster_data_representation import ERueckuebermittlung, EVorsatz, \
    EGrundsteuerSpecifics, EGrundsteuerData, \
    get_full_grundsteuer_data_representation, EGW2, EGW1, EErgAngaben
from erica.erica_legacy.elster_xml.grundsteuer.elster_eigentuemer import EAngFeststellung, EPersonData, EEigentumsverh, \
    EEmpfangsbevollmaechtigter
from erica.erica_legacy.elster_xml.grundsteuer.elster_gebaeude import EAngWohn
from erica.erica_legacy.request_processing.erica_input.v2.grundsteuer_input_eigentuemer import Eigentuemer, Person
from erica.erica_legacy.elster_xml.grundsteuer.elster_grundstueck import ELage, EAngGrundstuecksart, EMehrereGemeinden, \
    EGemarkungen, EAngGrund
from tests.erica_legacy.samples.grundsteuer_sample_data import get_grundsteuer_sample_data, \
    get_sample_single_person_dict, get_sample_empfangsbevollmaechtigter_dict, SampleGrundstueck


class TestEErgAnbaben:
    def test_if_instantiated_then_set_flag_and_value(self):
        result = EErgAngaben("foo bar baz")

        assert result.E7413001 == 1
        assert result.E7411702 == "foo bar baz"


class TestEGW1:
    def test_if_one_person_then_attributes_set_correctly(self):
        person = get_sample_single_person_dict()
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [person], "empfangsbevollmaechtigter": get_sample_empfangsbevollmaechtigter_dict()})
        grundstueck_obj = SampleGrundstueck().parse()
        result = EGW1(eigentuemer_obj, grundstueck_obj)

        assert result.Ang_Feststellung == EAngFeststellung()
        assert len(result.Eigentuemer) == 1
        assert result.Eigentuemer[0] == EPersonData(Person.parse_obj(person), person_index=0)
        assert result.Eigentumsverh == EEigentumsverh(eigentuemer_obj)
        assert result.Empfangsv == EEmpfangsbevollmaechtigter(eigentuemer_obj.empfangsbevollmaechtigter)
        assert result.Erg_Angaben is None
        assert len(vars(result)) == 8

    def test_if_no_empfangsbevollmaechtigter_set_then_attributes_set_correctly(self):
        person = get_sample_single_person_dict()
        eigentuemer_obj = Eigentuemer.parse_obj({"person": [person]})
        grundstueck_obj = SampleGrundstueck().parse()

        result = EGW1(eigentuemer_obj, grundstueck_obj)

        assert result.Ang_Feststellung == EAngFeststellung()
        assert len(result.Eigentuemer) == 1
        assert result.Eigentuemer[0] == EPersonData(Person.parse_obj(person), person_index=0)
        assert result.Eigentumsverh == EEigentumsverh(eigentuemer_obj)
        assert result.Empfangsv is None
        assert result.Erg_Angaben is None
        assert len(vars(result)) == 8

    def test_if_two_persons_then_attributes_set_correctly(self):
        person1 = get_sample_single_person_dict()
        person1["persoenlicheAngaben"]["vorname"] = "Albus"
        person2 = get_sample_single_person_dict()
        person2["persoenlicheAngaben"]["vorname"] = "Rubeus"
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [person1, person2], "verheiratet": {"are_verheiratet": False}})
        grundstueck_obj = SampleGrundstueck().parse()

        result = EGW1(eigentuemer_obj, grundstueck_obj)

        assert result.Ang_Feststellung == EAngFeststellung()
        assert len(result.Eigentuemer) == 2
        assert result.Eigentuemer[0] == EPersonData(Person.parse_obj(person1), person_index=0)
        assert result.Eigentuemer[1] == EPersonData(Person.parse_obj(person2), person_index=1)
        assert result.Eigentumsverh == EEigentumsverh(eigentuemer_obj)
        assert result.Empfangsv is None
        assert result.Erg_Angaben is None
        assert len(vars(result)) == 8

    def test_if_valid_grundstueck_then_set_lage_correctly(self):
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [get_sample_single_person_dict()]})
        grundstueck_obj = SampleGrundstueck().innerhalb_einer_gemeinder(False).parse()

        result = EGW1(eigentuemer_obj, grundstueck_obj)

        assert result.Lage == ELage(grundstueck_obj.adresse)
        assert len(vars(result)) == 8

    def test_if_not_innerhalb_einer_gemeinde_then_set_mehrere_gemeinden(self):
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [get_sample_single_person_dict()]})
        grundstueck_obj = SampleGrundstueck().innerhalb_einer_gemeinder(False).parse()

        result = EGW1(eigentuemer_obj, grundstueck_obj)

        assert result.Mehrere_Gemeinden == EMehrereGemeinden()
        assert len(vars(result)) == 8

    def test_if_innerhalb_einer_gemeinde_then_set_mehrere_gemeinden_to_none(self):
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [get_sample_single_person_dict()]})
        grundstueck_obj = SampleGrundstueck().innerhalb_einer_gemeinder(True).parse()

        result = EGW1(eigentuemer_obj, grundstueck_obj)

        assert result.Mehrere_Gemeinden is None
        assert len(vars(result)) == 8

    def test_if_valid_grundstueck_then_set_gemarkungen_correctly(self):
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [get_sample_single_person_dict()]})
        grundstueck_obj = SampleGrundstueck().parse()

        result = EGW1(eigentuemer_obj, grundstueck_obj)

        assert result.Gemarkungen == EGemarkungen(grundstueck_obj.flurstueck)

    def test_if_no_fretext_then_set_field_to_none(self):
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [get_sample_single_person_dict()]})
        grundstueck_obj = SampleGrundstueck().parse()

        result = EGW1(eigentuemer_obj, grundstueck_obj)

        assert result.Erg_Angaben is None

    def test_if_fretext_then_set_field(self):
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [get_sample_single_person_dict()]})
        grundstueck_obj = SampleGrundstueck().parse()

        result = EGW1(eigentuemer_obj, grundstueck_obj, "foo bar")

        assert result.Erg_Angaben == EErgAngaben("foo bar")


class TestEGW2:
    def test_if_valid_input_then_set_fields_correctly(self):
        input_data = get_grundsteuer_sample_data()

        result = EGW2(input_data)

        assert result.Ang_Grundstuecksart == EAngGrundstuecksart(input_data.grundstueck)
        assert result.Ang_Grund == EAngGrund(input_data.grundstueck)
        assert result.Ang_Wohn == EAngWohn(input_data.gebaeude)
        assert len(vars(result)) == 3


class TestERueckuebermittlung:
    def test_attributes_set_correctly(self):
        result = ERueckuebermittlung()

        assert result.Bescheid == "2"
        assert len(vars(result)) == 1


class TestEVorsatz:
    def test_attributes_set_correctly(self):
        grundsteuer_obj = get_grundsteuer_sample_data()

        result = EVorsatz(grundsteuer_obj)

        assert result.Unterfallart == "88"
        assert result.Vorgang == "01"
        assert result.StNr == "1121081508150"
        assert result.Zeitraum == "2022"
        assert result.AbsName == grundsteuer_obj.eigentuemer.person[0].persoenlicheAngaben.vorname + \
               " " + \
               grundsteuer_obj.eigentuemer.person[0].persoenlicheAngaben.name
        assert result.AbsStr == grundsteuer_obj.eigentuemer.person[0].adresse.strasse
        assert result.AbsPlz == grundsteuer_obj.eigentuemer.person[0].adresse.plz
        assert result.AbsOrt == grundsteuer_obj.eigentuemer.person[0].adresse.ort
        assert result.Copyright == "(C) 2022 DigitalService4Germany"
        assert result.OrdNrArt == "S"
        assert result.Rueckuebermittlung == ERueckuebermittlung()
        assert len(vars(result)) == 11


class TestEGrundsteuerSpecifics:
    def test_attributes_set_correctly(self):
        grundsteuer_obj = get_grundsteuer_sample_data()

        result = EGrundsteuerSpecifics(grundsteuer_obj)

        assert result.Vorsatz == EVorsatz(grundsteuer_obj)
        assert result.GW1 == EGW1(grundsteuer_obj.eigentuemer, grundsteuer_obj.grundstueck)
        assert result.GW2 == EGW2(grundsteuer_obj)
        assert result.xml_attr_version == "2"
        assert result.xml_attr_xmlns == "http://finkonsens.de/elster/elstererklaerung/grundsteuerwert/e88/v2"
        assert len(vars(result)) == 5


class TestEGrundsteuerData:
    def test_attributes_set_correctly(self):
        grundsteuer_obj = get_grundsteuer_sample_data()

        result = EGrundsteuerData(grundsteuer_obj)

        assert result.E88 == EGrundsteuerSpecifics(grundsteuer_obj)
        assert len(vars(result)) == 1


class TestGetFullGrundsteuerDataRepresentation:
    def test_returns_full_xml_including_grundsteuer_object(self):
        grundsteuer_obj = get_grundsteuer_sample_data()

        result = get_full_grundsteuer_data_representation(grundsteuer_obj)

        assert len(vars(result)) == 1
        assert isinstance(result, EXml)
        assert result.Elster.DatenTeil.Nutzdatenblock.Nutzdaten == EGrundsteuerData(grundsteuer_obj)

    def test_sets_empfaenger_data_correctly(self):
        grundsteuer_obj = get_grundsteuer_sample_data()

        result = get_full_grundsteuer_data_representation(grundsteuer_obj)
        empfaenger_result = result.Elster.DatenTeil.Nutzdatenblock.NutzdatenHeader.Empfaenger
        assert empfaenger_result.xml_attr_id == "F"
        # TODO assert empfaenger_result.xml_text == get_bufa_nr(...)

    def test_sets_nutzdaten_header_version_correctly(self):
        grundsteuer_obj = get_grundsteuer_sample_data()

        result = get_full_grundsteuer_data_representation(grundsteuer_obj)
        assert result.Elster.DatenTeil.Nutzdatenblock.NutzdatenHeader.xml_attr_version == "11"

    def test_returns_an_object_convertable_to_valid_xml(self):
        grundsteuer_obj = get_grundsteuer_sample_data()
        resulting_object = get_full_grundsteuer_data_representation(grundsteuer_obj)
        resulting_xml = convert_object_to_xml(resulting_object)
        try:
            ElementTree.fromstring(resulting_xml)
        except ElementTree.ParseError as e:
            return pytest.fail("Did not result in a valid xml: \n" + e.msg)
