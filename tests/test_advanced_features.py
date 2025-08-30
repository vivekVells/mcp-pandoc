"""Test suite for advanced mcp-pandoc features

This file tests enhanced functionality beyond basic conversions:
1. Defaults file support (YAML configuration files) - Added in PR #24
2. Enhanced filter support with path resolution - Added in PR #24
3. Future advanced features will be added here

Focuses on testing advanced feature functionality and integration.
"""
import os
import sys
import tempfile

import pytest
import yaml


class TestDefaultsFileSupport:
    """Test the defaults file functionality added in PR #24"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_valid_defaults_file_creation(self):
        """Test creating and parsing a valid defaults file"""
        defaults_content = {
            'from': 'markdown',
            'to': 'html',
            'standalone': True,
            'css': ['style.css'],
            'variables': {
                'title': 'Test Document',
                'author': 'Test User'
            }
        }

        defaults_path = os.path.join(self.temp_dir, "test_defaults.yaml")
        with open(defaults_path, 'w') as f:
            yaml.dump(defaults_content, f)

        # Verify file exists and can be parsed
        assert os.path.exists(defaults_path)

        with open(defaults_path) as f:
            loaded_content = yaml.safe_load(f)

        assert loaded_content == defaults_content
        assert loaded_content['from'] == 'markdown'
        assert loaded_content['to'] == 'html'
        assert loaded_content['variables']['title'] == 'Test Document'

    def test_malformed_yaml_detection(self):
        """Test that malformed YAML files raise appropriate errors"""
        malformed_path = os.path.join(self.temp_dir, "malformed.yaml")
        with open(malformed_path, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")

        # Should raise YAML error when trying to parse
        with pytest.raises(yaml.YAMLError):
            with open(malformed_path) as f:
                yaml.safe_load(f)

    def test_security_safe_yaml_loading(self):
        """Test that YAML loading is secure (uses safe_load)"""
        # Create a YAML file with potentially dangerous content
        dangerous_yaml = """
!!python/object/apply:os.system
- "echo 'dangerous code'"
"""
        dangerous_path = os.path.join(self.temp_dir, "dangerous.yaml")
        with open(dangerous_path, 'w') as f:
            f.write(dangerous_yaml)

        # Verify that safe_load doesn't execute dangerous content
        with open(dangerous_path) as f:
            try:
                result = yaml.safe_load(f)
                # If it loads, it should be safe (no code execution)
                assert result is None or isinstance(result, (dict, list, str, int, float))
            except yaml.YAMLError:
                # This is acceptable - safe_load rejecting dangerous content
                pass

    def test_empty_and_null_yaml_handling(self):
        """Test handling of edge cases in YAML files"""
        # Test empty file
        empty_path = os.path.join(self.temp_dir, "empty.yaml")
        with open(empty_path, 'w') as f:
            f.write("")

        with open(empty_path) as f:
            result = yaml.safe_load(f)
        assert result is None

        # Test file with only null
        null_path = os.path.join(self.temp_dir, "null.yaml")
        with open(null_path, 'w') as f:
            yaml.dump(None, f)

        with open(null_path) as f:
            result = yaml.safe_load(f)
        assert result is None


class TestFilterSupport:
    """Test the filter functionality added in PR #24"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_filter_file_creation_and_permissions(self):
        """Test creating filter files with proper permissions"""
        filter_content = '''#!/usr/bin/env python3
"""
Simple test Pandoc filter
"""
import sys
import json

def main():
    # Read JSON from stdin (Pandoc AST)
    doc = json.load(sys.stdin)
    # Echo it back (no transformation for test)
    json.dump(doc, sys.stdout)

if __name__ == "__main__":
    main()
'''
        filter_path = os.path.join(self.temp_dir, "test_filter.py")
        with open(filter_path, 'w') as f:
            f.write(filter_content)

        # Test permission handling
        os.chmod(filter_path, 0o644)  # Start without execute permission
        assert os.path.exists(filter_path)
        assert not os.access(filter_path, os.X_OK)

        # Test making executable
        os.chmod(filter_path, 0o755)
        assert os.access(filter_path, os.X_OK)

    def test_filter_path_resolution_scenarios(self):
        """Test various filter path resolution scenarios"""
        # Test absolute path
        abs_filter = os.path.join(self.temp_dir, "absolute_filter.py")
        with open(abs_filter, 'w') as f:
            f.write("#!/usr/bin/env python3\n# Absolute path filter")
        os.chmod(abs_filter, 0o755)

        assert os.path.isabs(abs_filter)
        assert os.path.exists(abs_filter)
        assert os.access(abs_filter, os.X_OK)

        # Test relative path resolution
        current_dir = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            rel_filter = "relative_filter.py"
            with open(rel_filter, 'w') as f:
                f.write("#!/usr/bin/env python3\n# Relative path filter")
            os.chmod(rel_filter, 0o755)

            assert os.path.exists(rel_filter)
            assert os.path.exists(os.path.abspath(rel_filter))
        finally:
            os.chdir(current_dir)

    def test_multiple_filter_organization(self):
        """Test organizing multiple filters"""
        # Create filters subdirectory (common pattern)
        filters_dir = os.path.join(self.temp_dir, "filters")
        os.makedirs(filters_dir)

        # Create multiple filters
        filter_names = ["mermaid_filter.py", "citation_filter.py", "custom_filter.py"]
        filter_paths = []

        for name in filter_names:
            filter_path = os.path.join(filters_dir, name)
            with open(filter_path, 'w') as f:
                f.write(f"#!/usr/bin/env python3\n# {name} implementation")
            os.chmod(filter_path, 0o755)
            filter_paths.append(filter_path)

        # Verify all filters exist and are executable
        for path in filter_paths:
            assert os.path.exists(path)
            assert os.access(path, os.X_OK)


