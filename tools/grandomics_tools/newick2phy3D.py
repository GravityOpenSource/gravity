#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import gc 
import argparse
import time
import pandas as pd
from Bio import Phylo
from Bio.Phylo import PhyloXML
from Bio.Phylo.PhyloXML import Phylogeny
from Bio.Phylo import PhyloXMLIO
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    

def GetArgs():
    parser = argparse.ArgumentParser(description='convert Newick format to extended phyloXML')
    parser.add_argument('-n','--newick',dest='nhx',help='Newick format file')
    parser.add_argument('-p','--phyxml3D',dest='phy3d',\
    help='extended phyloXML format file for phy3D')
    parser.add_argument('-s','--snvtable',dest='snvtable',help='SNV table')
    parser.add_argument('-f','--reference',dest='ref',default='reference',help='Select the reference sequence name')
    parser.add_argument('-r','--rm', action='store_true',default=False,help='Delete intermediate file')
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit()
    return parser.parse_args()


def Nhx2xml(nhx):
    tree = Phylo.read(nhx, "newick")
    phx= Phylogeny.from_tree(tree)
    phx.rooted = True
    terminals_clades=phx.get_terminals()
    n=1
    clade_dict={}
    for clade in terminals_clades:
        key=clade.name
        clade.node_id=PhyloXML.Id(str(n))
        clade_dict[key]=clade
        n+=1
    dt = time.strftime('temp-%Y-%m-%d-%H-%M-%S.xml',time.localtime( time.time()))
    Phylo.write(phx, dt, 'phyloxml')
    return clade_dict ,dt


def CreateNode(tag,content,property_map={}):
    element = ET.Element(tag, property_map)
    element.text = content
    element.tail='\n\t'
    return element


def AddChildNode(parent_node,tag='graphs',property_map={},content='\n\t'):
    element = CreateNode(tag,content,property_map)
    return parent_node.append(element)


def BuiltSub(parent_node,child_tag,property_map={},content='\n\t'):
    child_node=ET.SubElement(parent_node,child_tag)
    if property_map:
        child_node.attrib=property_map
    if content:
        child_node.text=content
    child_node.tail='\n\t'
    return child_node
        

def BuildHeat(cmap='Reds',valid_num=0,name='SNV'):
    template='''
    <graph type="heatmap">
      <name>{2}</name>
      <legend show="1">
        <gradient>
          <name>{0}</name>
          <classes>{1}</classes>
        </gradient>
      </legend>
      <data>
       </data>      
    </graph> 
    '''.format(cmap,valid_num,name)
    element= ET.fromstring(template)
    return element


def FillHeatfield(heat_root,valid_table,titel='Position'):
        valid_pos_list=list(valid_table['Position'])
        legend_node=heat_root.find('.//legend')
        for pos in valid_pos_list:
            field_node=BuiltSub(legend_node,'field')
            name_node=BuiltSub(field_node,'name',content=str(pos))

 
def FillHeatdata(heat_root,sample_name,valid_table,clade_dict,fre_name='Reference'):
    clade= clade_dict[sample_name]
    Id=str(clade.node_id)
    try:
        value_list=list(valid_table[fre_name]==valid_table[sample_name])
    except:
        try:
            value_list=list(valid_table['Reference']==valid_table[sample_name])
        except:
            value_list=list(valid_table['Reference']==valid_table['Reference'])
    if not value_list:
        return 0   
    data_node=heat_root.find('.//data')
    values_node=BuiltSub(data_node,'values',{'for':Id})
    for value in value_list:
        if value:
            content_text='0'
            value_node=BuiltSub(values_node,'value',content=content_text)
        else:
            content_text='1'
            value_node=BuiltSub(values_node,'value',content=content_text)


def RunHeat(graphs_node,valid_table,clade_dict,ref):
    step_num=9
    B=0
    for subvalid_table in [valid_table[i:i + step_num] for i in range(0, len(valid_table), step_num)]:
        graph_name='SNV-bin-{0}'.format(B)
        B+=1
        #heat_root=BuildHeat('RdYlGn',step_num,graph_name)
        heat_root=BuildHeat('Reds',step_num,graph_name)
        FillHeatfield(heat_root,subvalid_table,titel='Position')
        for sample_name in clade_dict:
            FillHeatdata(heat_root,sample_name,subvalid_table,clade_dict,fre_name=ref)
        graphs_node.append(heat_root)
    

