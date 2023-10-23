import re
import os
import math
import json
import yaml
import argparse
import requests
import subprocess
from bs4 import BeautifulSoup

login_url = 'https://engold.pdn.ac.lk/coursereg/dcf/login.php'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compile', action='store_true', help='Compile the generated latex file to pdf.')
    
    group_1 = parser.add_argument_group('Specify the metadata as a path to the yml file')
    group_1.add_argument('--meta_path', help='Path to the yml metadata file.')
    group_2 = parser.add_argument_group('Specify the metadata as a dictionary')
    group_2.add_argument('--meta_cfg', help='Metadata dictionary.', type=json.loads)
    group_3 = parser.add_argument_group('Specify metadata as command-line arguments')
    group_3.add_argument('--user', help='Your registeration number in the E/XX/YYY format.')
    group_3.add_argument('--passwd', help='Your password for the course registeration / degree claim account.')
    group_3.add_argument('--DOB', help='Your date of birth in the DD Month YYYY format.')
    group_3.add_argument('--dept_head', help='The name of your head of department.')
    
    args = parser.parse_args()
    
    if not any([args.meta_path, args.meta_cfg]) and not any([args.user, args.passwd, args.DOB, args.dept_head]):
        parser.error("You must provide all the required arguments from at least one group. See --help for more information.")
    elif args.meta_path:
        try:
            with open(args.meta_path, "r") as file:
                metadata = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"The file '{args.meta_path}' was not found.")
            exit(0)
        except yaml.YAMLError as e:
            print(f"Error reading the YAML file: {e}")
            exit(0)
    elif args.meta_cfg:
        metadata = args.meta_cfg
    elif all([args.user, args.passwd, args.DOB, args.dept_head]):
        metadata = {
            'user': args.user,
            'passwd': args.passwd,
            'DOB': args.DOB,
            'dept_head': args.dept_head
        }

    login_data = {
        'un': metadata['user'],
        'pwd': metadata['passwd'],
        'login': 'Login'
    }

    # Send a POST request with the login data
    response = requests.post(login_url, data=login_data)

    # Check the response
    if response.status_code == 200:
        response2 = requests.get('https://engold.pdn.ac.lk/coursereg/dcf/viewgradereport22.php', headers={'Cookie': f"PHPSESSID={response.cookies.get('PHPSESSID')}"})
        if response2.status_code == 200:
            soup = BeautifulSoup(response2.text, 'html.parser')
            field = soup.find(text=re.compile('Field :')).next_element.text.strip()
            e_number = soup.find_all(text=re.compile('Grade Report - '))[0].split(' - ')[1]
            gpa_value = math.ceil(float(soup.find_all(text=re.compile('Final Course GPA ='))[0].split('Final Course GPA =')[1].strip()) * 20) / 20
            full_name = ' '.join(soup.find_all('p')[5].text.split()[-3:])
            dob = metadata['DOB']
            dept_head = metadata['dept_head']
            gp_table = [[cell.text.replace('!', 'I') for cell in row.find_all('option')] for row in soup.find('table', border='1', align='center').find_all('tr')[1:][0].find_all('td')]
            gp_table = '\\\\\n\\hline\n'.join([' & '.join([str(round(float(row[i].replace('&', '\\&')), 2)) if row[i].replace('&', '\\&').replace('.', '').isnumeric() else row[i].replace('&', '\\&') for row in gp_table]) for i in range(len(gp_table[0]))]) + '\\\\\n\\hline'
            te_credits, ge_credits = [[int(s) for s in re.findall(r'\d+', s.replace('\xa0', ''))] for s in soup.find_all(text=re.compile('Credits Offered = '))]
            te_deficit, ge_deficit = [re.findall(r'\d+', s.replace('\xa0', '').replace('.', ''))[-1] for s in soup.find_all(text=re.compile('Credit Deficit'))[1:3]]
            te_table = [[cell.text.replace('!', 'I') for cell in row.find_all('option')] for row in soup.find_all('table', border='1', align='center')[1].find_all('tr')[1:][0].find_all('td')]
            te_table = '\\\\\n\\hline\n'.join([' & '.join([str(round(float(row[i].replace('&', '\\&')), 2)) if row[i].replace('&', '\\&').replace('.', '').isnumeric() else row[i].replace('&', '\\&') for row in te_table]) for i in range(len(te_table[0]))]) + '\\\\\n\\hline'
            ge_table = [[cell.text.replace('!', 'I') for cell in row.find_all('option')] for row in soup.find_all('table', border='1', align='center')[2].find_all('tr')[1:][0].find_all('td')]
            ge_table = '\\\\\n\\hline\n'.join([' & '.join([str(round(float(row[i].replace('&', '\\&')), 2)) if row[i].replace('&', '\\&').replace('.', '').isnumeric() else row[i].replace('&', '\\&') for row in ge_table]) for i in range(len(ge_table[0]))]) + '\\\\\n\\hline'
            tr_table = [[cell.text.replace('!', 'I') for cell in row.find_all('option')] for row in soup.find_all('table', border='1', align='center')[3].find_all('tr')[1:][0].find_all('td')]
            tr_table = '\\\\\n\\hline\n'.join([' & '.join([str(round(float(row[i].replace('&', '\\&')), 2)) if row[i].replace('&', '\\&').replace('.', '').isnumeric() else row[i].replace('&', '\\&') for row in tr_table]) for i in range(len(tr_table[0]))]) + '\\\\\n\\hline'
            effective_date = soup.find('em', text=re.compile('Effective date')).parent.next_sibling.next_element.text.strip()

            r = requests.get('https://upload.wikimedia.org/wikipedia/en/c/cc/University_of_Peradeniya_crest.png')
            with open('logo.png', 'wb') as f:
                f.write(r.content)

            latex_doc = f"""\\documentclass[12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
% \\usepackage{{fontspec}}
% \\setmainfont[Ligatures=TeX]{{Arial}}
\\newcommand{{\\comment}}[1]{{}}

%\\usepackage[scaled]{{helvet}}
%\\renewcommand\\familydefault{{\\sfdefault}} 
%\\usepackage[T1]{{fontenc}}
\\usepackage{{makecell}}
\\usepackage{{hyperref}}
\\usepackage{{lingmacros}}
\\usepackage{{anyfontsize}}
\\usepackage{{tabularx}}
\\newcolumntype{{L}}{{>{{\\raggedright\\arraybackslash}}X}}
\\usepackage{{adjustbox}}
\\usepackage{{float}}
\\usepackage{{tree-dvips}}
\\usepackage[a4paper,top=2cm,bottom=2cm,left=3cm,right=3cm,marginparwidth=1.75cm]{{geometry}}

\\makeatletter
\\renewcommand{{\\@seccntformat}}[1]{{}}
\\makeatother

\\newcommand{{\\sign}}[1]{{%      
\\begin{{tabular}}[t]{{@{{}}l@{{}}}}
\\makebox[2.5in]{{\\dotfill}}\\\\
\\strut#1\\strut
\\end{{tabular}}%
}}
\\newcommand{{\\Date}}{{%
\\begin{{tabular}}[t]{{@{{}}p{{2.5in}}@{{}}}}
\\\\[-2ex]
\\strut Date: \\dotfill\\strut
\\end{{tabular}}%
}}

\\begin{{document}}


\\noindent
\\begin{{minipage}}[H]{{0.17\\linewidth}}
\\centering
\\includegraphics[width=1.0\\linewidth]{{logo.png}}
\\end{{minipage}}%
\\hfill
\\begin{{minipage}}[H]{{0.8\\linewidth}}
{{\\fontsize{{28}}{{30}}\\selectfont \\textbf{{University of Peradeniya\\\\Sri Lanka}}}}

\\Large Peradeniya, Sri Lanka 20400\\\\
{{\\fontsize{{12}}{{30}}\\selectfont Telephone:+94812393301\\hfill Fax:+94812388158}}


\\end{{minipage}}

\\vspace{{10pt}}
\\noindent\\rule{{\\textwidth}}{{1pt}}
\\vspace{{-15pt}}
\\begin{{center}}
{{\\fontsize{{21}}{{30}}\\selectfont \\textbf{{ACADEMIC TRANSCRIPT (INTERIM)}}}}
\\end{{center}}

\\vspace{{-12.5pt}}

\\noindent\\rule{{\\textwidth}}{{1pt}}

\\begin{{table}}[H]
\\begin{{tabularx}}{{\\textwidth}}{{Xl}}
\\textbf{{Registration Number}} & {e_number} \\\\
\\textbf{{Name in Full}} & {full_name} \\\\
\\textbf{{Date of Birth}} & {dob} \\\\
% \\end{{tabularx}}
% \\end{{table}}
\\\\
\\\\
% \\vspace{{-10pt}}

% \\begin{{table}}[H]
% \\begin{{tabularx}}{{\\textwidth}}{{Xl}}
\\textbf{{Field of Specialization}} & {field} \\\\
\\textbf{{Degree}} & Bachelor of the Science of Engineering \\\\
\\textbf{{Medium of Instruction}} & English \\\\
\\textbf{{Current GPA}} & {gpa_value:.2f} \\\\
\\end{{tabularx}}
\\end{{table}}

\\vspace{{-15pt}}

\\noindent\\rule{{\\textwidth}}{{1pt}}

\\vspace{{-20pt}}

\\section*{{General Programme in Engineering Courses}}

A student who advances to follow the Specialization Programme in Engineering has earned a minimum of 33 credits from the General Programme in Engineering (This is without considering GP 102: English II).

\\begin{{table}}[h]
\\begin{{tabularx}}{{\\textwidth}}{{
    |>{{\\hsize=0.6\\hsize}}X| 
    >{{\\hsize=0.5\\hsize}}X|
    >{{\\hsize=2.0\\hsize}}X|
    >{{\\hsize=0.4\\hsize}}X|
    >{{\\hsize=0.5\\hsize}}X|
}}
\\hline 
\\textbf{{Semester Ending Date}} & \\textbf{{Course ID}} & \\textbf{{Course Unit Name}} & \\textbf{{Grade}} & \\textbf{{Credits}} \\\\ 
\\hline
{gp_table}
\\end{{tabularx}}
\\end{{table}}

\\vspace{{-10pt}}

\\section*{{Core and Technical Elective (TE) Courses}}

\\begin{{tabularx}}{{\\textwidth}}{{|X|l|}}
\\hline 
\\textbf{{Credits Offered}} & {te_credits[0]} \\\\ \\hline 
\\textbf{{Credits Earned from Core and Technical Elective courses to claim the Degree}} & {te_credits[1]} \\\\ \\hline 
\\textbf{{Credit Deficit from Core and Technical Elective courses}} & {te_deficit} \\\\
\\hline 
\\textbf{{GPA}} & {gpa_value:.2f} \\\\
\\hline 
\\end{{tabularx}}

\\noindent The following Core and Technical Elective courses contribute towards the calculation of GPA. If a course is repeated, the best attempt is used for all of the above calculations.

\\begin{{table}}[H]
\\begin{{tabularx}}{{\\textwidth}}{{
    |>{{\\hsize=1.0\\hsize}}X| 
    >{{\\hsize=0.7\\hsize}}X|
    >{{\\hsize=2.4\\hsize}}X|
    >{{\\hsize=0.6\\hsize}}X|
    >{{\\hsize=0.6\\hsize}}X|
    >{{\\hsize=0.7\\hsize}}X|
}}
\\hline 
\\textbf{{Semester Ending Date}} & \\textbf{{Course ID}} & \\textbf{{Course Unit Name}} & \\textbf{{Grade}} & \\textbf{{Grade Point}} & \\textbf{{Credits}} \\\\ 
\\hline
{te_table}
\\end{{tabularx}}
\\end{{table}}

\\section*{{General Elective (GE) Courses}}

\\begin{{tabularx}}{{\\textwidth}}{{|X|l|}}
\\hline 
\\textbf{{Credits Offered}} & {ge_credits[0]} \\\\ \\hline 
\\textbf{{Credits Earned from General Elective courses to claim the Degree}} & {ge_credits[1]} \\\\ \\hline 
\\textbf{{Credit Deficit from General Elective courses}} & {ge_deficit} \\\\
\\hline 
\\end{{tabularx}}

\\vspace{{10pt}}

\\noindent The General Elective courses do not count towards GPA calculation. But these courses count for the Earned Credits to claim the degree and Credit Deficit calculations. If a course is repeated, the grade obtained in the best attempt is used for all of the above calculations.

\\begin{{table}}[H]
\\begin{{tabularx}}{{\\textwidth}}{{
    |>{{\\hsize=0.8\\hsize}}X| 
    >{{\\hsize=0.6\\hsize}}X|
    >{{\\hsize=2.6\\hsize}}X|
    >{{\\hsize=0.5\\hsize}}X|
    >{{\\hsize=0.5\\hsize}}X|
}}
\\hline
\\textbf{{Semester Ending Date}} & \\textbf{{Course ID}} & \\textbf{{Course Unit Name}} & \\textbf{{Grade}} & \\textbf{{Credits}} \\\\ 
\\hline
{ge_table}
\\end{{tabularx}}
\\end{{table}}

\\section[GP102: English II and TR400: Industrial Training Courses]{{\\texorpdfstring{{GP102: English II and TR400: Industrial Training \\\\Courses}}{{GP102: English II and TR400: Industrial Training Courses}}}}

TR400: Industrial Training will have to be Passed for the student to successfully complete the Specialization Programme in Engineering. After passing TR400, the student earns 6 more credits towards claiming the degree.

\\noindent GP102: English II will have to be Passed for the student to successfully complete the General Programme in Engineering. After passing GP102, the student earns 3 more credits towards claiming the degree.

\\begin{{table}}[H]
\\begin{{tabularx}}{{\\textwidth}}{{|L|l|l|l|l|}}
\\hline 
\\textbf{{Semester Ending Date}} & \\textbf{{Course ID}} & \\textbf{{Course Unit Name}} & \\textbf{{Grade}} & \\textbf{{Credits}} \\\\ 
\\hline
{tr_table}
\\end{{tabularx}}
\\end{{table}}


%\\noindent
%\\begin{{minipage}}[t]{{0.4\\linewidth}}
%\\centering
%
%\\begin{{table}}[H]
%\\begin{{tabularx}}{{1.0\\textwidth}}{{|L|L|}}
%\\hline
%\\textbf{{Grade}} & \\textbf{{Points}} \\\\ 
%\\hline
%A+ & 4.0 \\\\ 
%A & 4.0 \\\\ 
%A- & 3.7 \\\\ 
%B+ & 3.3 \\\\ 
%B & 3.0 \\\\ 
%B- & 2.7 \\\\ 
%C+ & 2.3 \\\\ 
%\\hline
%\\end{{tabularx}}
%\\end{{table}}
%
%\\end{{minipage}}%
%\\hfill
%  \\begin{{minipage}}[t]{{0.4\\linewidth}}
%  
%\\begin{{table}}[H]
%\\begin{{tabularx}}{{1.0\\textwidth}}{{|L|L|}}
%\\hline
%\\textbf{{Grade}} & \\textbf{{Points}} \\\\ 
%\\hline
%C & 2.0 \\\\ 
%C- & 1.7 \\\\ 
%D+ & 1.3 \\\\ 
%D & 1.0 \\\\ 
%E & 0.7 \\\\ 
%F & 0.0 \\\\ 
%\\hline
%\\end{{tabularx}}
%\\end{{table}}  
%\\end{{minipage}}


\\noindent\\rule{{\\textwidth}}{{1pt}}
\\vspace{{5pt}}
This is an interim academic transcript issued at the request of the student, covering seven (7) semesters that have been completed so far.
\\vspace{{5pt}}

\\noindent\\textbf{{Effective date:}} {effective_date}

\\vspace{{45pt}}

\\noindent
\\begin{{minipage}}[t]{{0.5\\linewidth}}
    \\raggedright
    \\sign{{{dept_head}}}
    \\par
    Head of Department\\par
    Department of {field}, \\par
    Faculty of Engineering, \\par
    University of Peradeniya, Sri Lanka
\\end{{minipage}}%
\\hfill
\\begin{{minipage}}[t]{{0.4\\linewidth}}
    \\Date
\\end{{minipage}}



\\textbf{{Note:}} Grade Points are given according to 0.0 - 4.0 scale

\\begin{{table}}[H]
\\centering
\\begin{{tabular}}{{ll}}
\\multicolumn{{1}}{{c}}{{Grade}} &
\\multicolumn{{1}}{{c}}{{Points}}\\\\
% Grade & Points \\\\ 
\\ \\ A+    & \\ \\ 4.0    \\\\ 
\\ \\ A     & \\ \\ 4.0    \\\\ 
\\ \\ A-    & \\ \\ 3.7    \\\\ 
\\ \\ B+    & \\ \\ 3.3    \\\\ 
\\ \\ B    & \\ \\ 3.0    \\\\ 
\\ \\ B-    & \\ \\ 2.7    \\\\ 
\\ \\ C+    & \\ \\ 2.3    \\\\ 
\\ \\ C     & \\ \\ 2.0    \\\\ 
\\ \\ C-    & \\ \\ 1.7    \\\\ 
\\ \\ D+    & \\ \\ 1.3    \\\\ 
\\ \\ D     & \\ \\ 1.0    \\\\ 
\\ \\ E     & \\ \\ 0.0    \\\\ 
\\end{{tabular}}
\\end{{table}}

\\begin{{center}}
**End of the document**
\\end{{center}}


\\end{{document}}        
"""
        e_number = e_number.replace('/', '')

        with open(f'{e_number}_transcript.tex', 'w') as f:
            f.write(latex_doc)
            
        if args.compile:
            proc = subprocess.Popen(['pdflatex', f'{e_number}_transcript.tex'])
            proc.communicate()
            
            os.unlink(f'{e_number}_transcript.log')
            os.unlink(f'{e_number}_transcript.aux')
            os.unlink(f'{e_number}_transcript.out')

if __name__ == '__main__':
    main()