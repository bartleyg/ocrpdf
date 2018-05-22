# ocrpdf
OCR PDF files or directory of PDF files to text files and structured json files. This uses the Google Cloud Vision API and ImageMagick6.

## Setup:
Create a Google Cloud API key and setup your environment to authenticate with it: https://cloud.google.com/docs/authentication/getting-started

```
brew install imagemagick@6    # required for convert command
pip3 install -r requirements.txt
```

## Use:
```
# OCR one file
python3 ocrpdf.py input.pdf

# OCR a directory
python3 ocrpdf-dir.py directory-of-pdfs/

# OCR a directory with two threads for slight speed boost
python3 ocrpdf-dir-threaded.py directory-of-pdfs/
```

## JSON example output structure:
```json
{
  "pages": [
    {
      "blocks": [
        {
          "paragraphs": [
            "page 1 block 1 paragraph 1",
            "page 1 block 1 paragraph 2"
          ]
        },
        {
          "paragraphs": [
            "page 1 block 2 paragraph 1"
          ]
        }
      ]
    },
    {
      "blocks": [
        {
          "paragraphs": [
            "page 2 block 1 paragraph 1"
          ]
        },
        {
          "paragraphs": [
            "page 2 block 2 paragraph 1",
            "page 2 block 2 paragraph 2"
          ]
        }
      ]
    }
  ]
}
```
