SET path=%path%;C:\python25
#SET tiny_sxw2rml_path=../../base_report_designer/wizard/tiny_sxw2rml/tiny_sxw2rml.py
SET tiny_sxw2rml_path=../../../addons\base_report_designer\openerp_sxw2rml\openerp_sxw2rml.py
#SET tiny_sxw2rml_path=../../../addons/base_report_designer/wizard/tiny_sxw2rml/tiny_sxw2rml.py
python %tiny_sxw2rml_path% voucher_receipt_report.sxw > voucher_receipt_report.rml
pause