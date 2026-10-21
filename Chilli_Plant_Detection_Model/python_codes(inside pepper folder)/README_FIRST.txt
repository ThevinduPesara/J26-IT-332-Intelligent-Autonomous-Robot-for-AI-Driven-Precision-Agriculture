PEPPER ANNOTATION CHECKER
=========================

Your folders
------------
Images:
C:\Users\LENOVO\Downloads\Lithira_Ai_part\pepper\pepper\pepper_photo

XML:
C:\Users\LENOVO\Downloads\Lithira_Ai_part\pepper\pepper\Labels

Output:
C:\Users\LENOVO\Downloads\Lithira_Ai_part\check_annotation

What the script does
--------------------
- Finds matching Pascal VOC XML + image pairs.
- Reads the first 100 valid matched pairs.
- Draws every bounding box.
- Writes the XML object class above each box.
- Saves every checked image into check_annotation.
- Creates one contact sheet for quick visual review.
- Creates CSV reports for class counts, object details and errors.

Install
-------
pip install pillow

Run
---
Open PowerShell in:

C:\Users\LENOVO\Downloads\Lithira_Ai_part

Then run:

python check_annotations.py

Files created
-------------
check_annotation\
    001_..._checked.jpg
    002_..._checked.jpg
    ...
    contact_sheet_first_100.jpg
    annotation_summary.csv
    object_details.csv
    class_counts.csv
    annotation_errors.csv

What to check visually
----------------------
1. Does every box cover the correct plant part?
2. Is the class name correct?
3. Are boxes too large or too small?
4. Are any leaves/parts missing annotations?
5. Are labels such as leaf, stem, flower, fruit, bud, root,
   back leaf and bottom leaf being used consistently?

Important for the nutrient model
--------------------------------
This script checks the EXISTING XML annotations only.

If the XML class says "leaf", the box is labelled "leaf".
It does not automatically change the class to N_Def, P_Def or K_Def.

After this annotation-quality check, the next step is to map the
nutrient-treatment folder/group to Healthy / N_Def / P_Def / K_Def
and prepare the model training dataset.
