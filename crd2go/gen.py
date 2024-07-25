import os
import json
import yaml
import click

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .templates import *

header="""
package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// +genclient
// +genclient:noStatus
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object


"""

def process(crdPath:str, outputPath:str):
    if not os.path.exists(crdPath):
        click.echo(f'CRD path {crdPath} does not exist')
        raise Exception(f'CRD path {crdPath} does not exist')
        

    # create output folder, mainly needed for docker.
    '''
    if not os.path.exists(outputPath):
        click.echo(f'Output folder {outputPath} does not exist. Creating....')
        try:
            os.makedirs(outputPath)
        except Exception as e:
            pass
    '''

    click.echo('Reading ' + crdPath)

    with open(crdPath) as data_file:
        if crdPath.endswith('.json'):
            data = json.load(data_file)
        else:
            data = yaml.load(data_file, Loader=Loader)

    spec = data['spec']
    crd_name = spec['names']['kind']
    versions = spec['versions']

    if len(versions) > 1:
        click.echo("We do not support multiple versions yet")
        return
    
    version = versions[0]
    schema = version['schema']['openAPIV3Schema']

    if schema['type'] != 'object':
        click.echo(f'Dont support non-object')
        return
    
    properties = schema['properties']
    spec = properties['spec']

    if spec['type'] != 'object':
        click.echo(f'Dont support non-object')
        return
    
    document = []
    structures = []

    spec_properties = spec['properties']

    process_spec(
        crd_name=crd_name,
        postfix="Spec",
        spec_properties=spec_properties,
        document=document,
        structures=structures,
        is_struct=False
    )

    status_document = []
    status_structures = []
    process_spec(
        crd_name=crd_name,
        postfix="Status",
        spec_properties=properties['status']['properties'],
        document=status_document,
        structures=status_structures,
        is_struct=False
    )

    output_txt = []
    output_txt.append(header)
    output_txt.append('')
    output_txt.extend(structures)
    output_txt.append('')
    output_txt.extend(status_structures)
    output_txt.append('')

    output_txt.extend(document)
    output_txt.append('')
    output_txt.extend(status_document)
    output_txt.append('')

    '''
    // EventHubList is a list of EventHub resources
    type EventHubList struct {
        metav1.TypeMeta `json:",inline"`
        metav1.ListMeta `json:"metadata"`

        Items []EventHub `json:"items"`
    }

    // EventHubResource is the spec for a single resource/component comprising a eventhub (where type is kafka-topic, hive-table, etc)
    type EventHubResource struct {
        Type  string `json:"type"`
        Name  string `json:"name"`
        K8sId string `json:"k8s_id"`
    }    
    '''

    output_txt.append(render_object(crdName=titleCase(crd_name)))


    output_txt.append(render_list_resource(crdName=titleCase(crd_name)))

    with open(outputPath, 'w') as f:
        f.write('\n'.join(output_txt))
    

def process_spec(
    crd_name:str,
    postfix:str,
    spec_properties:dict, 
    document:list,
    structures:list,
    is_struct:bool) -> str:

    _document = document if not is_struct else structures

    _document.append(f'type {crd_name}{postfix} struct ' + '{')
    for n,t in spec_properties.items():
        nullable = 'nullable' in t and t['nullable']

        if t['type'] == 'string':
            if 'enum' in t:
                _document.append(f'\t{titleCase(n)}  {titleCase(n)} `json:"{omitempty(n,nullable=nullable)}"`')
                process_enum(n,t,structures)
            else:
                _document.append(f'\t{titleCase(n)}  string `json:"{omitempty(n,nullable=nullable)}"`')
        elif t['type'] == 'boolean':
            _document.append(f'\t{titleCase(n)}  bool `json:"{omitempty(n,nullable=nullable)}"`')
        elif t['type'] == 'array':
            '''
            targets:
                type: array
                items:
                    type: object
                    properties:
                        accountIdentifier:
                            type: string
                            enum: [ streamz, zillow, datalake ]
                        destinationType:
                            type: string
                            enum: [ kafka, kinesis, firehose ]
                        destinationName:
                            type: string  
            '''
            process_array(n,n,t,document,structures)
        else:
            click.echo(f'Unprocessed: {n} {json.dumps(t, indent=4)}')

    _document.append('}')

def process_array(
    crd_name:str,
    field_name:str, 
    field_type:dict, 
    document:list, 
    structures:list):
    '''
    INPUT

    targets:
        type: array
        items:
            type: object
            properties:
                accountIdentifier:
                    type: string
                    enum: [ streamz, zillow, datalake ]
                destinationType:
                    type: string
                    enum: [ kafka, kinesis, firehose ]
                destinationName:
                    type: string  
    '''  
    array_type = field_type['items']['type']
    if array_type == 'object':
        process_spec(
            crd_name=titleCase(crd_name),
            postfix="",
            spec_properties=field_type['items']['properties'],
            document=document,
            structures=structures,
            is_struct=True
        )
        document.append(f'\t{titleCase(field_name)}  []{titleCase(field_name)} `json:"{field_name}"`')
    else:
        document.append(f'\t{titleCase(field_name)}  []{array_type} `json:"{field_name}"`')

def process_enum(field_name:str, field_type:dict, structures:list):
    '''
    INPUT

    apiType:
        type: string
        enum: [ datalake, webhook, clickstream ]

    '''

    '''
    OUTPUT

    type ApiType string

    const (
        DATALAKE                ApiType = "datalake"
        WEBHOOK            ApiType = "webhook"
        CLICKSTREAM    ApiType = "clickstream"
    )    
    '''

    structures.append(f'type {titleCase(field_name)} string')
    structures.append('')
    structures.append('const(')
    for e in field_type['enum']:
        structures.append(f'\t{e.upper()} {titleCase(field_name)} = \"{e}\"')
    structures.append(')')
    structures.append('')

def omitempty(value:str, nullable:bool) -> str:
    return f'{value},omitempty' if nullable else value

def capitalCase(value:str) -> str:
    return value.upper()

def titleCase(value:str) -> str:
    return value[0].upper() + value[1:]

def render_object(crdName:str) -> str:

    return OBJECT_TEMPLATE.replace('{crdName}', crdName)

def render_list_resource(crdName:str) -> str:
    return LIST_RESOURCE_TEMPLATE.replace('{crdName}', crdName)

