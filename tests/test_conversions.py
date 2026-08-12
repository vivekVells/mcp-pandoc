import pypandoc
import os
import shutil
import pytest

# pandoc renders PDF through an external engine (a TeX distribution by default).
# Without one installed, PDF conversion cannot run — so those cases are skipped
# rather than failed. This keeps CI green on jobs that install pandoc but not a
# heavy TeX distribution (e.g. the Windows matrix job).
_PDF_ENGINES = (
    "pdflatex", "xelatex", "lualatex", "tectonic", "wkhtmltopdf",
    "weasyprint", "prince", "context", "pagedjs-cli", "typst",
)


def _pdf_engine_available() -> bool:
    return any(shutil.which(engine) for engine in _PDF_ENGINES)

# Define paths
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# All supported formats. pdf and pptx are write-only: pandoc has no pdf reader in any
# release, and its pptx reader arrived in 3.8.3, which this project does not require.
FORMATS = ['md', 'html', 'txt', 'rst', 'tex', 'docx', 'pdf', 'epub', 'ipynb', 'odt', 'pptx']
WRITE_ONLY_FORMATS = ['pdf', 'pptx']

# Create a dummy fixture file for each format
for format in FORMATS:
    if format not in ['pdf', 'pptx', 'docx', 'epub', 'ipynb', 'odt']:
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

    # pdf and pptx are write-only. There is no fixture to read from, by design.
    if from_format in WRITE_ONLY_FORMATS:
        pytest.skip(f"Skipping conversion from {from_format}: this project treats it as write-only.")

    # For this test, we will only test converting *to* pdf from markdown
    if to_format == 'pdf' and from_format != 'md':
        pytest.skip("Skipping conversion to PDF from formats other than markdown for this test.")

    # PDF output needs a rendering engine (TeX etc.). Skip cleanly when none is
    # installed instead of failing — e.g. a Windows job with pandoc but no TeX.
    if to_format == 'pdf' and not _pdf_engine_available():
        pytest.skip("Skipping PDF conversion: no PDF engine (e.g. a TeX distribution) is installed.")

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
