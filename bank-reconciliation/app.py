# pdf_to_excel_gui.py

import tkinter as tk  # GUI library
from tkinter import filedialog, messagebox  # File dialog and message boxes
import pandas as pd  # Data handling and Excel export
import os  # File path operations
import xml.etree.ElementTree as ET

# --- Logic from convert_file.py (adapted for GUI use) ---
def extract_from_xml(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    ns = {'ns': root.tag.split('}')[0].strip('{')}

    def extract_transaction_data(entry, ns):
        data = {}
        entry_ref = entry.find('ns:NtryRef', ns)
        if entry_ref is not None and entry_ref.text:
            data['transaction_id'] = entry_ref.text.strip()
        amount = entry.find('ns:Amt', ns)
        if amount is not None and amount.text:
            data['amount'] = float(amount.text.strip())
            data['currency'] = amount.get('Ccy', 'EUR')
        cd_indicator = entry.find('ns:CdtDbtInd', ns)
        if cd_indicator is not None and cd_indicator.text:
            data['credit_debit'] = cd_indicator.text.strip()
        status = entry.find('ns:Sts', ns)
        if status is not None and status.text:
            data['status'] = status.text.strip()
        booking_date = entry.find('ns:BookgDt/ns:Dt', ns)
        if booking_date is not None and booking_date.text:
            data['booking_date'] = booking_date.text.strip()
        value_date = entry.find('ns:ValDt/ns:Dt', ns)
        if value_date is not None and value_date.text:
            data['value_date'] = value_date.text.strip()
        acct_svcr_ref = entry.find('ns:AcctSvcrRef', ns)
        if acct_svcr_ref is not None and acct_svcr_ref.text:
            data['bank_reference'] = acct_svcr_ref.text.strip()
        bank_tx_code = entry.find('ns:BkTxCd/ns:Domn/ns:Cd', ns)
        if bank_tx_code is not None and bank_tx_code.text:
            data['transaction_type'] = bank_tx_code.text.strip()
        bank_tx_family = entry.find('ns:BkTxCd/ns:Domn/ns:Fmly/ns:Cd', ns)
        if bank_tx_family is not None and bank_tx_family.text:
            data['transaction_family'] = bank_tx_family.text.strip()
        bank_tx_subfamily = entry.find('ns:BkTxCd/ns:Domn/ns:Fmly/ns:SubFmlyCd', ns)
        if bank_tx_subfamily is not None and bank_tx_subfamily.text:
            data['transaction_subfamily'] = bank_tx_subfamily.text.strip()
        return data

    def extract_transaction_details(tx_dtls, ns):
        data = {}
        tx_ref = tx_dtls.find('ns:Refs/ns:AcctSvcrRef', ns)
        if tx_ref is not None and tx_ref.text:
            data['transaction_reference'] = tx_ref.text.strip()
        inst_amt = tx_dtls.find('ns:AmtDtls/ns:InstdAmt/ns:Amt', ns)
        if inst_amt is not None and inst_amt.text:
            data['instructed_amount'] = float(inst_amt.text.strip())
        tx_amt = tx_dtls.find('ns:AmtDtls/ns:TxAmt/ns:Amt', ns)
        if tx_amt is not None and tx_amt.text:
            data['transaction_amount'] = float(tx_amt.text.strip())
        src_ccy = tx_dtls.find('ns:AmtDtls/ns:TxAmt/ns:CcyXchg/ns:SrcCcy', ns)
        trgt_ccy = tx_dtls.find('ns:AmtDtls/ns:TxAmt/ns:CcyXchg/ns:TrgtCcy', ns)
        xchg_rate = tx_dtls.find('ns:AmtDtls/ns:TxAmt/ns:CcyXchg/ns:XchgRate', ns)
        if src_ccy is not None and trgt_ccy is not None and src_ccy.text and trgt_ccy.text:
            data['source_currency'] = src_ccy.text.strip()
            data['target_currency'] = trgt_ccy.text.strip()
            if xchg_rate is not None and xchg_rate.text:
                data['exchange_rate'] = float(xchg_rate.text.strip())
        debtor_name = tx_dtls.find('ns:RltdPties/ns:Dbtr/ns:Nm', ns)
        if debtor_name is not None and debtor_name.text:
            data['debtor_name'] = debtor_name.text.strip()
        debtor_address = tx_dtls.find('ns:RltdPties/ns:Dbtr/ns:PstlAdr/ns:AdrLine', ns)
        if debtor_address is not None and debtor_address.text:
            data['debtor_address'] = debtor_address.text.strip()
        creditor_name = tx_dtls.find('ns:RltdPties/ns:Cdtr/ns:Nm', ns)
        if creditor_name is not None and creditor_name.text:
            data['creditor_name'] = creditor_name.text.strip()
        debtor_bic = tx_dtls.find('ns:RltdAgts/ns:DbtrAgt/ns:FinInstnId/ns:BIC', ns)
        if debtor_bic is not None and debtor_bic.text:
            data['debtor_bank_bic'] = debtor_bic.text.strip()
        debtor_bank_name = tx_dtls.find('ns:RltdAgts/ns:DbtrAgt/ns:FinInstnId/ns:Nm', ns)
        if debtor_bank_name is not None and debtor_bank_name.text:
            data['debtor_bank_name'] = debtor_bank_name.text.strip()
        debtor_bank_country = tx_dtls.find('ns:RltdAgts/ns:DbtrAgt/ns:FinInstnId/ns:PstlAdr/ns:Ctry', ns)
        if debtor_bank_country is not None and debtor_bank_country.text:
            data['debtor_bank_country'] = debtor_bank_country.text.strip()
        ustrd_elements = tx_dtls.findall('.//ns:Ustrd', ns)
        if ustrd_elements:
            data['description'] = ' | '.join([elem.text.strip() for elem in ustrd_elements if elem.text and elem.text.strip()])
        return data

    acct = root.find('.//ns:Acct', ns)
    account_info = {}
    if acct:
        iban = acct.find('ns:Id/ns:IBAN', ns)
        if iban is not None and iban.text:
            account_info['account_iban'] = iban.text.strip()
        currency = acct.find('ns:Ccy', ns)
        if currency is not None and currency.text:
            account_info['account_currency'] = currency.text.strip()
        owner_name = acct.find('ns:Ownr/ns:Nm', ns)
        if owner_name is not None and owner_name.text:
            account_info['account_owner'] = owner_name.text.strip()
        servicer_bic = acct.find('ns:Svcr/ns:FinInstnId/ns:BIC', ns)
        if servicer_bic is not None and servicer_bic.text:
            account_info['account_servicer_bic'] = servicer_bic.text.strip()

    stmt = root.find('.//ns:Stmt', ns)
    statement_info = {}
    if stmt:
        stmt_id = stmt.find('ns:Id', ns)
        if stmt_id is not None and stmt_id.text:
            statement_info['statement_id'] = stmt_id.text.strip()
        stmt_date = stmt.find('ns:CreDtTm', ns)
        if stmt_date is not None and stmt_date.text:
            statement_info['statement_date'] = stmt_date.text.strip()

    opening_balance = None
    closing_balance = None
    balances = root.findall('.//ns:Bal', ns)
    for bal in balances:
        bal_type = bal.find('ns:Tp/ns:CdOrPrtry/ns:Cd', ns)
        if bal_type is not None and bal_type.text:
            bal_type_code = bal_type.text.strip()
            bal_amt = bal.find('ns:Amt', ns)
            bal_cd = bal.find('ns:CdtDbtInd', ns)
            bal_date = bal.find('ns:Dt/ns:Dt', ns)
            if bal_amt is not None and bal_amt.text and bal_cd is not None and bal_cd.text:
                balance_data = {
                    'amount': float(bal_amt.text.strip()),
                    'currency': bal_amt.get('Ccy', 'EUR'),
                    'credit_debit': bal_cd.text.strip(),
                    'date': bal_date.text.strip() if bal_date is not None and bal_date.text else None
                }
                if bal_type_code == 'OPBD':
                    opening_balance = balance_data
                elif bal_type_code == 'CLBD':
                    closing_balance = balance_data

    data = []
    for entry in root.findall('.//ns:Ntry', ns):
        entry_data = extract_transaction_data(entry, ns)
        txs = entry.findall('.//ns:TxDtls', ns)
        if txs:
            for tx in txs:
                tx_data = extract_transaction_details(tx, ns)
                row = {}
                row.update(account_info)
                row.update(statement_info)
                if opening_balance:
                    row.update({f'opening_balance_{k}': v for k, v in opening_balance.items()})
                if closing_balance:
                    row.update({f'closing_balance_{k}': v for k, v in closing_balance.items()})
                row.update(entry_data)
                row.update(tx_data)
                row['source_file'] = os.path.basename(xml_file_path)
                data.append(row)
        else:
            row = {}
            row.update(account_info)
            row.update(statement_info)
            if opening_balance:
                row.update({f'opening_balance_{k}': v for k, v in opening_balance.items()})
            if closing_balance:
                row.update({f'closing_balance_{k}': v for k, v in closing_balance.items()})
            row.update(entry_data)
            row['source_file'] = os.path.basename(xml_file_path)
            data.append(row)
    return pd.DataFrame(data)

# --- GUI logic ---
def select_and_convert_files():
    file_paths = filedialog.askopenfilenames(
        title="Select XML/NDA Files",
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
        # Remove duplicate columns (keep only the most specific version)
        columns_to_keep = []
        for col in df_all.columns:
            if col not in columns_to_keep:
                columns_to_keep.append(col)
        # Reorder columns for better readability
        preferred_order = [
            'transaction_id', 'transaction_reference', 'booking_date', 'value_date',
            'amount', 'currency', 'credit_debit', 'status',
            'transaction_type', 'transaction_family', 'transaction_subfamily',
            'debtor_name', 'creditor_name', 'description',
            'debtor_bank_bic', 'debtor_bank_name', 'debtor_bank_country',
            'account_iban', 'account_currency', 'account_owner', 'account_servicer_bic',
            'statement_id', 'statement_date', 'source_file'
        ]
        balance_cols = [col for col in df_all.columns if col.startswith('opening_balance_') or col.startswith('closing_balance_')]
        preferred_order.extend(balance_cols)
        remaining_cols = [col for col in df_all.columns if col not in preferred_order]
        final_order = [col for col in preferred_order if col in df_all.columns] + remaining_cols
        df_all = df_all[final_order]
        output_csv = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Output CSV As"
        )
        if not output_csv:
            return
        df_all.to_csv(output_csv, index=False)
        messagebox.showinfo("Success", f"Data saved to:\n{output_csv}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- GUI Setup ---
root = tk.Tk()
root.title("XML/NDA to CSV Converter")
root.geometry("350x180")

btn = tk.Button(root, text="Select XML/NDA Files", command=select_and_convert_files, width=30, height=2)
btn.pack(pady=50)

root.mainloop()