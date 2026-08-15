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
from mcp_pandoc.server import (
    ADVANCED_FORMATS,
    INPUT_FORMATS,
    OUTPUT_FORMATS,
    REFERENCE_DOC_FORMATS,
)


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

    @pytest.mark.skipif(os.name == "nt", reason="Windows has no POSIX execute bit")
    def test_filter_file_posix_execute_permissions(self):
        """Test creating filter files with POSIX execute permissions."""
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

    def test_version_matches_between_pyproject_and_server(self):
        """The packaged version and the version the server advertises must agree.

        They are declared in two separate files, so a bump that updates only one ships a
        server reporting a version that does not match what users installed. Comparing
        them beats asserting a literal, which silently becomes a chore on every release.
        """
        import re

        pyproject_path = os.path.join(os.path.dirname(__file__), '..', 'pyproject.toml')

        with open(pyproject_path) as f:
            content = f.read()

        match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
        assert match, "pyproject.toml has no top-level version field"

        from mcp_pandoc.server import server
        assert server.version == match.group(1)

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


class TestReferenceDocSupport:
    """Test reference_doc validation and styling behaviour.

    Pandoc accepts --reference-doc for docx, odt and pptx. This project exposes it for
    the output formats listed in REFERENCE_DOC_FORMATS, and rejects a reference document
    whose type does not match the requested output format, because pandoc itself does
    not check that and fails silently when it is wrong.
    """

    SENTINEL_FONT = "McpPandocSentinelFont"
    DEFAULT_ODT_FONT = b"Times New Roman"

    def setup_method(self):
        """Create a scratch directory for generated documents."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Remove the scratch directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _path(self, name):
        """Return a path inside this test's scratch directory."""
        return os.path.join(self.temp_dir, name)

    def _make_reference(self, output_format):
        """Generate a minimal, valid reference document for the given output format."""
        import pypandoc

        path = self._path(f"ref.{output_format}")
        pypandoc.convert_text("# Reference", output_format, format="md", outputfile=path)
        return path

    def _make_sentinel_odt_reference(self):
        """Build a reference.odt whose styles.xml carries a unique, detectable font name.

        Asserting only that an output file exists would pass even if --reference-doc were
        silently dropped, since pandoc writes an odt either way. Tagging the reference
        stylesheet lets the test prove the styling actually reached the output.
        """
        import subprocess
        import zipfile

        default_ref = self._path("default_ref.odt")
        with open(default_ref, "wb") as handle:
            subprocess.run(
                ["pandoc", "--print-default-data-file", "reference.odt"],
                stdout=handle,
                check=True,
            )

        sentinel_ref = self._path("sentinel_ref.odt")
        injected = False
        with zipfile.ZipFile(default_ref) as source, zipfile.ZipFile(sentinel_ref, "w") as target:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename == "styles.xml" and self.DEFAULT_ODT_FONT in data:
                    data = data.replace(self.DEFAULT_ODT_FONT, self.SENTINEL_FONT.encode())
                    injected = True
                target.writestr(item, data)

        assert injected, (
            "Could not inject the sentinel font into pandoc's default reference.odt. "
            "The default stylesheet no longer contains "
            f"{self.DEFAULT_ODT_FONT.decode()!r}; update DEFAULT_ODT_FONT."
        )
        return sentinel_ref

    def _styles_xml(self, odt_path):
        """Return the styles.xml bytes from an odt package."""
        import zipfile

        with zipfile.ZipFile(odt_path) as archive:
            return archive.read("styles.xml")

    @pytest.mark.parametrize("output_format", REFERENCE_DOC_FORMATS)
    def test_pandoc_accepts_reference_doc_for_every_supported_format(self, output_format):
        """Every format we advertise must actually accept --reference-doc in pandoc.

        Driven off REFERENCE_DOC_FORMATS so the coverage cannot drift from the allow-list.
        """
        import pypandoc

        reference = self._make_reference(output_format)
        output = self._path(f"out.{output_format}")

        pypandoc.convert_text(
            "# Content",
            output_format,
            format="md",
            outputfile=output,
            extra_args=["--reference-doc", reference],
        )

        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("output_format", REFERENCE_DOC_FORMATS)
    async def test_reference_doc_accepted_end_to_end(self, output_format):
        """Every format in the allow-list must accept reference_doc through the tool itself.

        Parametrized off the constant so a format added to the allow-list without working
        end to end fails here rather than in a user's document.
        """
        from mcp_pandoc.server import handle_call_tool

        reference = self._make_reference(output_format)
        output = self._path(f"out.{output_format}")

        await handle_call_tool(
            "convert-contents",
            {
                "contents": "# Content",
                "output_format": output_format,
                "output_file": output,
                "reference_doc": reference,
            },
        )

        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    @pytest.mark.asyncio
    async def test_reference_doc_styling_reaches_odt_output(self):
        """The reference stylesheet must actually be applied, not merely accepted."""
        from mcp_pandoc.server import handle_call_tool

        sentinel_reference = self._make_sentinel_odt_reference()
        styled = self._path("styled.odt")
        unstyled = self._path("unstyled.odt")

        await handle_call_tool(
            "convert-contents",
            {
                "contents": "# Content",
                "output_format": "odt",
                "output_file": styled,
                "reference_doc": sentinel_reference,
            },
        )
        await handle_call_tool(
            "convert-contents",
            {"contents": "# Content", "output_format": "odt", "output_file": unstyled},
        )

        assert self.SENTINEL_FONT.encode() in self._styles_xml(styled)
        assert self.SENTINEL_FONT.encode() not in self._styles_xml(unstyled)

    @pytest.mark.asyncio
    async def test_reference_doc_rejected_for_unsupported_output_format(self):
        """An unsupported output format is named in the error, alongside the supported ones."""
        from mcp_pandoc.server import handle_call_tool

        reference = self._make_reference("docx")

        with pytest.raises(ValueError) as excinfo:
            await handle_call_tool(
                "convert-contents",
                {"contents": "# Test", "output_format": "html", "reference_doc": reference},
            )

        from mcp_pandoc.server import _join_with_and

        message = str(excinfo.value)
        assert "not supported for 'html'" in message
        assert _join_with_and(REFERENCE_DOC_FORMATS) in message

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("output_format", "reference_format"),
        [("odt", "docx"), ("docx", "odt")],
    )
    async def test_reference_doc_rejected_when_type_does_not_match_output(
        self, output_format, reference_format
    ):
        """A mismatched reference document must be rejected before pandoc sees it.

        Pandoc exits 0 for both of these. A docx reference against odt output writes an
        odt that pandoc itself cannot read back, and an odt reference against docx output
        is discarded silently, producing an unstyled file reported as a success.
        """
        from mcp_pandoc.server import handle_call_tool

        reference = self._make_reference(reference_format)
        output = self._path(f"out.{output_format}")

        with pytest.raises(ValueError) as excinfo:
            await handle_call_tool(
                "convert-contents",
                {
                    "contents": "# Test",
                    "output_format": output_format,
                    "output_file": output,
                    "reference_doc": reference,
                },
            )

        message = str(excinfo.value)
        assert f"must be a '.{output_format}' file" in message
        assert f"ref.{reference_format}" in message
        assert not os.path.exists(output), "no output should be written when validation fails"

    @pytest.mark.asyncio
    async def test_reference_doc_extension_check_is_case_insensitive(self):
        """An uppercase extension is the same format and must be accepted."""
        from mcp_pandoc.server import handle_call_tool

        reference = self._make_reference("odt")
        uppercase_reference = self._path("REF.ODT")
        os.rename(reference, uppercase_reference)
        output = self._path("out.odt")

        await handle_call_tool(
            "convert-contents",
            {
                "contents": "# Content",
                "output_format": "odt",
                "output_file": output,
                "reference_doc": uppercase_reference,
            },
        )

        assert os.path.exists(output)

    @pytest.mark.asyncio
    async def test_reference_doc_rejected_when_path_is_a_directory(self):
        """A directory passes os.path.exists, so it needs its own check."""
        from mcp_pandoc.server import handle_call_tool

        directory = self._path("looks_like.docx")
        os.makedirs(directory)

        with pytest.raises(ValueError) as excinfo:
            await handle_call_tool(
                "convert-contents",
                {
                    "contents": "# Test",
                    "output_format": "docx",
                    "output_file": self._path("out.docx"),
                    "reference_doc": directory,
                },
            )

        assert "is not a file" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_reference_doc_missing_file_is_reported(self):
        """The documented 'Reference document not found' wording must not regress."""
        from mcp_pandoc.server import handle_call_tool

        with pytest.raises(ValueError) as excinfo:
            await handle_call_tool(
                "convert-contents",
                {
                    "contents": "# Test",
                    "output_format": "docx",
                    "output_file": self._path("out.docx"),
                    "reference_doc": self._path("nope.docx"),
                },
            )

        assert "Reference document not found" in str(excinfo.value)


