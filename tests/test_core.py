import unittest
from prompts.loader import load_system_prompt

class TestCoreFunctions(unittest.TestCase):
    def test_prompt_loader(self):
        """测试提示词加载是否正常"""
        prompt = load_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)
        
    def test_file_structure(self):
        """测试必要目录是否存在"""
        import os
        self.assertTrue(os.path.exists('web_interface'))
        self.assertTrue(os.path.exists('static'))

if __name__ == '__main__':
    unittest.main()