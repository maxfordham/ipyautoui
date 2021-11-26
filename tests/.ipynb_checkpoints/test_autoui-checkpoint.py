#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `mfom` package."""

import pytest
import sys
import os
sys.path.append('/mnt/c/engDev/git_mf/mfom')
#  from click.testing import CliRunner
from mfom import Document, Job, DocumentHeader, JobDirs
from mfom.document import DocHeaderReadWrite, DocumentHeaderBase
from pprint import pprint

FDIR_TEST = os.path.join(os.path.dirname(__file__),"test_data")
try:
    os.makedirs(FDIR_TEST)
except:
    pass
FPTH_TEST_DOC_HEADER = os.path.join(FDIR_TEST, "doc_header.json")
FPTH_TEST_DOC_HEADER_SCHEMA = os.path.join(FDIR_TEST,"doc_header_schema.json")
class TestDocument:
    def test_doc_header(self):
        print('+++++++++ test_doc_header +++++++++ ')
        dh = DocumentHeader()
        
        DocHeaderReadWrite.to_json_fpth(dh,fpth=FPTH_TEST_DOC_HEADER)
        dh1 = DocHeaderReadWrite.from_json_fpth(FPTH_TEST_DOC_HEADER)
        assert type(dh1) == DocumentHeader
        assert dh == dh1

    def test_doc_header_schema(self):
        print('+++++++++  test_doc_header_schema +++++++++ ')
        DocHeaderReadWrite.to_json_schema(fpth=FPTH_TEST_DOC_HEADER_SCHEMA)
        assert os.path.isfile(FPTH_TEST_DOC_HEADER_SCHEMA)

    def test_notes_string_validation(self):
        print('+++++++++ test_notes_string_validation +++++++++ ')
        dh = DocumentHeaderBase(notes=['a','b',2])
        for n in dh.notes:
            assert type(n)==str
        #assert [type(n)==str for n in ]
        
    #def test_delete_test_files(self):
    #    print('delete_test_files')
     #   os.remove(FPTH_TEST_DOC_HEADER)
      #  os.remove(FPTH_TEST_DOC_HEADER_SCHEMA)