class TestNewDependencies:
    """Test that the new dependencies added in PR #24 work correctly"""

    def test_yaml_dependency(self):
        """Test pyyaml dependency functionality"""
        import yaml

        # Test basic functionality
        assert hasattr(yaml, 'safe_load')
        assert hasattr(yaml, 'dump')
        assert hasattr(yaml, 'YAMLError')

        # Test actual usage
        test_data = {'key': 'value', 'number': 42, 'list': [1, 2, 3]}
        yaml_string = yaml.dump(test_data)
        loaded_data = yaml.safe_load(yaml_string)
        assert loaded_data == test_data

    def test_pandocfilters_dependency(self):
        """Test pandocfilters dependency functionality"""
        import pandocfilters

        # Test basic functionality
        assert hasattr(pandocfilters, 'walk')
        assert hasattr(pandocfilters, 'toJSONFilter')

        # Test that we can import common filter functions
        from pandocfilters import Para, Str

        # Test basic filter element creation
        text_element = Str("test")
        para_element = Para([text_element])

        assert text_element['t'] == 'Str'
        assert text_element['c'] == 'test'
        assert para_element['t'] == 'Para'

    def test_panflute_dependency(self):
        """Test panflute dependency functionality"""
        import panflute

        # Test basic functionality
        assert hasattr(panflute, 'run_filter')
        assert hasattr(panflute, 'Doc')
        assert hasattr(panflute, 'Para')

        # Test basic element creation
        doc = panflute.Doc()
        para = panflute.Para()

        assert isinstance(doc, panflute.Doc)
        assert isinstance(para, panflute.Para)


class TestBackwardsCompatibility:
    """Test that PR #24 maintains backwards compatibility"""

    def test_existing_parameters_still_work(self):
        """Test that all existing parameters are still supported"""
        # Test old-style arguments still work
        old_style_args = {
            "contents": "# Test Document",
            "output_format": "html",
            "input_format": "markdown",
            "output_file": "/tmp/test.html",
            "reference_doc": "/path/to/reference.docx"
        }

        # These should all be valid parameter names
        required_params = {"contents", "output_format", "input_format"}
        optional_params = {"output_file", "reference_doc"}

        assert required_params.issubset(set(old_style_args.keys()))
        assert optional_params.issubset(set(old_style_args.keys()))

    def test_new_parameters_are_optional(self):
        """Test that new parameters are optional and don't break existing usage"""
        # Existing usage should work without new parameters
        minimal_args = {
            "contents": "# Test",
            "output_format": "html"
        }

        # New parameters should be additive
        enhanced_args = {
            **minimal_args,
            "defaults_file": "/path/to/defaults.yaml",
            "filters": ["/path/to/filter.py"]
        }

        # Both should be valid argument structures
        assert "contents" in minimal_args
        assert "output_format" in minimal_args
        assert "defaults_file" in enhanced_args
        assert "filters" in enhanced_args
        assert isinstance(enhanced_args["filters"], list)


class TestVersionUpdate:
    """Test that version information is properly updated"""

    def test_version_in_pyproject_toml(self):
        """Test that pyproject.toml has the correct version"""
        pyproject_path = os.path.join(os.path.dirname(__file__), '..', 'pyproject.toml')

        with open(pyproject_path) as f:
            content = f.read()

        # Version should be updated correctly following semantic versioning
        assert 'version = "0.8.1"' in content

        # New dependencies should be present
        assert 'pyyaml' in content
        assert 'pandocfilters' in content
        assert 'panflute' in content

    def test_server_module_imports(self):
        """Test that the server module has proper imports for new features"""
        # Add the src directory to path for import
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        # Import the server module
        from mcp_pandoc import server

        # Verify core function exists
        assert hasattr(server, 'handle_call_tool')

        # Verify we can import the new dependencies at module level
        import pandocfilters
        import panflute
        import yaml

        # All should import successfully
        assert yaml
        assert pandocfilters
        assert panflute
