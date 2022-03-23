from erica.erica_legacy.elster_xml.common.elsterify_fields import elsterify_anrede, elsterify_date
from erica.erica_legacy.elster_xml.grundsteuer.elster_eigentuemer import EAnteil, EGesetzlicherVertreter, EPersonData, \
    EEigentumsverh, EEmpfangsbevollmaechtigter
from erica.erica_legacy.request_processing.erica_input.v2.grundsteuer_input_eigentuemer import Anteil, Eigentuemer
from tests.erica_legacy.samples.grundsteuer_sample_data import SampleVertreter, SampleBevollmaechtigter, SamplePerson, \
    SampleEigentuemer


class TestEAnteil:
    def test_attributes_set_correctly(self):
        anteil_obj = Anteil.parse_obj({'zaehler': '1', 'nenner': '2'})

        result = EAnteil(anteil_obj)

        assert result.E7404570 == anteil_obj.zaehler
        assert result.E7404571 == anteil_obj.nenner


class TestEGesetzlicherVertreter:
    def test_attributes_set_correctly(self):
        full_vertreter_obj = SampleVertreter().complete().parse()

        result = EGesetzlicherVertreter(full_vertreter_obj)

        assert result.E7415101 == elsterify_anrede(full_vertreter_obj.name.anrede)
        assert result.E7415102 == full_vertreter_obj.name.titel
        assert result.E7415201 == full_vertreter_obj.name.vorname
        assert result.E7415301 == full_vertreter_obj.name.name
        assert result.E7415401 == full_vertreter_obj.adresse.strasse
        assert result.E7415501 == full_vertreter_obj.adresse.hausnummer
        assert result.E7415502 == full_vertreter_obj.adresse.hausnummerzusatz
        assert result.E7415601 == full_vertreter_obj.adresse.plz
        assert result.E7415602 == full_vertreter_obj.adresse.postfach
        assert result.E7415603 == full_vertreter_obj.adresse.ort
        assert result.E7415604 == full_vertreter_obj.telefonnummer.telefonnummer
        assert len(vars(result)) == 11

    def test_if_all_optional_attributes_not_given_then_attributes_set_correctly(self):
        vertreter_obj = SampleVertreter().parse()

        result = EGesetzlicherVertreter(vertreter_obj)

        assert result.E7415101 == elsterify_anrede(vertreter_obj.name.anrede)
        assert result.E7415102 is None
        assert result.E7415201 == vertreter_obj.name.vorname
        assert result.E7415301 == vertreter_obj.name.name
        assert result.E7415401 is None
        assert result.E7415501 is None
        assert result.E7415502 is None
        assert result.E7415601 == vertreter_obj.adresse.plz
        assert result.E7415602 is None
        assert result.E7415603 == vertreter_obj.adresse.ort
        assert result.E7415604 is None
        assert len(vars(result)) == 11


class TestEPersonData:
    def test_attributes_set_correctly(self):
        person_obj = SamplePerson().with_telefonnummer().with_vertreter().parse()
        person_index = 2

        result = EPersonData(person_obj, person_index)

        assert result.Beteiligter == person_index + 1
        assert result.E7404510 == elsterify_anrede(person_obj.persoenlicheAngaben.anrede)
        assert result.E7404514 == person_obj.persoenlicheAngaben.titel
        assert result.E7404518 == elsterify_date(person_obj.persoenlicheAngaben.geburtsdatum)
        assert result.E7404513 == person_obj.persoenlicheAngaben.vorname
        assert result.E7404511 == person_obj.persoenlicheAngaben.name
        assert result.E7404524 == person_obj.adresse.strasse
        assert result.E7404525 == person_obj.adresse.hausnummer
        assert result.E7404526 == person_obj.adresse.hausnummerzusatz
        assert result.E7404540 == person_obj.adresse.plz
        assert result.E7404527 == person_obj.adresse.postfach
        assert result.E7404522 == person_obj.adresse.ort
        assert result.E7414601 == person_obj.telefonnummer.telefonnummer
        assert result.E7404519 == person_obj.steuer_id.steuer_id
        assert result.Anteil == EAnteil(person_obj.anteil)
        assert result.Ges_Vertreter == EGesetzlicherVertreter(person_obj.vertreter)
        assert len(vars(result)) == 16

    def test_if_all_optional_attributes_not_given_then_attributes_set_correctly(self):
        person_obj = SamplePerson().parse()
        person_index = 2

        result = EPersonData(person_obj, person_index)

        assert result.Beteiligter == person_index + 1
        assert result.E7404510 == elsterify_anrede(person_obj.persoenlicheAngaben.anrede)
        assert result.E7404514 is None
        assert result.E7404518 is None
        assert result.E7404513 == person_obj.persoenlicheAngaben.vorname
        assert result.E7404511 == person_obj.persoenlicheAngaben.name
        assert result.E7404524 is None
        assert result.E7404525 is None
        assert result.E7404526 is None
        assert result.E7404540 == person_obj.adresse.plz
        assert result.E7404527 is None
        assert result.E7404522 == person_obj.adresse.ort
        assert result.E7414601 is None
        assert result.E7404519 == person_obj.steuer_id.steuer_id
        assert result.Anteil == EAnteil(person_obj.anteil)
        assert result.Ges_Vertreter is None
        assert len(vars(result)) == 16

    def test_if_part_of_optional_attributes_not_given_then_attributes_set_correctly(self):
        person_obj = SamplePerson().with_vertreter().with_telefonnummer().parse()
        person_obj.persoenlicheAngaben.titel = None
        person_index = 2

        result = EPersonData(person_obj, person_index)

        assert result.Beteiligter == person_index + 1
        assert result.E7404510 == elsterify_anrede(person_obj.persoenlicheAngaben.anrede)
        assert result.E7404514 is None
        assert result.E7404518 == elsterify_date(person_obj.persoenlicheAngaben.geburtsdatum)
        assert result.E7404513 == person_obj.persoenlicheAngaben.vorname
        assert result.E7404511 == person_obj.persoenlicheAngaben.name
        assert result.E7404524 == person_obj.adresse.strasse
        assert result.E7404525 == person_obj.adresse.hausnummer
        assert result.E7404526 == person_obj.adresse.hausnummerzusatz
        assert result.E7404540 == person_obj.adresse.plz
        assert result.E7404527 == person_obj.adresse.postfach
        assert result.E7404522 == person_obj.adresse.ort
        assert result.E7414601 == person_obj.telefonnummer.telefonnummer
        assert result.E7404519 == person_obj.steuer_id.steuer_id
        assert result.Anteil == EAnteil(person_obj.anteil)
        assert result.Ges_Vertreter == EGesetzlicherVertreter(person_obj.vertreter)
        assert len(vars(result)) == 16


