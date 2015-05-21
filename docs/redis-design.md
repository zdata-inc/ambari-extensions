@startuml
package redis {
    class Redis1
    class Redis2
    class Redis3
}

package webserver {
    class WebServer1
    class WebServer2
    class WebServer3
}

Redis1 <|-- Redis2
Redis2 <|-- Redis3
Redis3 <|-- Redis1

WebServer1 <|-- WebServer2
WebServer2 <|-- WebServer3
WebServer3 <|-- WebServer1

WebServer1 <|-- Redis1
WebServer2 <|-- Redis2
WebServer3 <|-- Redis3

WebServer1 --|> Redis1
WebServer2 --|> Redis1
WebServer3 --|> Redis1
@enduml
