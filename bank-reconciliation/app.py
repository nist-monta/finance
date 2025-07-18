# pdf_to_excel_gui.py

import tkinter as tk  # GUI library
from tkinter import filedialog, messagebox  # File dialog and message boxes
import pandas as pd  # Data handling and Excel export
import os  # File path operations
from convert_file import extract_from_xml, process_dataframe

# --- GUI logic ---
def select_and_convert_files():
    file_paths = filedialog.askopenfilenames(
        title="Select CAMT053 files",
        filetypes=[("XML/NDA Files", "*.xml *.nda")]
    )
    if not file_paths:
        return
    try:
        df_list = []
        for fpath in file_paths:
            df = extract_from_xml(fpath)
            df_list.append(df)
        if not df_list:
            messagebox.showwarning("No Data", "No data extracted from selected files.")
            return
        df_all = pd.concat(df_list, ignore_index=True)
        # Process the dataframe with invoice logic and column filtering
        df_all = process_dataframe(df_all)
        output_csv = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Output CSV As",
        )
        if not output_csv:
            return
        df_all.to_csv(output_csv, index=False)
        messagebox.showinfo("Success", f"Data saved to:\n{output_csv}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- GUI Setup ---
root = tk.Tk()
root.title("CAMT053 Bank Reconciliation")
root.geometry("350x180")

btn = tk.Button(root, text="Select CAMT053 Files", command=select_and_convert_files, width=30, height=2)
btn.pack(pady=50)

root.mainloop()