def BuildPie(pie1_color='0xFF0000',pie2_color='0x00FF00'):
    template='''
    <graph type="pie">
      <name>SNV ratio pie</name>
      <legend show="1">
        <field>
          <name>mutation site num</name>
          <color>{0}</color>
        </field>
        <field>
          <name>normal site num</name>
          <color>{1}</color>
        </field>
      </legend>
      <data>
      </data>
    </graph> 
    '''.format(pie1_color,pie2_color)
    element= ET.fromstring(template)
    return element
    
def FillPiedata(pie_root,sample_name,valid_table,clade_dict,fre_name='Reference'):
    clade= clade_dict[sample_name]
    Id=str(clade.node_id)
    try:
        value_list=list(valid_table[fre_name]==valid_table[sample_name])
    except:
        try:
            value_list=list(valid_table['Reference']==valid_table[sample_name])
        except:
            value_list=list(valid_table['Reference']==valid_table['Reference'])
    if not value_list:
        return 0
    data_node=pie_root.find('.//data')
    values_node=BuiltSub(data_node,'values',{'for':Id})
    normal_site_num=sum(value_list)
    mutation_site_num=len(value_list)-sum(value_list)
    value_node=BuiltSub(values_node,'value',content=str(mutation_site_num))
    value_node=BuiltSub(values_node,'value',content=str(normal_site_num))


def RunPie(graphs_node,valid_table,clade_dict,ref):
    pie_root=BuildPie(pie1_color='0xFFBBFF',pie2_color='0xAEEEEE')
    for sample_name in clade_dict:
        FillPiedata(pie_root,sample_name,valid_table,clade_dict,fre_name=ref)
    graphs_node.append(pie_root)


def BuildBar(bar_color='0xFFFF00'):
    template='''
    <graph type="multibar">
      <name>SNV Bar</name>
      <legend show="1">
        <field>
          <name>mutation site num</name>
          <color>{0}</color>
        </field>
      </legend>
      <data>
      </data>
    </graph>
    '''.format(bar_color)
    element= ET.fromstring(template)
    return element


def FillBardata(bar_root,sample_name,valid_table,clade_dict,fre_name='Reference'):
    clade= clade_dict[sample_name]
    Id=str(clade.node_id)
    try:
        value_list=list(valid_table[fre_name]==valid_table[sample_name])
    except:
        try:
            value_list=list(valid_table['Reference']==valid_table[sample_name])
        except:
            value_list=list(valid_table['Reference']==valid_table['Reference'])
    if not value_list:
        return 0
    data_node=bar_root.find('.//data')
    values_node=BuiltSub(data_node,'values',{'for':Id})
    normal_site_num=sum(value_list)
    mutation_site_num=len(value_list)-sum(value_list)
    value_node=BuiltSub(values_node,'value',content=str(mutation_site_num))
    

def RunBar(graphs_node,valid_table,clade_dict,ref):
    bar_root=BuildBar(bar_color='0xFFFF00')
    for sample_name in clade_dict:
        FillBardata(bar_root,sample_name,valid_table,clade_dict,fre_name=ref)
    graphs_node.append(bar_root)
    

def ResoverSnvTable(snvtable):
    df=pd.read_csv(snvtable,sep='\t')
    data=df[df.Status=='valid']
    return data


def WriteXML(root_node,phy3d):
    ET.register_namespace('',"http://www.phyloxml.org")
    tree = ET.ElementTree(root_node)
    tree.write(phy3d, encoding="utf-8", xml_declaration=True)


def Run():
    opts=GetArgs()
    nhx=opts.nhx
    phy3d=opts.phy3d
    snvtable=opts.snvtable
    ref=opts.ref  
    clade_dict ,temp_phx = Nhx2xml(nhx)
    tree_txt=open(temp_phx).read().replace('node_id','id')
    if opts.rm:
        if os.path.exists(temp_phx):
            os.remove(temp_phx)   
    root_node=ET.fromstring(tree_txt)
    del tree_txt
    gc.collect()
    valid_table = ResoverSnvTable(snvtable)
    graphs_node=BuiltSub(root_node,'graphs')
    RunBar(graphs_node,valid_table,clade_dict,ref)
    RunPie(graphs_node,valid_table,clade_dict,ref)
    RunHeat(graphs_node,valid_table,clade_dict,ref)
    WriteXML(root_node,phy3d)


if __name__ == "__main__":
    Run()
