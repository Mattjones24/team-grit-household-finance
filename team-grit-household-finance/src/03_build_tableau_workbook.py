"""
Step 3 - Build the Tableau workbook (tableau/Team_Grit_SCE_Household_Finance.twb).

8 worksheets + 3 dashboards on the cleaned CSV, using survey-weighted calculated fields.
Run from the repository root:  python src/03_build_tableau_workbook.py
The workbook stores the absolute folder of the CSV; re-run this script after moving the repo,
or use Edit Connection in Tableau.
"""
import html, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "sce_household_finance_clean.csv"
DIR = sys.argv[1] if len(sys.argv) > 1 else str(CSV.parent)
d=pd.read_csv(CSV)
DS='federated.teamgrit01'; TS='textscan.teamgrit01'
def dt(c):
    k=d[c].dtype.kind
    return 'string' if k=='O' else ('integer' if k=='i' else 'real')
cols=''.join(f"<column datatype='{dt(c)}' name='{c}' ordinal='{i}' />" for i,c in enumerate(d.columns))
q=lambda s: html.escape(s, quote=True)
def wavg(f): return f"SUM([{f}]*[weight]) / SUM(IIF(ISNULL([{f}]),0,[weight]))"
calcs={ # id: (caption, formula, type(measure/dim), datatype, format)
 'C_share':("Weighted Share", "SUM(IIF(ISNULL([saving_behavior]),0,[weight])) / MIN({FIXED [income_group]: SUM(IIF(ISNULL([saving_behavior]),0,[weight]))})",'m','real','p0%'),
 'C_saver':("Net Saver % (weighted)", wavg('net_saver'),'m','real','p0%'),
 'C_shock':("Shock Status", "IF ISNULL([shock_group]) THEN NULL ELSEIF [shock_group]='No shock' THEN 'No shock' ELSE 'Income drop or health decline' END",'d','string',None),
 'C_v1':("Valid RQ1", "NOT ISNULL([income_group]) AND NOT ISNULL([saving_behavior])",'d','boolean',None),
 'C_v2':("Valid Shock", "NOT ISNULL([income_group]) AND NOT ISNULL([shock_group]) AND NOT ISNULL([net_saver])",'d','boolean',None),
 'C_v3':("Valid Debt Mix", "[non_housing_debt]>0 AND NOT ISNULL([pct_credit_card]) AND NOT ISNULL([housing_debt_tier])",'d','boolean',None),
 'C_v4':("Known Credit", "NOT ISNULL([credit_rating]) AND [credit_rating]<>\"6. Don't know\"",'d','boolean',None),
 'C_cc':("Credit cards", wavg('amt_credit_card'),'m','real','c"$"#,##0'),
 'C_auto':("Auto loans", wavg('amt_auto'),'m','real','c"$"#,##0'),
 'C_stu':("Student loans", wavg('amt_student'),'m','real','c"$"#,##0'),
 'C_med':("Medical bills", wavg('amt_medical'),'m','real','c"$"#,##0'),
 'C_oth':("Other & legal", "SUM((ZN([amt_other_loans])+ZN([amt_legal]))*[weight]) / SUM(IIF(ISNULL([amt_credit_card]),0,[weight]))",'m','real','c"$"#,##0'),
 'C_bk':("Avg % chance of bankruptcy (12m)", f"({wavg('pct_chance_bankruptcy_12m')})/100",'m','real','p0.0%'),
 'C_2k':("Avg % chance can raise $2,000", f"({wavg('pct_chance_can_raise_2k')})/100",'m','real','p0%'),
 'C_age':("Avg planned retirement age", wavg('planned_retirement_age'),'m','real','n#,##0.0'),
 'C_yrs':("Avg years savings will last", wavg('years_savings_will_last'),'m','real','n#,##0.0'),
 'C_short':("% expecting 'too little' saved", "SUM(IIF([savings_adequacy]='Too little',[weight],0)) / SUM(IIF(ISNULL([savings_adequacy]),0,[weight]))",'m','real','p0%'),
 'C_vinc':("Has Income Group", "NOT ISNULL([income_group])",'d','boolean',None),
 'C_vsav':("Has Savings Tier", "NOT ISNULL([savings_tier])",'d','boolean',None),
}
def calc_col(cid):
    cap,f,r,t,fmt=calcs[cid]
    role='measure' if r=='m' else 'dimension'; typ='quantitative' if r=='m' else 'nominal'
    df=f" default-format='{q(fmt)}'" if fmt else ''
    return f"<column caption='{q(cap)}' datatype='{t}'{df} name='[{cid}]' role='{role}' type='{typ}'><calculation class='tableau' formula='{q(f)}' /></column>"
def base_col(c):
    t=dt(c); role='dimension' if t=='string' else 'measure'; typ='nominal' if t=='string' else 'quantitative'
    return f"<column datatype='{t}' name='[{c}]' role='{role}' type='{typ}' />"
