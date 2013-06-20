import os, unittest, tempfile
import app

class BrickrTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        
    def tearDown(self):
        pass
        
if __name__ == '__main__':
    unittest.main()
