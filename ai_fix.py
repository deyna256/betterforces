# AI-generated fix (fallback):
```diff
PR: Add tests for AbandonedProblemsService, Closes #8

diff --git a/backend/domain/services/test_abandoned_problems_service.py b/backend/domain/services/test_abandoned_problems_service.py
new file mode 100644
index 0000000..c8befe4
--- /dev/null
+++ b/backend/domain/services/test_abandoned_problems_service.py
@@ -0,0 +1,24 @@
+import unittest
+from unittest.mock import Mock
+from backend.domain.services.abandoned_problems_service import AbandonedProblemsService
+
+class TestAbandonedProblemsService(unittest.TestCase):
+    def setUp(self):
+        self.service = AbandonedProblemsService()
+
+    def test_analyze_abandoned_problems_no_attempts(self):
+        # Arrange
+        user = Mock(attempts=[])
+        # Act
+        result = self.service.analyze_abandoned_problems(user)
+        # Assert
+        self.assertEqual(result, [])
+
+    def test_analyze_abandoned_problems_multiple_attempts(self):
+        # Arrange
+        user = Mock(attempts=[Mock(problem='problem1'), Mock(problem='problem2')])
+        # Act
+        result = self.service.analyze_abandoned_problems(user)
+        # Assert
+        self.assertEqual(len(result), 2)
```