allcalcs=''.join(calc_col(c) for c in calcs)
datasource=f"""<datasource caption='SCE Household Finance (Team Grit)' inline='true' name='{DS}' version='18.1'>
<connection class='federated'><named-connections><named-connection caption='sce_household_finance_clean' name='{TS}'>
<connection class='textscan' directory='{DIR}' filename='sce_household_finance_clean.csv' password='' server='' /></named-connection></named-connections>
<relation connection='{TS}' name='sce_household_finance_clean.csv' table='[sce_household_finance_clean#csv]' type='table'>
<columns character-set='UTF-8' header='yes' locale='en_US' separator=','>{cols}</columns></relation></connection>
<aliases enabled='yes' />{allcalcs}</datasource>"""

def dim(c): return f"[none:{c}:nk]"
def usr(c): return f"[usr:{c}:qk]"
def ci_dim(c): return f"<column-instance column='[{c}]' derivation='None' name='{dim(c)}' pivot='key' type='nominal' />"
def ci_usr(c): return f"<column-instance column='[{c}]' derivation='User' name='{usr(c)}' pivot='key' type='quantitative' />"
def R(x): return f"[{DS}].{x}"
def colrefs(names):
    out=''
    for n in names:
        out+= calc_col(n) if n in calcs else base_col(n)
    return out
def boolfilter(c):
    return f"<filter class='categorical' column='{R(dim(c))}'><groupfilter function='member' level='{dim(c)}' member='true' user:ui-domain='relevant' user:ui-enumeration='inclusive' user:ui-marker='enumerate' /></filter>"

def sheet(name,title,rows,cols,mark,dims,meas,filters,color=None,text=None,extra_ci='',extra_cols=[],mn_filter=None):
    deps=colrefs(list(dict.fromkeys(dims+meas+extra_cols)))+''.join(ci_dim(c) for c in dims)+''.join(ci_usr(c) for c in meas)+extra_ci
    enc=''
    if color: enc+=f"<color column='{color}' />"
    if text: enc+=f"<text column='{text}' />"
    flt=''.join(boolfilter(f) for f in filters)+(mn_filter or '')
    return f"""<worksheet name='{q(name)}'><layout-options><title><formatted-text><run bold='true' fontsize='14'>{q(title)}</run></formatted-text></title></layout-options>
<table><view><datasources><datasource caption='SCE Household Finance (Team Grit)' name='{DS}' /></datasources>
<datasource-dependencies datasource='{DS}'>{deps}</datasource-dependencies>{flt}<aggregation value='true' /></view><style />
<panes><pane selection-relaxation-option='selection-relaxation-allow'><view><breakdown value='auto' /></view><mark class='{mark}' />
<encodings>{enc}</encodings><style><style-rule element='mark'><format attr='mark-labels-show' value='true' /><format attr='mark-labels-cull' value='true' /></style-rule></style></pane></panes>
<rows>{rows}</rows><cols>{cols}</cols></table><simple-id uuid='{{{abs(hash(name))%10**8:08d}-0000-4000-8000-000000000000}}' /></worksheet>"""

S=[]
S.append(sheet('1 Saving by Income','Higher income turns households into net savers', R(dim('income_group')), R(usr('C_share')),'Bar',
     ['income_group','saving_behavior','C_v1'],['C_share'],['C_v1'],color=R(dim('saving_behavior')),text=R(usr('C_share'))))
S.append(sheet('2 Shocks and Saving','A shock cuts the net-saver rate at every income level', R(usr('C_saver')), R(dim('income_group')),'Line',
     ['income_group','C_shock','C_v2'],['C_saver'],['C_v2'],color=R(dim('C_shock')),text=R(usr('C_saver'))))
mn=['C_cc','C_auto','C_stu','C_med','C_oth']
mnf="<filter class='categorical' column='"+R('[:Measure Names]')+"'><groupfilter function='union' user:op='manual'>"+''.join(f"<groupfilter function='member' level='[:Measure Names]' member='&quot;{R(usr(m))}&quot;' />" for m in mn)+"</groupfilter></filter>"
S.append(sheet('3 Debt Mix by Mortgage','Large mortgages come with more consumer debt (avg per indebted household)', R('[Multiple Values]'), R(dim('housing_debt_tier')),'Bar',
     ['housing_debt_tier','C_v3'],mn,['C_v3'],color=R('[:Measure Names]'),mn_filter=mnf))
S.append(sheet('4 Credit vs Bankruptcy Risk','Weak credit = ~7x the expected bankruptcy risk', R(usr('C_bk')), R(dim('credit_rating')),'Bar',
     ['credit_rating','C_v4'],['C_bk'],['C_v4'],text=R(usr('C_bk'))))
S.append(sheet('5 Credit vs $2k Cushion','...and far less cushion for a surprise $2,000 bill', R(usr('C_2k')), R(dim('credit_rating')),'Bar',
     ['credit_rating','C_v4'],['C_2k'],['C_v4'],text=R(usr('C_2k'))))
