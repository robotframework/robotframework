import unittest

from robot.utils.htmlformatters import LinkFormatter


class TestLinkFormatter(unittest.TestCase):

    def setUp(self):
        self.formatter = LinkFormatter()

    def test_format_link(self):
        result = self.formatter.format_link('Robot Good!')
        self.assertEqual(result, 'Robot Good!')

    def test_format_link_url_image(self):
        for ext in ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'PNG'):
            result = self.formatter.format_link('Robot -> [doc/images/robot.%s|robot] Good!' % ext)
            self.assertEqual(result, 'Robot -> <img src="doc/images/robot.%s" title="robot"> Good!' % ext)

    def test_format_base64_image_link(self):
        result = self.formatter.format_link('[data:image/png;base64,oooxxx=|Robot rocks!]')
        self.assertEqual(result, '<img src="data:image/png;base64,oooxxx=" title="Robot rocks!">')

    def test_format_base64_image_content(self):
        result = self.formatter.format_link('[robot.html|data:image/png;base64,oooxxx=]')
        self.assertEqual(result, '<a href="robot.html"><img src="data:image/png;base64,oooxxx=" title="robot.html"></a>')

    def test_format_base64_image_link_and_content(self):
        result = self.formatter.format_link('[image.jpg|data:image/png;base64,oooxxx=]')
        self.assertEqual(result, '<a href="image.jpg"><img src="data:image/png;base64,oooxxx=" title="image.jpg"></a>')


if __name__ == '__main__':
    unittest.main()
