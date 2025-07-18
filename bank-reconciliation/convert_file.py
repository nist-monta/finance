import os
import pandas as pd
import xml.etree.ElementTree as ET
import re

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
        ustrd_elements = tx_dtls.findall('.//ns:Ustrd', ns)
        if ustrd_elements:
            data['description'] = ' | '.join([elem.text.strip() for elem in ustrd_elements if elem.text and elem.text.strip()])
        return data

    # Extract account information (static for all transactions)
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

    # Extract statement information
    stmt = root.find('.//ns:Stmt', ns)
    statement_info = {}
    if stmt:
        stmt_id = stmt.find('ns:Id', ns)
        if stmt_id is not None and stmt_id.text:
            statement_info['statement_id'] = stmt_id.text.strip()
        stmt_date = stmt.find('ns:CreDtTm', ns)
        if stmt_date is not None and stmt_date.text:
            statement_info['statement_date'] = stmt_date.text.strip()

    # Extract balance information
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

    # Collect transaction data
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

def process_dataframe(df_all):
    """Process the concatenated dataframe with invoice logic and column filtering"""
    # Add 'is_invoice_payment' column based on debtor_name
    invoice_exclude = ['ADYEN', 'U.S. BANK', 'Stripe', 'ELAVON', 'Adyen']
    if 'debtor_name' in df_all.columns:
        # Use vectorized string operations instead of apply
        name_mask = df_all['debtor_name'].str.contains('|'.join(invoice_exclude), case=False, na=False)
        df_all['is_invoice_payment'] = ~name_mask
    else:
        df_all['is_invoice_payment'] = True
    
    # Set is_invoice_payment to False for DBIT transactions
    if 'credit_debit' in df_all.columns:
        df_all['is_invoice_payment'] = df_all['is_invoice_payment'] & (df_all['credit_debit'] != 'DBIT')
    
    # Set is_invoice_payment to False if debtor_address contains specific strings
    if 'debtor_address' in df_all.columns:
        address_mask = df_all['debtor_address'].str.contains('ELAVON|Stripe|ADYEN', case=False, na=False)
        df_all['is_invoice_payment'] = df_all['is_invoice_payment'] & (~address_mask)
    
    # Set is_invoice_payment to False if description contains STRIPE
    if 'description' in df_all.columns:
        desc_mask = df_all['description'].str.contains('STRIPE', case=False, na=False)
        df_all['is_invoice_payment'] = df_all['is_invoice_payment'] & (~desc_mask)
    
    # User-specified columns - only keep these specific columns
    preferred_order = [
        'booking_date', 'value_date', 'amount', 'currency', 'credit_debit',
        'debtor_name', 'creditor_name', 'description', 'debtor_bank_bic',
        'debtor_bank_name', 'debtor_bank_country', 'account_iban', 'account_currency',
        'instructed_amount', 'transaction_amount', 'debtor_address',
        'source_currency', 'target_currency', 'exchange_rate', 'is_invoice_payment'
    ]
    
    # Add new columns for invoice extraction
    def extract_invoice_number(description):
        if pd.isna(description):
            return ''
        match = re.search(r'(?<!\d)(\d{6,7})(?!\d)', str(description))
        return match.group(1) if match else ''
    df_all['Inv.no.'] = df_all['description'].apply(extract_invoice_number) if 'description' in df_all.columns else ''
    
    def note_for_invoice(inv_no):
        return 'Inv.no. fetched via Python' if inv_no else ''
    df_all['Note'] = df_all['Inv.no.'].apply(note_for_invoice)
    df_all['Comment'] = ''
    
    # Add new columns to preferred_order if not present
    for col in ['Inv.no.', 'Note', 'Comment']:
        if col not in preferred_order:
            preferred_order.append(col)
    
    # Only keep columns that exist in the DataFrame
    final_order = [col for col in preferred_order if col in df_all.columns]
    df_all = df_all[final_order]
    
    return df_all

def main():
    """Main function to process files from directory"""
    # Directory containing the XML and NDA files
    input_dir = 'CA XML Account statement extended'
    
    # List all .xml and .nda files in the directory
    all_files = [f for f in os.listdir(input_dir) if f.endswith('.xml') or f.endswith('.nda')]
    
    # Process all files and concatenate results
    df_list = []
    for fname in all_files:
        fpath = os.path.join(input_dir, fname)
        try:
            df = extract_from_xml(fpath)
            df_list.append(df)
            print(f"Processed: {fname} ({len(df)} rows)")
        except Exception as e:
            print(f"Error processing {fname}: {e}")
    
    if df_list:
        df_all = pd.concat(df_list, ignore_index=True)
        df_all = process_dataframe(df_all)
        
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(df_all.head())
        output_csv = 'output_all.csv'
        df_all.to_csv(output_csv, index=False)
        print(f"\nData saved to: {output_csv}")
        print(f"Total columns extracted: {len(df_all.columns)}")
        print(f"Total rows: {len(df_all)}")
    else:
        print("No data extracted from any files.")

if __name__ == "__main__":
    main()