S.append(sheet('6 Retirement Age by Income','Higher income: retire ~3 years earlier', R(usr('C_age')), R(dim('income_group')),'Bar',
     ['income_group','C_vinc'],['C_age'],['C_vinc'],text=R(usr('C_age'))))
S.append(sheet('7 Years Savings Last','More savings: savings last 2.5x longer', R(usr('C_yrs')), R(dim('savings_tier')),'Bar',
     ['savings_tier','C_vsav'],['C_yrs'],['C_vsav'],text=R(usr('C_yrs'))))
S.append(sheet('8 Retirement Shortfall','Share expecting too little saved for retirement', R(dim('savings_tier')), R(usr('C_short')),'Bar',
     ['savings_tier','C_vsav'],['C_short'],['C_vsav'],text=R(usr('C_short'))))

zid=[10]
def z(**k):
    zid[0]+=1; k['id']=zid[0]
    return k
def dash(name,title,subtitle,layout):
    # layout: list of (sheetname,x,y,w,h) in 0..100000 units below a header band
    zones=f"<zone h='9000' id='{z()['id']}' type-v2='text' w='100000' x='0' y='0'><formatted-text><run bold='true' fontsize='20'>{q(title)}</run><run>&#10;</run><run fontcolor='#52514e' fontsize='11'>{q(subtitle)}</run></formatted-text></zone>"
    for (s,x,y,w,h) in layout:
        zones+=f"<zone h='{h}' id='{z()['id']}' name='{q(s)}' w='{w}' x='{x}' y='{y}' />"
    zones+=f"<zone h='4000' id='{z()['id']}' type-v2='text' w='100000' x='0' y='96000'><formatted-text><run fontcolor='#8a8984' fontsize='8'>Source: Survey of Consumer Expectations, © 2013-2019 Federal Reserve Bank of New York (FRBNY). SCE Household Finance survey, 2014-2019 waves; survey-weighted. Team Grit.</run></formatted-text></zone>"
    return f"""<dashboard name='{q(name)}'><style /><size maxheight='800' maxwidth='1300' minheight='800' minwidth='1300' sizing-mode='fixed' />
<zones><zone h='100000' id='{z()['id']}' type-v2='layout-basic' w='100000' x='0' y='0'>{zones}</zone></zones><simple-id uuid='{{{abs(hash(name))%10**8:08d}-1111-4000-8000-000000000000}}' /></dashboard>"""
D=[dash('RQ1 Income, Saving & Shocks','RQ1 — Income decides who saves; shocks erase much of that advantage','Saving behavior by household income (left) and net-saver rate with vs. without an income or health shock (right).',
        [('1 Saving by Income',0,9000,55000,87000),('2 Shocks and Saving',55000,9000,45000,87000)]),
   dash('RQ2 Housing Debt & Credit','RQ2 — Bigger mortgages bring more consumer debt; weak credit signals default risk','Average non-housing debt by type and mortgage tier (left); self-rated credit vs expected bankruptcy risk and $2k cushion (right).',
        [('3 Debt Mix by Mortgage',0,9000,50000,87000),('4 Credit vs Bankruptcy Risk',50000,9000,50000,43500),('5 Credit vs $2k Cushion',50000,52500,50000,43500)]),
   dash('RQ3 Savings, Income & Retirement','RQ3 — Money buys an earlier and longer-lasting retirement','Non-retired household heads. Total savings = liquid savings + 401(k)/DC plans + IRAs.',
        [('6 Retirement Age by Income',0,9000,33333,87000),('7 Years Savings Last',33333,9000,33333,87000),('8 Retirement Shortfall',66666,9000,33334,87000)])]
names=[s.split("name='")[1].split("'")[0] for s in S]
dnames=['RQ1 Income, Saving &amp; Shocks','RQ2 Housing Debt &amp; Credit','RQ3 Savings, Income &amp; Retirement']
windows=''.join(f"<window class='worksheet' name='{n}'><cards><edge name='left'><strip size='160'><card type='pages' /><card type='filters' /><card type='marks' /></strip></edge><edge name='top'><strip size='2147483647'><card type='columns' /></strip><strip size='2147483647'><card type='rows' /></strip><strip size='31'><card type='title' /></strip></edge></cards></window>" for n in names)
windows+=''.join(f"<window class='dashboard' maximized='true' name='{n}'><viewpoints /></window>" for n in dnames)
twb=f"""<?xml version='1.0' encoding='utf-8' ?>
<workbook original-version='18.1' source-build='2023.1.0 (20231.23.0310.1045)' source-platform='mac' version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
<preferences><preference name='ui.encoding.shelf.height' value='24' /><preference name='ui.shelf.height' value='26' /></preferences>
<datasources>{datasource}</datasources>
<worksheets>{''.join(S)}</worksheets>
<dashboards>{''.join(D)}</dashboards>
<windows source-height='30'>{windows}</windows>
</workbook>"""
(ROOT / 'tableau' / 'Team_Grit_SCE_Household_Finance.twb').write_text(twb)
import xml.dom.minidom; xml.dom.minidom.parseString(twb.encode()); print('ok', len(twb))
