"""
module to process gbXML files. 
currently it can extract space type and areas and constructions information. 
"""


import xmltodict
from IPython.display import HTML, Markdown, JSON, display, Image, FileLink, FileLinks
import pandas as pd
import numpy as np
from mf_modules.pandas_operations import df_from_list_of_dicts
from mf_modules.pandas_operations import split_col
from mf_modules.pandas_operations import df_tonumeric
from mf_modules.file_operations import fnm_from_fpth


def extract_name_docs(gbxsdjson):
    '''
    extracts documentation assocated to a @name
    '''
    df=pd.DataFrame(columns=['schema_item','@name','xsd:annotation:documentation'])
    items=["xsd:simpleType","xsd:element"]
    for i in items:
        item=i
        simpleType=gbxsdjson["xsd:schema"][item]
        for t in simpleType:
            try:
                ann = t['xsd:annotation']['xsd:documentation']
            except:
                ann = 'na'
            df=df.append({'schema_item' : item , '@name' : t['@name'],'xsd:annotation:documentation':ann} , ignore_index=True)
    return df

def gbxml_json(FPTH,display_gbmxl=True):
    '''
    convert from gbxml format to json format
    '''
    from mf_modules.file_operations import path_leaf
    with open(FPTH) as fd:
        gbjson = xmltodict.parse(fd.read())
    if display_gbmxl == True:
        display(HTML(path_leaf(FPTH)))
        display(FileLink(FPTH))
        display(JSON(gbjson))
    return gbjson



def get_di_and_keys(key):
    di = gbjson['gbXML']['Campus']['Building'][key]
    li_of_keys = list(di[0])
    return (di,li_of_keys)

# constructions
def extract_uval(cnstrn,n):
    try:
        return np.round(float(cnstrn.loc[n]['U-value']['#text']),2)
    except:
        return None

def layer_id(cnstrn,n):
    try:
        return cnstrn['LayerId'].iloc[1]['@layerIdRef']
    except:
        return None

class GbxmlParser():
    def __init__(self, FPTH, display_gbmxl=True):
        self.FPTH = FPTH
        self.gbjson = gbxml_json(FPTH,display_gbmxl=display_gbmxl)
        
    @property
    def spcs(self):
        spcs = self.gbjson['gbXML']['Campus']['Building']['Space']
        li_of_keys = list(spcs[0])
        spcs = df_from_list_of_dicts(spcs,li_of_keys=li_of_keys)
        try:
            di = {0:'BlockCode',1:'Level',2:'TM46Category',3:'SpaceId',4:'SpaceType'}
            col_nm = 'Name'
            spcs = split_col(spcs,col_nm,di,pat='_')
        except:
            print('gbxml doesnt have mf compliant space name:')
            print("{0:'BlockCode',1:'Level',2:'TM46Category',3:'SpaceId',4:'SpaceType'}")
            di['spaces'] = spcs
        model=fnm_from_fpth(self.FPTH, drop_extension=False).split('.')[0]
        spcs['model']=model
        spcs = df_tonumeric(spcs)
        spcs['id'] = spcs['model'] + ', ' + spcs['Name']
        return spcs
    
    @property
    def cnstrn(self):
        '''
        Args:
            FPTH (str): fpth of gbxml file
            display_gbmxl (bool): show json structure in browser
        Returns:
            cnstrn (pd.DataFrame): dataframe of constructions in the gbxml model
        '''
        cnstrn = self.gbjson['gbXML']['Construction'][0]
        li_of_keys=list(cnstrn)
        cnstrn=df_from_list_of_dicts(self.gbjson['gbXML']['Construction'],li_of_keys=li_of_keys)
        cnstrn['U-value_WPerSquareMeterK']=[extract_uval(cnstrn,n) for n in range(0,len(cnstrn))]
        cnstrn['LayerId']=[layer_id(cnstrn,n) for n in range(0,len(cnstrn))]
        model=fnm_from_fpth(self.FPTH, drop_extension=False).split('.')[0]
        cnstrn['model']=model
        try:
            cnstrn=cnstrn.append(self.glz).reset_index(drop=True)
        except:
            pass
            #print('glazing not extracted')
        cnstrn = df_tonumeric(cnstrn)
        return cnstrn
    
    @property
    def glz(self):
        '''
        Args:
            FPTH (str): fpth of gbxml file
            display_gbmxl (bool): show json structure in browser
        Returns:
            cnstrn (pd.DataFrame): dataframe of constructions in the gbxml model
        '''
        try:
            glz = self.gbjson['gbXML']['WindowType'][0]
        except:
            glz = self.gbjson['gbXML']['WindowType']
        li_of_keys=list(glz)
        glz=df_from_list_of_dicts(self.gbjson['gbXML']['WindowType'],li_of_keys=li_of_keys)
        glz['U-value_WPerSquareMeterK']=[extract_uval(glz,n) for n in range(0,len(glz))]
        model=fnm_from_fpth(self.FPTH, drop_extension=False).split('.')[0]
        glz['model']=model
        glz = df_tonumeric(glz)
        return glz

class GbxmlReport(GbxmlParser):
    def __init__(self, FPTH, spcs_fig_size_x=16, spcs_fig_size_y=10):
        self.spcs_fig_size_x = spcs_fig_size_x
        self.spcs_fig_size_y = spcs_fig_size_y
        super(GbxmlReport, self).__init__(FPTH)

    @property
    def fabric_summ(self):
        cols = ['Name','U-value_WPerSquareMeterK']
        f_summ = self.cnstrn.append(self.glz).set_index('@id')[cols].dropna()
        return f_summ

    @property
    def show_fabric_summ(self):
        display(Markdown(self.fabric_summ.to_markdown()))

    @property
    def spcs_treemap(self):
        create_groupby_squarify(self.spcs, 'Area', 'id',fig_size_x=self.spcs_fig_size_x, fig_size_y= self.spcs_fig_size_y)

if __name__ == '__main__':
    if __debug__ ==True:
        from mf_modules.file_operations import fnm_from_fpth
        from mf_modules.datamine_functions import recursive_glob
        from mf_modules.vis import create_groupby_squarify
        from mf_modules.excel_in import ExcelIn
        #from mf_modules.gbxml import *
        gbxml_des='''
        gbXML is the standard opensource file format for storing/transporting Building Physics data. 
        gbXML follows the widely used xml datastructure (used alot in web-design and also used for ifc-xml). 
        It has been recently bought by Autodesk. Revit, IES, EnergyPlus/OpenStudio and other softwares all export to gbXML. 
        This notebook presents some simple functions for operating on gbXML data.
        '''
        fpth_gbxml = r'J:\J6701\Calcs\EnergyModelling\03_gbXML\NQ06\NQ06.xml'
        Gbxml = GbxmlReport(fpth_gbxml);
        # help(Gbxml)
        Gbxml.show_fabric_summ

        #FPTH=r'J:\J4834\ProjectFolder\Calcs\IES\model_runs.xlsm'
        #xl=ExcelIn(FPTH)
        #fpths=recursive_glob(rootdir=xl.setup['06a_Outputs_ModelData'],pattern='*.xml', recursive=True)
        #spcs=GbxmlParser(fpths[0], display_gbmxl=True).spcs
        #cnstrn=pd.DataFrame()
        #for fpth in fpths:
        #    cnstrn=cnstrn.append(GbxmlParser(fpth, display_gbmxl=False).cnstrn,sort =True)
