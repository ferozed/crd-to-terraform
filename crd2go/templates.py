OBJECT_TEMPLATE="""
// {crdName} is a specification for an {crdName} resource
type {crdName} struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata"`

    Spec   {crdName}Spec   `json:"spec"`
    Status {crdName}Status `json:"status,omitempty"`
    SpecId string         `json:"specId,omitempty"`
}
"""

LIST_RESOURCE_TEMPLATE="""
// {crdName}List is a list of {crdName} resources
type {crdName}List struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata"`

    Items []{crdName} `json:"items"`
}

// {crdName}Resource is the spec for a single resource/component comprising a {crdName} (where type is kafka-topic, hive-table, etc)
type {crdName}Resource struct {
    Type  string `json:"type"`
    Name  string `json:"name"`
    K8sId string `json:"k8s_id"`
}    
"""