import os
import comtypes.client
import pythoncom

def convert_word_to_pdf(doc_path, output_folder):
    word = None
    doc = None

    try:
        pythoncom.CoInitialize()

        doc_path = os.path.abspath(doc_path)
        output_folder = os.path.abspath(output_folder)

        if not os.path.exists(doc_path):
            raise Exception("File not found")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        word = comtypes.client.CreateObject("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0  # Disable popups

        # Open safely
        doc = word.Documents.Open(
            doc_path,
            ReadOnly=True,
            ConfirmConversions=False
        )

        output_path = os.path.join(
            output_folder,
            os.path.splitext(os.path.basename(doc_path))[0] + ".pdf"
        )

        # Absolute path required by Word
        output_path = os.path.abspath(output_path)

        # Use constant instead of raw number
        wdExportFormatPDF = 17

        doc.ExportAsFixedFormat(
            OutputFileName=output_path,
            ExportFormat=wdExportFormatPDF,
            OpenAfterExport=False
        )

        return output_path

    except Exception as e:
        raise Exception(f"Word to PDF conversion failed: {str(e)}")

    finally:
        if doc:
            doc.Close(False)
        if word:
            word.Quit()
        pythoncom.CoUninitialize()