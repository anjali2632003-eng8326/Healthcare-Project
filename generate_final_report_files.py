import os
import sys

def main():
    print("Running document generator and converter...")
    # Run script
    os.system("python build_complete_64page_docx.py")
    
    docx_path = "Healthcare_Data_Analysis_and_Visualization_Dashboard_Project_Report.docx"
    pdf_path = "Healthcare_Data_Analysis_and_Visualization_Dashboard_Project_Report.pdf"
    
    if os.path.exists(docx_path):
        print(f"DOCX created at {os.path.abspath(docx_path)}")
        try:
            from docx2pdf import convert
            print("Converting DOCX to PDF...")
            convert(docx_path, pdf_path)
            print(f"PDF created at {os.path.abspath(pdf_path)}")
        except Exception as e:
            print("docx2pdf note:", e)
            try:
                import win32com.client
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                doc = word.Documents.Open(os.path.abspath(docx_path))
                doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
                doc.Close()
                word.Quit()
                print(f"PDF created via Win32COM at {os.path.abspath(pdf_path)}")
            except Exception as ex:
                print("Win32COM note:", ex)

if __name__ == "__main__":
    main()
