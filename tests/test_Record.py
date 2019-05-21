# Testing class dtypes.RedcapProject

import os
import sys
import pytest

sys.path.insert(
    0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)

from scred.dtypes import Record, RecordSet, DataDictionary
from . import testdata

def _setup_stored_datadict_and_record():
    stored_datadict = DataDictionary(
        testdata.get_stored_neurogap_datadictionary_response()
    )
    # stored_record_response has all observations; take 0th so we can
    # work on an individual record instead of a recordset
    stored_record = Record(
        id_key="subjid",
        data=testdata.get_stored_neurogap_record_response()[0],
    )
    return (stored_datadict, stored_record)

# ---------------------------------------------------

def test_create_Record_from_fake_data():
    record_data = testdata.get_fake_record_dict()
    record = Record(id_key="idvar", data=record_data)
    assert record.id == "ABC12345678"
    assert record.loc["Var1", "response"] == False
    assert record.loc["Var10", "response"] == 1
    with pytest.raises(KeyError):
        record.loc["VarNotReal", "response"]


def test_record_transfers_logic_to_exported_checkbox_variables():
    stored_datadict, stored_record = _setup_stored_datadict_and_record()
    stored_record.add_branching_logic(stored_datadict)
    # TODO: Add assertions
    # assert stored_record


def test_record_backfill_na_values_with_practice_data():
    stored_datadict, stored_record = _setup_stored_datadict_and_record()
    stored_record.add_branching_logic(stored_datadict)
    stored_record._fill_na_values(stored_datadict)
    assert stored_record.loc["organic_cause_other", "response"] == -555
    assert stored_record.loc["psychosis_primary", "response"] == ""
    assert stored_record.loc["is_case", "response"] == '0' # Becomes num later


def test_record_backfill_missing_values_with_practice_data():
    stored_datadict, stored_record = _setup_stored_datadict_and_record()
    stored_record.add_branching_logic(stored_datadict)
    stored_record._fill_na_values(stored_datadict)
    stored_record._fill_bad_data()
    assert stored_record.loc["psychosis_primary", "response"] == -444


def test_record_fill_bad_data_raises_error_if_not_nafilled():
    stored_datadict, stored_record = _setup_stored_datadict_and_record()
    stored_record.add_branching_logic(stored_datadict)
    with pytest.raises(AttributeError):
        stored_record._fill_bad_data()

def test_record_fill_missing_converts_to_numeric():
    stored_datadict, stored_record = _setup_stored_datadict_and_record()
    stored_record.add_branching_logic(stored_datadict)
    assert stored_record.loc["is_case", "response"] == '0'
    stored_record.fill_missing(stored_datadict)
    assert stored_record.loc["is_case", "response"] == 0

# Testing class dtypes.RecordSet

def test_create_empty_RecordSet_raises_TypeError():
    with pytest.raises(TypeError):
        RecordSet()
