
package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// +genclient
// +genclient:noStatus
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object




type ApiType string

const(
	BACKEND ApiType = "backend"
	FRONTEND ApiType = "frontend"
)

type Targets struct {
	DestinationType  DestinationType `json:"destinationType"`
type DestinationType string

const(
	KAFKA DestinationType = "kafka"
	KINESIS DestinationType = "kinesis"
	FIREHOSE DestinationType = "firehose"
)

	DestinationName  string `json:"destinationName"`
}


type ExampleSpec struct {
	Name  string `json:"name"`
	SpecId  string `json:"specId,omitempty"`
	ApiType  ApiType `json:"apiType"`
	Targets  []Targets `json:"targets"`
}

type ExampleStatus struct {
	Text  string `json:"text"`
}


// Example is a specification for an Example resource
type Example struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata"`

    Spec   ExampleSpec   `json:"spec"`
    Status ExampleStatus `json:"status,omitempty"`
    SpecId string         `json:"specId,omitempty"`
}


// ExampleList is a list of Example resources
type ExampleList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata"`

    Items []Example `json:"items"`
}

// ExampleResource is the spec for a single resource/component comprising a Example (where type is kafka-topic, hive-table, etc)
type ExampleResource struct {
    Type  string `json:"type"`
    Name  string `json:"name"`
    K8sId string `json:"k8s_id"`
}    