class TestEEigentumsverh:
    def test_if_one_person_then_attributes_set_correctly(self):
        person = SamplePerson().parse()
        eigentuemer_obj = Eigentuemer.parse_obj({"person": [person]})

        result = EEigentumsverh(eigentuemer_obj)

        assert result.E7401340 == "0"

    def test_if_two_married_persons_then_attributes_set_correctly(self):
        person1 = SamplePerson().parse()
        person2 = SamplePerson().parse()
        eigentuemer_obj = Eigentuemer.parse_obj(
            {"person": [person1, person2], "verheiratet": {"are_verheiratet": True}})

        result = EEigentumsverh(eigentuemer_obj)

        assert result.E7401340 == "4"

    def test_if_two_not_married_persons_then_attributes_set_correctly(self):
        person1 = SamplePerson().build()
        person2 = SamplePerson().build()
        eigentuemer_obj = SampleEigentuemer().person(person1).person(person2).verheiratet(False).parse()

        result = EEigentumsverh(eigentuemer_obj)

        assert result.E7401340 == "6"

    def test_if_three_persons_then_attributes_set_correctly(self):
        person1 = SamplePerson().build()
        person2 = SamplePerson().build()
        person3 = SamplePerson().build()
        eigentuemer_obj = SampleEigentuemer().person(person1).person(person2).person(person3).parse()

        result = EEigentumsverh(eigentuemer_obj)

        assert result.E7401340 == "6"


class TestEEmpfangsbevollmaechtigter:
    def test_attributes_set_correctly(self):
        input_data = SampleBevollmaechtigter().complete().parse()

        result = EEmpfangsbevollmaechtigter(input_data)

        assert result.E7404610 == elsterify_anrede(input_data.name.anrede)
        assert result.E7404614 == input_data.name.titel
        assert result.E7404613 == input_data.name.vorname
        assert result.E7404611 == input_data.name.name
        assert result.E7404624 == input_data.adresse.strasse
        assert result.E7404625 == input_data.adresse.hausnummer
        assert result.E7404626 == input_data.adresse.hausnummerzusatz
        assert result.E7404640 == input_data.adresse.plz
        assert result.E7404627 == input_data.adresse.postfach
        assert result.E7404622 == input_data.adresse.ort
        assert result.E7412201 == input_data.telefonnummer.telefonnummer
        assert len(vars(result)) == 11

    def test_if_all_optional_attributes_not_given_then_attributes_set_correctly(self):
        input_data = SampleBevollmaechtigter().parse()

        result = EEmpfangsbevollmaechtigter(input_data)

        assert result.E7404610 == elsterify_anrede(input_data.name.anrede)
        assert result.E7404614 is None
        assert result.E7404613 == input_data.name.vorname
        assert result.E7404611 == input_data.name.name
        assert result.E7404624 is None
        assert result.E7404625 is None
        assert result.E7404626 is None
        assert result.E7404640 == input_data.adresse.plz
        assert result.E7404627 is None
        assert result.E7404622 == input_data.adresse.ort
        assert result.E7412201 is None
        assert len(vars(result)) == 11
