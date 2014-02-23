from nose.tools import *
from app import util
from test.base import BaseTestCase, assert_obj_subset

class UtilTestCase(BaseTestCase):

    def test_str_to_url(self):
        eq_(util.str_to_url('Remi'), 'remi')
        eq_(util.str_to_url('Remi Gagne'), 'remi_gagne')
        eq_(util.str_to_url('0Remi'), '0remi')
        eq_(util.str_to_url('*$#()*&Remi_*((*&$Foo'), 'remi_foo')
        eq_(util.str_to_url('   Remi   '), 'remi')

