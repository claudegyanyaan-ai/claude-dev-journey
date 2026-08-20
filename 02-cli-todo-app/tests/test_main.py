import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import main


class TestAddTask(unittest.TestCase):
    def setUp(self):
        # Point the app at a throwaway file instead of the real tasks.json
        self.test_file = os.path.join(os.path.dirname(__file__), "test_tasks.json")
        main.TASKS_FILE = self.test_file

    def tearDown(self):
        # Clean up the throwaway file after the test runs
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_saves_to_file(self):
        main.add_task("test task")
        tasks = main.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["task"], "test task")
        self.assertFalse(tasks[0]["done"])


if __name__ == "__main__":
    unittest.main()