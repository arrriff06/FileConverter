import comtypes.client
import os
import time
import pythoncom

def convert_ppt_to_pdf(ppt_path, output_folder):
    powerpoint = None
    presentation = None

    try:
        # Initialize COM (important!)
        pythoncom.CoInitialize()

        # Convert to absolute path
        ppt_path = os.path.abspath(ppt_path)
        output_folder = os.path.abspath(output_folder)

        if not os.path.exists(ppt_path):
            raise Exception("PPT file not found")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Start PowerPoint
        powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
        powerpoint.Visible = 1

        # Open presentation (WithWindow=False makes it stable)
        presentation = powerpoint.Presentations.Open(
            ppt_path,
            WithWindow=False
        )

        output_file = os.path.join(
            output_folder,
            f"converted_{int(time.time())}.pdf"
        )

        # 32 = PDF format
        presentation.SaveAs(output_file, 32)

        return output_file

    except Exception as e:
        raise Exception(f"PPT to PDF conversion failed: {str(e)}")

    finally:
        if presentation:
            presentation.Close()
        if powerpoint:
            powerpoint.Quit()
        pythoncom.CoUninitialize()