class TestFormatDirectionality:
    """Pandoc reads and writes different sets of formats, and the schema must say so.

    The input and output enums were a single shared list until pptx was exposed. These
    tests exist to stop them being collapsed back together, which would re-advertise
    every writable format as readable.
    """

    def test_input_and_output_lists_differ_only_by_write_only_formats(self):
        """pptx is writable but not readable on the pandoc versions this project supports."""
        assert set(OUTPUT_FORMATS) - set(INPUT_FORMATS) == {"pptx"}
        assert set(INPUT_FORMATS) - set(OUTPUT_FORMATS) == set()

    def test_reference_doc_formats_are_all_writable(self):
        """A styling target that cannot be written would be unreachable."""
        assert set(REFERENCE_DOC_FORMATS) <= set(OUTPUT_FORMATS)

    def test_advanced_formats_are_all_writable(self):
        """An output_file requirement for a format we cannot write would be dead code."""
        assert set(ADVANCED_FORMATS) <= set(OUTPUT_FORMATS)

    @pytest.mark.asyncio
    async def test_schema_enums_are_generated_from_the_constants(self):
        """The advertised schema and the runtime check must not drift apart."""
        from mcp_pandoc.server import handle_list_tools

        tool = (await handle_list_tools())[0]
        properties = tool.input_schema["properties"]

        assert properties["input_format"]["enum"] == list(INPUT_FORMATS)
        assert properties["output_format"]["enum"] == list(OUTPUT_FORMATS)

    @pytest.mark.asyncio
    async def test_pptx_output_works_through_the_client_path(self, tmp_path):
        """A real MCP client must be able to ask for pptx and receive a file.

        Goes through call_tool rather than handle_call_tool, because only call_tool runs
        the JSON-schema validation a client hits first. A test that skipped it would pass
        even with pptx missing from the enum.
        """
        import mcp.types as types
        from mcp_pandoc.server import call_tool

        output = str(tmp_path / "deck.pptx")
        result = await call_tool(
            None,
            types.CallToolRequestParams(
                name="convert-contents",
                arguments={
                    "contents": "# Slide One\n\nBody text.",
                    "output_format": "pptx",
                    "output_file": output,
                },
            ),
        )

        assert result.is_error is False, result.content[0].text
        assert os.path.getsize(output) > 0

    @pytest.mark.asyncio
    async def test_pptx_is_rejected_as_an_input_format(self):
        """The pptx reader arrived in pandoc 3.8.3 and this project declares no floor. See #54."""
        import mcp.types as types
        from mcp_pandoc.server import call_tool

        result = await call_tool(
            None,
            types.CallToolRequestParams(
                name="convert-contents",
                arguments={"contents": "x", "input_format": "pptx", "output_format": "markdown"},
            ),
        )

        assert result.is_error is True
        assert "pptx" in result.content[0].text

    @pytest.mark.asyncio
    @pytest.mark.parametrize("output_format", ["odt", "pptx"])
    async def test_binary_formats_require_an_output_file(self, output_format):
        """Ask for a path up front rather than letting pandoc fail late.

        Without this, odt returned pandoc's own "Output to odt only works by using a
        outputfile", which does not name the parameter the caller has to supply.
        """
        from mcp_pandoc.server import handle_call_tool

        with pytest.raises(ValueError) as excinfo:
            await handle_call_tool(
                "convert-contents",
                {"contents": "# Test", "output_format": output_format},
            )

        assert "output_file path is required" in str(excinfo.value)


