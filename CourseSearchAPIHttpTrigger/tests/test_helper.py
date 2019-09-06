import unittest
import os
import sys
import inspect

CURRENTDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PARENTDIR = os.path.dirname(CURRENTDIR)
sys.path.insert(0, PARENTDIR)

from helper import remove_conjunctions


class TestRemoveConjunctions(unittest.TestCase):
    def test_when_searchable_field_is_empty_string(self):

        output_result = remove_conjunctions("")
        self.assertEqual("", output_result)

    def test_when_searchable_field_has_ampersand_conjunction(self):
        input_field = "Mathematics & Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_And_conjunction(self):
        input_field = "Mathematics And Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_and_conjunction(self):
        input_field = "Mathematics and Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_For_conjunction(self):
        input_field = "Mathematics For Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_for_conjunction(self):
        input_field = "Mathematics for Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_In_conjunction(self):
        input_field = "Mathematics In Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_in_conjunction(self):
        input_field = "Mathematics in Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_The_conjunction(self):
        input_field = "Mathematics The Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_the_conjunction(self):
        input_field = "Mathematics the Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_With_conjunction(self):
        input_field = "Mathematics With Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_with_conjunction(self):
        input_field = "Mathematics with Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_multiple_conjunctions(self):
        input_field = "The Mathematics with Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)

    def test_when_searchable_field_has_uppercase_conjunction(self):
        input_field = "Mathematics WITH Physics"
        expected_result = "Mathematics Physics"

        output_result = remove_conjunctions(input_field)
        self.assertEqual(expected_result, output_result)
