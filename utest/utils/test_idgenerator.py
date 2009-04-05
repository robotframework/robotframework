import unittest
import os.path

from robot.utils.asserts import *

from robot.utils.idgenerator import IdGenerator, FileNameGenerator


class TestIdAndFileNameGenerators(unittest.TestCase):
    
    def test_id_generator_no_args(self):
        gen = IdGenerator()
        for i in range(1, 101):
            assert_equals(gen.get_id(), '%06d' % i)
        
    def test_id_generator_with_args(self):
        gen = IdGenerator()
        assert_equals(gen.get_id('foo'), 'foo000001')
        assert_equals(gen.get_id('bar'), 'bar000001')
        assert_equals(gen.get_id('bar'), 'bar000002')
        assert_equals(gen.get_id('bar'), 'bar000003')
        assert_equals(gen.get_id('foo'), 'foo000002')
        assert_equals(gen.get_id('bar'), 'bar000004')
        
    def test_id_generator_with_custom_padding(self):
        gen1 = IdGenerator(1)
        gen2 = IdGenerator(2)
        gen10 = IdGenerator(10)
        for i in range(1, 101):
            assert_equals(gen1.get_id(), '%d' % i)
            assert_equals(gen2.get_id('foo'), 'foo%02d' % i)
            assert_equals(gen10.get_id(), '%010d' % i)

    def test_file_name_generator(self):
        gen1 = FileNameGenerator('myname.ext')
        gen2 = FileNameGenerator('my.name.extension')
        gen3 = FileNameGenerator('myname-200709061549')
        for i in range(1, 101):
            assert_equals(gen1.get_name(), 'myname-%03d.ext' % i)
            assert_equals(gen2.get_name(), 'my.name-%03d.extension' % i)
            assert_equals(gen3.get_name(), 'myname-200709061549-%03d' % i)
        
    def test_file_name_generator_with_path(self):
        gen = FileNameGenerator(os.path.join('path','to','file.ext'))
        for i in range(1, 101):
            exp = os.path.join('path','to','file-%03d.ext' % i)
            assert_equals(gen.get_name(), exp)
        
        
if __name__ == '__main__':
    unittest.main()
