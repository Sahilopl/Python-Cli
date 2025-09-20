"""
Test Suite for Python Command Terminal
Tests both CLI and Web interface functionality
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import CommandTerminal
    from cli_terminal import CLITerminal
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")

class TestCommandTerminal(unittest.TestCase):
    """Test the web terminal backend"""
    
    def setUp(self):
        """Set up test environment"""
        self.terminal = CommandTerminal()
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = self.terminal.current_dir
        self.terminal.current_dir = self.test_dir
    
    def tearDown(self):
        """Clean up test environment"""
        self.terminal.current_dir = self.original_dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_pwd_command(self):
        """Test pwd command"""
        result = self.terminal.execute_command('pwd')
        self.assertEqual(result, self.test_dir)
    
    def test_mkdir_command(self):
        """Test mkdir command"""
        result = self.terminal.execute_command('mkdir testdir')
        self.assertIn('created successfully', result)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'testdir')))
    
    def test_ls_command(self):
        """Test ls command"""
        # Create test files
        test_file = os.path.join(self.test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        result = self.terminal.execute_command('ls')
        self.assertIsInstance(result, str)
        self.assertIn('test.txt', result)
    
    def test_cd_command(self):
        """Test cd command"""
        # Create test directory
        test_subdir = os.path.join(self.test_dir, 'subdir')
        os.mkdir(test_subdir)
        
        result = self.terminal.execute_command('cd subdir')
        self.assertIn('Changed directory', result)
        self.assertEqual(self.terminal.current_dir, test_subdir)
    
    def test_invalid_command(self):
        """Test invalid command handling"""
        result = self.terminal.execute_command('invalidcommand')
        # Should either execute as system command or return error
        self.assertIsInstance(result, str)
    
    def test_natural_language_parsing(self):
        """Test natural language command parsing"""
        # Test create folder
        parsed = self.terminal.parse_natural_language('create folder mytest')
        self.assertEqual(parsed, 'mkdir mytest')
        
        # Test list files
        parsed = self.terminal.parse_natural_language('list files')
        self.assertEqual(parsed, 'ls')
        
        # Test change directory
        parsed = self.terminal.parse_natural_language('go to documents')
        self.assertEqual(parsed, 'cd documents')
    
    def test_system_info(self):
        """Test system info retrieval"""
        info = self.terminal.get_system_info()
        self.assertIn('platform', info)
        self.assertIn('python_version', info)
        self.assertIsInstance(info['platform'], str)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_system_monitoring(self, mock_disk, mock_memory, mock_cpu):
        """Test system monitoring"""
        # Mock system data
        mock_cpu.return_value = 25.5
        mock_memory.return_value = MagicMock(
            total=8000000000, used=4000000000, 
            available=4000000000, percent=50.0
        )
        mock_disk.return_value = MagicMock(
            total=500000000000, used=250000000000, 
            free=250000000000
        )
        
        result = self.terminal.get_system_monitoring()
        self.assertIsInstance(result, dict)
        self.assertIn('cpu_percent', result)
        self.assertIn('memory', result)
        self.assertIn('disk', result)
    
    def test_command_history(self):
        """Test command history functionality"""
        # Execute some commands
        self.terminal.execute_command('pwd')
        self.terminal.execute_command('ls')
        
        # Check history
        self.assertEqual(len(self.terminal.command_history), 2)
        self.assertEqual(self.terminal.command_history[0]['command'], 'pwd')
        self.assertEqual(self.terminal.command_history[1]['command'], 'ls')
    
    def test_dangerous_command_blocking(self):
        """Test that dangerous commands are blocked"""
        result = self.terminal.execute_system_command('rm -rf /')
        self.assertIn('not allowed for security', result)
        
        result = self.terminal.execute_system_command('format c:')
        self.assertIn('not allowed for security', result)

class TestCLITerminal(unittest.TestCase):
    """Test the CLI terminal"""
    
    def setUp(self):
        """Set up test environment"""
        self.terminal = CLITerminal()
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = self.terminal.current_dir
        self.terminal.current_dir = self.test_dir
    
    def tearDown(self):
        """Clean up test environment"""
        self.terminal.current_dir = self.original_dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_directory_operations(self):
        """Test directory operations in CLI"""
        # Test mkdir
        result = self.terminal.execute_command('mkdir testdir')
        self.assertIn('created successfully', result)
        
        # Test cd
        result = self.terminal.execute_command('cd testdir')
        self.assertIn('Changed directory', result)
        
        # Test pwd
        result = self.terminal.execute_command('pwd')
        self.assertIn('testdir', result)
    
    def test_file_listing(self):
        """Test file listing in CLI"""
        # Create test file
        test_file = os.path.join(self.test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        result = self.terminal.execute_command('ls')
        self.assertIn('test.txt', result)
    
    def test_help_command(self):
        """Test help command"""
        result = self.terminal.execute_command('help')
        self.assertIn('AVAILABLE COMMANDS', result)
        self.assertIn('pwd', result)
        self.assertIn('cd', result)
    
    def test_natural_language_cli(self):
        """Test natural language in CLI"""
        result = self.terminal.execute_command('create folder mynewdir')
        self.assertIn('created successfully', result)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'mynewdir')))

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_flask_app_creation(self):
        """Test that Flask app can be created"""
        try:
            from app import app
            self.assertIsNotNone(app)
            self.assertEqual(app.name, 'app')
        except ImportError:
            self.skipTest("Flask not available")
    
    def test_file_structure(self):
        """Test that all required files exist"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        required_files = [
            'app.py',
            'cli_terminal.py',
            'launcher.py',
            'requirements.txt',
            'README.md',
            'templates/index.html'
        ]
        
        for file_path in required_files:
            full_path = os.path.join(base_dir, file_path)
            self.assertTrue(os.path.exists(full_path), f"Missing required file: {file_path}")
    
    def test_requirements_file(self):
        """Test that requirements.txt contains necessary packages"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        req_file = os.path.join(base_dir, 'requirements.txt')
        
        with open(req_file, 'r') as f:
            requirements = f.read()
        
        required_packages = ['Flask', 'psutil']
        for package in required_packages:
            self.assertIn(package, requirements)

class TestNaturalLanguageProcessing(unittest.TestCase):
    """Test natural language processing capabilities"""
    
    def setUp(self):
        self.terminal = CommandTerminal()
    
    def test_create_folder_patterns(self):
        """Test various create folder patterns"""
        test_cases = [
            ('create folder mydir', 'mkdir mydir'),
            ('make directory testdir', 'mkdir testdir'),
            ('mkdir newdir', 'mkdir newdir')
        ]
        
        for input_cmd, expected in test_cases:
            result = self.terminal.parse_natural_language(input_cmd)
            self.assertEqual(result, expected)
    
    def test_list_patterns(self):
        """Test various list patterns"""
        test_cases = [
            'list files',
            'show files',
            'list directory',
            'show contents'
        ]
        
        for input_cmd in test_cases:
            result = self.terminal.parse_natural_language(input_cmd)
            self.assertEqual(result, 'ls')
    
    def test_navigation_patterns(self):
        """Test navigation patterns"""
        test_cases = [
            ('go to documents', 'cd documents'),
            ('change to desktop', 'cd desktop'),
            ('cd home', 'cd home')
        ]
        
        for input_cmd, expected in test_cases:
            result = self.terminal.parse_natural_language(input_cmd)
            self.assertEqual(result, expected)

def run_performance_tests():
    """Run basic performance tests"""
    import time
    
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    
    terminal = CommandTerminal()
    
    # Test command execution speed
    start_time = time.time()
    for i in range(100):
        terminal.execute_command('pwd')
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    print(f"Average command execution time: {avg_time:.4f} seconds")
    
    # Test system monitoring speed
    start_time = time.time()
    for i in range(10):
        try:
            terminal.get_system_monitoring()
        except:
            pass
    end_time = time.time()
    
    avg_monitor_time = (end_time - start_time) / 10
    print(f"Average system monitoring time: {avg_monitor_time:.4f} seconds")
    
    # Test natural language processing speed
    start_time = time.time()
    for i in range(1000):
        terminal.parse_natural_language('create folder test')
    end_time = time.time()
    
    avg_nlp_time = (end_time - start_time) / 1000
    print(f"Average NLP processing time: {avg_nlp_time:.6f} seconds")

def main():
    """Main test runner"""
    print("🧪 Running Python Command Terminal Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestCommandTerminal,
        TestCLITerminal,
        TestIntegration,
        TestNaturalLanguageProcessing
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run performance tests
    try:
        run_performance_tests()
    except Exception as e:
        print(f"Performance tests failed: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("✅ Test suite passed!")
        return 0
    else:
        print("❌ Test suite failed!")
        return 1

if __name__ == "__main__":
    exit(main())
