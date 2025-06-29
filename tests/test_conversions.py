import pypandoc
import os
import pytest

# Define paths
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# All supported formats
FORMATS = ['md', 'html', 'txt', 'rst', 'tex', 'docx', 'pdf', 'epub', 'ipynb', 'odt']

# Create a dummy fixture file for each format
for format in FORMATS:
    if format not in ['pdf', 'docx', 'epub', 'ipynb', 'odt']:
        with open(os.path.join(FIXTURE_DIR, f'test.{format}'), 'w') as f:
            f.write(f'# Test Document\n\nThis is a test document for pandoc conversion from {format}.\n')

# Create valid docx, epub, ipynb, and odt fixtures
pypandoc.convert_text('# Test', 'docx', format='md', outputfile=os.path.join(FIXTURE_DIR, 'test.docx'))
pypandoc.convert_text('# Test', 'epub', format='md', outputfile=os.path.join(FIXTURE_DIR, 'test.epub'))
pypandoc.convert_text('# Test', 'ipynb', format='md', outputfile=os.path.join(FIXTURE_DIR, 'test.ipynb'))
pypandoc.convert_text('# Test', 'odt', format='md', outputfile=os.path.join(FIXTURE_DIR, 'test.odt'))

@pytest.mark.parametrize("from_format", FORMATS)
@pytest.mark.parametrize("to_format", FORMATS)
def test_bidirectional_conversions(from_format, to_format):
    """Tests all bidirectional conversions between supported formats."""
    if from_format == to_format:
        pytest.skip("Skipping conversion from a format to itself.")

    # PDF is a special case, we can only convert *to* it, not *from* it with pandoc easily
    if from_format == 'pdf':
        pytest.skip("Skipping conversion from PDF as it is not reliably supported by pandoc.")

    # For this test, we will only test converting *to* pdf from markdown
    if to_format == 'pdf' and from_format != 'md':
        pytest.skip("Skipping conversion to PDF from formats other than markdown for this test.")

    input_file = os.path.join(FIXTURE_DIR, f'test.{from_format}')
    output_file = os.path.join(OUTPUT_DIR, f'test.{to_format}')

    # pypandoc uses 'plain' for txt and 'latex' for tex
    pandoctor_from_format = from_format
    if from_format == 'txt':
        pandoctor_from_format = 'markdown' # Treat txt as markdown
    elif from_format == 'tex':
        pandoctor_from_format = 'latex'

    pandoctor_to_format = to_format
    if to_format == 'txt':
        pandoctor_to_format = 'plain'

    try:
        pypandoc.convert_file(input_file, pandoctor_to_format, format=pandoctor_from_format, outputfile=output_file)
        assert os.path.exists(output_file)
    except Exception as e:
        pytest.fail(f"Conversion from {from_format} to {to_format} failed with error: {e}")