class TestPptxOutputRobustness:
    """pptx output must work on every path into the converter, not just inline markdown.

    pptx was the first format added after the input and output enums diverged, so these
    cover the argument-composition paths that a new output format can quietly break:
    a non-default input_format, the input_file branch, filters, and a defaults file.
    """

    def setup_method(self):
        """Create a scratch directory for generated documents."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Remove the scratch directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _path(self, name):
        """Return a path inside this test's scratch directory."""
        return os.path.join(self.temp_dir, name)

    async def _convert(self, arguments):
        """Run a conversion through the client path and return the tool result."""
        import mcp.types as types
        from mcp_pandoc.server import call_tool

        return await call_tool(
            None, types.CallToolRequestParams(name="convert-contents", arguments=arguments)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("input_format", "contents"),
        [
            ("markdown", "# Slide One\n\nBody text.\n\n# Slide Two\n\nMore."),
            ("html", "<h1>Slide One</h1><p>Body text.</p>"),
            ("rst", "Slide One\n=========\n\nBody text.\n"),
        ],
    )
    async def test_pptx_output_from_each_input_format(self, input_format, contents):
        """input_format must be honoured when the target is pptx."""
        output = self._path(f"from_{input_format}.pptx")

        result = await self._convert(
            {
                "contents": contents,
                "input_format": input_format,
                "output_format": "pptx",
                "output_file": output,
            }
        )

        assert result.is_error is False, result.content[0].text
        assert os.path.getsize(output) > 0

    @pytest.mark.asyncio
    async def test_pptx_output_from_an_input_file(self):
        """The input_file branch builds its arguments separately from the contents branch."""
        import pypandoc

        source = self._path("source.docx")
        output = self._path("from_file.pptx")
        pypandoc.convert_text("# Slide\n\nBody.", "docx", format="md", outputfile=source)

        result = await self._convert({"input_file": source, "output_format": "pptx", "output_file": output})

        assert result.is_error is False, result.content[0].text
        assert os.path.getsize(output) > 0

    @pytest.mark.asyncio
    async def test_pptx_output_with_a_filter(self):
        """Filters and the pptx writer must compose in extra_args."""
        filter_path = self._path("passthrough.py")
        with open(filter_path, "w") as handle:
            handle.write("#!/usr/bin/env python3\nimport sys, json\njson.dump(json.load(sys.stdin), sys.stdout)\n")
        os.chmod(filter_path, 0o755)
        output = self._path("filtered.pptx")

        result = await self._convert(
            {
                "contents": "# Slide\n\nBody.",
                "output_format": "pptx",
                "output_file": output,
                "filters": [filter_path],
            }
        )

        assert result.is_error is False, result.content[0].text
        assert os.path.getsize(output) > 0

    @pytest.mark.asyncio
    async def test_pptx_output_with_a_defaults_file(self):
        """A defaults file naming pptx must not conflict with the requested format."""
        defaults_path = self._path("defaults.yaml")
        with open(defaults_path, "w") as handle:
            yaml.dump({"to": "pptx"}, handle)
        output = self._path("with_defaults.pptx")

        result = await self._convert(
            {
                "contents": "# Slide\n\nBody.",
                "output_format": "pptx",
                "output_file": output,
                "defaults_file": defaults_path,
            }
        )

        assert result.is_error is False, result.content[0].text
        assert os.path.getsize(output) > 0

    @pytest.mark.asyncio
    async def test_pptx_output_handles_non_ascii_content(self):
        """OOXML is zipped XML, so encoding problems surface as a corrupt package."""
        output = self._path("unicode.pptx")

        result = await self._convert(
            {
                "contents": "# Ünïcødé başlık\n\nTürkçe içerik ve emoji 🎯",
                "output_format": "pptx",
                "output_file": output,
            }
        )

        assert result.is_error is False, result.content[0].text
        assert os.path.getsize(output) > 0

    @pytest.mark.asyncio
    async def test_pptx_output_without_headings_still_produces_a_deck(self):
        """Content with no headings has no slide breaks. Pandoc still writes a valid deck."""
        output = self._path("no_headings.pptx")

        result = await self._convert(
            {"contents": "Just a paragraph, no headings.", "output_format": "pptx", "output_file": output}
        )

        assert result.is_error is False, result.content[0].text
        assert os.path.getsize(output) > 0
